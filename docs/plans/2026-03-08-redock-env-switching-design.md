# Redock Environment Switching - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement `josi redock up {env}` with cloud/local modes (matching lightspun-cli), remove Redis and Adminer from the stack.

**Architecture:** Docker Compose overlay files per environment with profile-based service selection. Cloud mode fetches DB credentials from GCP Secret Manager and connects via Cloud SQL Auth Proxy. Local mode uses local Postgres with hardcoded credentials. CLI orchestrates compose file selection, secret fetching, and container lifecycle.

**Tech Stack:** TypeScript (Commander.js CLI), Docker Compose profiles + overlays, GCP Secret Manager (gcloud CLI), Cloud SQL Auth Proxy

---

## Design Reference

See the approved design section below for full context on modes, file structure, and GCP details.

## Goal (Design)

Implement `josi redock up {env}` with cloud/local modes, matching the lightspun-cli pattern. Remove Redis and Adminer from the stack.

## Usage

```bash
josi redock up dev          # Cloud mode: API -> Cloud SQL dev via proxy
josi redock up prod         # Cloud mode: API -> Cloud SQL prod via proxy
josi redock up dev --local  # Local mode: API -> local Postgres (current behavior minus Redis/Adminer)
```

## Modes

### Cloud Mode (default)

- Fetches `DB_USER` / `DB_PASSWORD` from GCP Secret Manager (`josiam-db-user-{env}`, `josiam-db-password-{env}`)
- Starts Cloud SQL Auth Proxy container (ADC-based, mounting `~/.config/gcloud/`)
  - Falls back to ADC since no SA key secrets exist (`iam.disableServiceAccountKeyCreation` org policy)
  - If `josiam-sa-credentials-{env}` is ever added, CLI will prefer it over ADC
- API container connects to proxy at `cloudsql-proxy:5432`
- No local Postgres

### Local Mode (`--local`)

- Spins up local Postgres (pgvector/pg16) with hardcoded credentials (`josi:josi`)
- No secret fetching, no Cloud SQL Proxy
- Runs migrations automatically (`AUTO_DB_MIGRATION=True`)
- Equivalent to current behavior minus Redis/Adminer

## Docker Compose File Structure

### Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Base: all service definitions with profiles |
| `docker-compose.dev.yml` | Cloud dev overrides (connection string, env vars) |
| `docker-compose.prod.yml` | Cloud prod overrides |
| `docker-compose.local.yml` | Local mode overrides (local Postgres config) |
| `docker-compose.test.yml` | Test runner (unchanged) |

### Compose File Selection

| Mode | Files | Profiles |
|------|-------|----------|
| Cloud dev | `docker-compose.yml` + `docker-compose.dev.yml` | `--profile cloud` |
| Cloud prod | `docker-compose.yml` + `docker-compose.prod.yml` | `--profile cloud` |
| Local | `docker-compose.yml` + `docker-compose.local.yml` | `--profile local` |

### Service Profile Assignment

| Service | Profile | Runs in Cloud | Runs in Local |
|---------|---------|---------------|---------------|
| `api` | _(none)_ | Yes | Yes |
| `web` | _(none)_ | Yes | Yes |
| `cloudsql-proxy` | `cloud` | Yes | No |
| `db` | `local` | No | Yes |
| `db-test` | `test` | No | No |

### `docker-compose.yml` (base)

```yaml
services:
  api:
    container_name: josi-api
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "1954:8000"
    volumes:
      - ./src/:/app/src
      - ./alembic.ini:/app/alembic.ini
    env_file: .env.local
    environment:
      AUTO_DB_MIGRATION: "True"
      EPHEMERIS_PATH: /usr/share/swisseph
    command: poetry run uvicorn josi.main:app --host 0.0.0.0 --port 8000 --reload

  cloudsql-proxy:
    container_name: josi-cloudsql-proxy
    image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.15.2
    profiles: ['cloud']
    ports:
      - "15432:5432"

  db:
    container_name: josi-db
    image: pgvector/pgvector:pg16
    profiles: ['local']

  db-test:
    container_name: josi-db-test
    image: pgvector/pgvector:pg16
    profiles: ['test']
    # ... (unchanged)

  web:
    container_name: josi-web
    build:
      context: ./web
      dockerfile: Dockerfile.dev
    ports:
      - "1989:4000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:1954
      - API_URL=http://api:8000
    command: npm run dev
```

### `docker-compose.dev.yml`

```yaml
services:
  api:
    environment:
      DATABASE_URL: "postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@cloudsql-proxy:5432/josi"
      ENVIRONMENT: development
    depends_on:
      cloudsql-proxy:
        condition: service_started

  cloudsql-proxy:
    command: ["--address", "0.0.0.0", "--port", "5432", "josiam:us-central1:josiam-dev"]
    volumes:
      - ${GOOGLE_ADC_PATH:-~/.config/gcloud}:/root/.config/gcloud:ro
```

### `docker-compose.prod.yml`

```yaml
services:
  api:
    environment:
      DATABASE_URL: "postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@cloudsql-proxy:5432/josi"
      ENVIRONMENT: production
    depends_on:
      cloudsql-proxy:
        condition: service_started

  cloudsql-proxy:
    command: ["--address", "0.0.0.0", "--port", "5432", "josiam:us-central1:josiam-prod"]
    volumes:
      - ${GOOGLE_ADC_PATH:-~/.config/gcloud}:/root/.config/gcloud:ro
```

### `docker-compose.local.yml`

```yaml
services:
  api:
    environment:
      DATABASE_URL: "postgresql+asyncpg://josi:josi@db:5432/josi"
      ENVIRONMENT: development
    depends_on:
      db:
        condition: service_healthy

  db:
    environment:
      POSTGRES_USER: josi
      POSTGRES_PASSWORD: josi
      POSTGRES_DB: josi
    ports:
      - "1961:5432"
    volumes:
      - josi-db:/var/lib/postgresql/data
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U josi -d josi"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  josi-db:
```

## CLI Changes

### New: `cli/src/lib/secrets.ts`

```typescript
import { execFileSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as logger from './logger';

const GCP_PROJECT = 'josiam';

export function fetchSecret(secretName: string): string {
  const result = execFileSync('gcloud', [
    'secrets', 'versions', 'access', 'latest',
    `--secret=${secretName}`,
    `--project=${GCP_PROJECT}`,
  ], { encoding: 'utf-8', timeout: 15_000 });
  return result.trim();
}

export function fetchDbCredentials(env: string): { DB_USER: string; DB_PASSWORD: string } {
  logger.info(`Fetching DB credentials for ${env}...`);
  const DB_USER = fetchSecret(`josiam-db-user-${env}`);
  const DB_PASSWORD = fetchSecret(`josiam-db-password-${env}`);
  return { DB_USER, DB_PASSWORD };
}

export function trySaKey(env: string): string | null {
  try {
    const key = fetchSecret(`josiam-sa-credentials-${env}`);
    const keyPath = path.join(process.cwd(), '.sa-key.json');
    fs.writeFileSync(keyPath, key + '\n', { mode: 0o600 });
    logger.success('Using SA key from Secret Manager');
    return keyPath;
  } catch {
    logger.info('No SA key found, falling back to ADC');
    return null;
  }
}
```

### Modified: `cli/src/commands/redock/up.ts`

```
josi redock up <env> [--local] [--no-logs] [--no-web]

Arguments:
  env         Environment: dev | prod

Options:
  --local     Use local database instead of Cloud SQL
  --no-logs   Don't follow logs after starting
  --no-web    Don't start the web service
```

Flow:
1. Validate env argument (dev | prod)
2. Validate required docker-compose files exist
3. If cloud mode: fetch DB credentials from Secret Manager
4. If cloud mode: try SA key, fall back to ADC
5. Kill and remove existing containers
6. Build compose file list and profile args
7. `docker compose [...files] [...profiles] up -d --build` with DB_USER/DB_PASSWORD as env vars
8. Follow logs (unless `--no-logs`)

### New: `cli/src/lib/compose.ts`

```typescript
export type Env = 'dev' | 'prod';
export type Mode = 'cloud' | 'local';

export interface ComposeConfig {
  files: string[];
  profiles: string[];
}

export function buildComposeConfig(env: Env, mode: Mode): ComposeConfig {
  const files = ['docker-compose.yml'];
  const profiles: string[] = [];

  if (mode === 'cloud') {
    files.push(`docker-compose.${env}.yml`);
    profiles.push('cloud');
  } else {
    files.push('docker-compose.local.yml');
    profiles.push('local');
  }

  return { files, profiles };
}
```

### Environment Config

```typescript
export const ENV_CONFIGS: Record<Env, EnvConfig> = {
  dev:  { project: 'josiam', instance: 'josiam:us-central1:josiam-dev' },
  prod: { project: 'josiam', instance: 'josiam:us-central1:josiam-prod' },
};
```

## Removals

### Redis (everywhere)
- `docker-compose.yml`: remove `redis` service
- `docker-compose.yml`: remove `REDIS_URL` from api environment
- `docker-compose.yml`: remove api `depends_on: redis`
- `docker-compose.test.yml`: remove `test-redis` service if present
- `.env.example`: remove `REDIS_URL`

### Adminer
- `docker-compose.yml`: remove `adminer` service
- `cli/src/commands/redock/adminer.ts`: delete file
- `cli/src/commands/redock/index.ts`: remove adminer registration

## GCP Details

| | Dev | Prod |
|---|---|---|
| Project | josiam | josiam |
| Instance | josiam:us-central1:josiam-dev | josiam:us-central1:josiam-prod |
| DB Name | josi | josi |
| DB User Secret | josiam-db-user-dev | josiam-db-user-prod |
| DB Password Secret | josiam-db-password-dev | josiam-db-password-prod |

## Port Mappings

| Service | Host:Container |
|---------|---------------|
| API | 1954:8000 |
| Web | 1989:4000 |
| Cloud SQL Proxy | 15432:5432 |
| Local Postgres | 1961:5432 |
| Test DB | 1962:5432 |

---

## Implementation Tasks

### Task 1: Remove Redis and Adminer from docker-compose.yml

**Files:**
- Modify: `docker-compose.yml`
- Delete: `cli/src/commands/redock/adminer.ts`
- Modify: `cli/src/commands/redock/index.ts`
- Modify: `cli/src/types.ts`
- Modify: `.env.example`

**Step 1: Edit docker-compose.yml — remove redis service, adminer service, redis volume, redis_data volume, REDIS_URL from api, and redis dependency from api**

Remove the entire `redis:` service block (lines 49-66), the entire `adminer:` service block (lines 111-121), `REDIS_URL` from api environment, `redis` from api depends_on, and `redis_data` from volumes.

The resulting `docker-compose.yml` should be:

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: josi-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: josi
      POSTGRES_PASSWORD: josi
      POSTGRES_DB: josi
    ports:
      - "1961:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U josi"]
      interval: 5s
      timeout: 5s
      retries: 5
    command: >
      postgres
      -c shared_buffers=256MB
      -c max_connections=200
      -c log_statement=all
      -c log_duration=on

  db-test:
    image: pgvector/pgvector:pg16
    container_name: josi-db-test
    environment:
      POSTGRES_USER: josi
      POSTGRES_PASSWORD: josi
      POSTGRES_DB: josi_test
    ports:
      - "1962:5432"
    tmpfs:
      - /var/lib/postgresql/data
    volumes:
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U josi"]
      interval: 5s
      timeout: 3s
      retries: 3
    profiles:
      - test

  api:
    build: .
    container_name: josi-api
    restart: unless-stopped
    ports:
      - "1954:8000"
    env_file:
      - .env.local
    environment:
      DATABASE_URL: postgresql://josi:josi@db:5432/josi
      AUTO_DB_MIGRATION: "True"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./alembic.ini:/app/alembic.ini
    command: poetry run uvicorn josi.main:app --host 0.0.0.0 --port 8000 --reload

  web:
    build:
      context: ./web
      dockerfile: Dockerfile.dev
    container_name: josi-web
    restart: unless-stopped
    ports:
      - "1989:4000"
    env_file:
      - .env.local
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:1954
      API_URL: http://api:8000
    depends_on:
      - api
    volumes:
      - ./web:/app
      - web_node_modules:/app/node_modules
      - /app/.next
    command: npm run dev

volumes:
  postgres_data:
  web_node_modules:
```

**Step 2: Remove REDIS_URL from .env.example**

Delete the lines:
```
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

**Step 3: Remove redis and adminer from cli/src/types.ts**

Remove the `redis` and `adminer` entries from `SERVICES` and `adminer` from `URLS`.

After edit, `SERVICES` should be:
```typescript
export const SERVICES: Record<string, ServiceConfig> = {
  api: { name: 'Josi API', port: 1954, url: 'http://localhost:1954' },
  db: { name: 'PostgreSQL', port: 1961, url: 'postgresql://josi:josi@localhost:1961/josi' },
  'db-test': { name: 'Test DB', port: 1962, url: 'postgresql://josi:josi@localhost:1962/josi_test' },
  web: { name: 'Josi Web', port: 1989, url: 'http://localhost:1989' },
};
```

And `URLS` should be:
```typescript
export const URLS = {
  docs: 'http://localhost:1954/docs',
  redoc: 'http://localhost:1954/redoc',
  graphql: 'http://localhost:1954/graphql',
  health: 'http://localhost:1954/api/v1/health',
  web: 'http://localhost:1989',
};
```

**Step 4: Delete cli/src/commands/redock/adminer.ts**

```bash
rm cli/src/commands/redock/adminer.ts
```

**Step 5: Remove adminer registration from cli/src/commands/redock/index.ts**

Remove the import line and the `registerAdminer(redock)` call. After edit:

```typescript
import type { Command } from 'commander';
import { register as registerUp } from './up.js';
import { register as registerStatus } from './status.js';
import { register as registerLogs } from './logs.js';
import { register as registerClean } from './clean.js';
import { register as registerCheck } from './check.js';

export function register(program: Command): void {
  const redock = program
    .command('redock')
    .description('Docker Compose service management');

  registerUp(redock);
  registerStatus(redock);
  registerLogs(redock);
  registerClean(redock);
  registerCheck(redock);
}
```

**Step 6: Remove test-redis from docker-compose.test.yml**

Remove the `test-redis` service block and the `REDIS_URL` env var from `test-runner`, and remove `test-redis` from `test-runner` depends_on.

**Step 7: Verify — build CLI and check docker-compose parses**

```bash
cd cli && npm run build
cd /Users/govind/Developer/josi/josi-svc && docker compose config --services
```

Expected: `db`, `api`, `web` (no redis, no adminer). CLI compiles without errors.

**Step 8: Commit**

```bash
git add -A && git commit -m "chore: remove Redis and Adminer from stack"
```

---

### Task 2: Restructure docker-compose.yml with profiles

**Files:**
- Modify: `docker-compose.yml` — add profiles to `db`, add `cloudsql-proxy` service
- Create: `docker-compose.dev.yml`
- Create: `docker-compose.prod.yml`
- Create: `docker-compose.local.yml`

**Step 1: Modify docker-compose.yml — add profiles and cloudsql-proxy**

The base file defines all services. `db` gets `profiles: [local]`, `cloudsql-proxy` gets `profiles: [cloud]`. The `api` service loses its hardcoded `DATABASE_URL` and `depends_on` (these move to overlay files). Write the full file:

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: josi-db
    restart: unless-stopped
    profiles:
      - local
    command: >
      postgres
      -c shared_buffers=256MB
      -c max_connections=200
      -c log_statement=all
      -c log_duration=on

  db-test:
    image: pgvector/pgvector:pg16
    container_name: josi-db-test
    environment:
      POSTGRES_USER: josi
      POSTGRES_PASSWORD: josi
      POSTGRES_DB: josi_test
    ports:
      - "1962:5432"
    tmpfs:
      - /var/lib/postgresql/data
    volumes:
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U josi"]
      interval: 5s
      timeout: 3s
      retries: 3
    profiles:
      - test

  cloudsql-proxy:
    container_name: josi-cloudsql-proxy
    image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.15.2
    restart: unless-stopped
    profiles:
      - cloud
    ports:
      - "15432:5432"

  api:
    build: .
    container_name: josi-api
    restart: unless-stopped
    ports:
      - "1954:8000"
    env_file:
      - .env.local
    environment:
      AUTO_DB_MIGRATION: "True"
      EPHEMERIS_PATH: /usr/share/swisseph
    volumes:
      - ./src:/app/src
      - ./alembic.ini:/app/alembic.ini
    command: poetry run uvicorn josi.main:app --host 0.0.0.0 --port 8000 --reload

  web:
    build:
      context: ./web
      dockerfile: Dockerfile.dev
    container_name: josi-web
    restart: unless-stopped
    ports:
      - "1989:4000"
    env_file:
      - .env.local
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:1954
      API_URL: http://api:8000
    depends_on:
      - api
    volumes:
      - ./web:/app
      - web_node_modules:/app/node_modules
      - /app/.next
    command: npm run dev

volumes:
  web_node_modules:
```

**Step 2: Create docker-compose.local.yml**

```yaml
services:
  api:
    environment:
      DATABASE_URL: "postgresql+asyncpg://josi:josi@db:5432/josi"
      ENVIRONMENT: development
    depends_on:
      db:
        condition: service_healthy

  db:
    environment:
      POSTGRES_USER: josi
      POSTGRES_PASSWORD: josi
      POSTGRES_DB: josi
    ports:
      - "1961:5432"
    volumes:
      - josi-db:/var/lib/postgresql/data
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U josi -d josi"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  josi-db:
```

**Step 3: Create docker-compose.dev.yml**

```yaml
services:
  api:
    environment:
      DATABASE_URL: "postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@cloudsql-proxy:5432/josi"
      ENVIRONMENT: development
    depends_on:
      cloudsql-proxy:
        condition: service_started

  cloudsql-proxy:
    command: ["--address", "0.0.0.0", "--port", "5432", "josiam:us-central1:josiam-dev"]
    volumes:
      - type: bind
        source: ~/.config/gcloud
        target: /root/.config/gcloud
        read_only: true
```

**Step 4: Create docker-compose.prod.yml**

```yaml
services:
  api:
    environment:
      DATABASE_URL: "postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@cloudsql-proxy:5432/josi"
      ENVIRONMENT: production
    depends_on:
      cloudsql-proxy:
        condition: service_started

  cloudsql-proxy:
    command: ["--address", "0.0.0.0", "--port", "5432", "josiam:us-central1:josiam-prod"]
    volumes:
      - type: bind
        source: ~/.config/gcloud
        target: /root/.config/gcloud
        read_only: true
```

**Step 5: Verify compose files parse correctly**

```bash
# Local mode
docker compose -f docker-compose.yml -f docker-compose.local.yml --profile local config --services
# Expected: api, db, web

# Cloud dev mode (will warn about unset DB_USER/DB_PASSWORD, that's OK)
DB_USER=test DB_PASSWORD=test docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile cloud config --services
# Expected: api, cloudsql-proxy, web
```

**Step 6: Commit**

```bash
git add docker-compose.yml docker-compose.local.yml docker-compose.dev.yml docker-compose.prod.yml
git commit -m "feat: add docker-compose overlay files for cloud/local modes"
```

---

### Task 3: Add types and compose helper to CLI

**Files:**
- Modify: `cli/src/types.ts` — add Env, Mode, ComposeConfig, EnvConfig types
- Create: `cli/src/lib/compose.ts` — compose config builder

**Step 1: Add environment types to cli/src/types.ts**

Append after the existing `Tool` interface:

```typescript
export const VALID_ENVS = ['dev', 'prod'] as const;
export type Env = (typeof VALID_ENVS)[number];

export const VALID_MODES = ['cloud', 'local'] as const;
export type Mode = (typeof VALID_MODES)[number];

export interface UpOptions {
  local?: boolean;
  logs?: boolean;
  web?: boolean;
  build?: boolean;
}

export interface ComposeConfig {
  files: string[];
  profiles: string[];
}

export interface EnvConfig {
  project: string;
  instance: string;
}

export const ENV_CONFIGS: Record<Env, EnvConfig> = {
  dev:  { project: 'josiam', instance: 'josiam:us-central1:josiam-dev' },
  prod: { project: 'josiam', instance: 'josiam:us-central1:josiam-prod' },
};
```

**Step 2: Create cli/src/lib/compose.ts**

```typescript
import type { Env, Mode, ComposeConfig } from '../types.js';

export function buildComposeConfig(env: Env, mode: Mode): ComposeConfig {
  const files = ['docker-compose.yml'];
  const profiles: string[] = [];

  if (mode === 'cloud') {
    files.push(`docker-compose.${env}.yml`);
    profiles.push('cloud');
  } else {
    files.push('docker-compose.local.yml');
    profiles.push('local');
  }

  return { files, profiles };
}

export function composeFileArgs(files: string[]): string[] {
  return files.flatMap((f) => ['-f', f]);
}

export function composeProfileArgs(profiles: string[]): string[] {
  return profiles.flatMap((p) => ['--profile', p]);
}

export function allComposeArgs(): string[] {
  return ['--profile', 'cloud', '--profile', 'local'];
}
```

**Step 3: Verify — build CLI**

```bash
cd cli && npm run build
```

Expected: compiles without errors.

**Step 4: Commit**

```bash
git add cli/src/types.ts cli/src/lib/compose.ts
git commit -m "feat(cli): add environment types and compose config builder"
```

---

### Task 4: Add GCP secrets module to CLI

**Files:**
- Create: `cli/src/lib/secrets.ts`

**Step 1: Create cli/src/lib/secrets.ts**

```typescript
import { execFileSync } from 'node:child_process';
import * as logger from './logger.js';

const GCP_PROJECT = 'josiam';

export function fetchSecret(secretName: string): string {
  const result = execFileSync(
    'gcloud',
    [
      'secrets', 'versions', 'access', 'latest',
      `--secret=${secretName}`,
      `--project=${GCP_PROJECT}`,
    ],
    { encoding: 'utf-8', timeout: 15_000 },
  );
  return result.trim();
}

export interface DbCredentials {
  DB_USER: string;
  DB_PASSWORD: string;
}

export function fetchDbCredentials(env: string): DbCredentials {
  logger.step(`Fetching DB credentials for ${env}...`);
  const DB_USER = fetchSecret(`josiam-db-user-${env}`);
  const DB_PASSWORD = fetchSecret(`josiam-db-password-${env}`);
  logger.success('DB credentials fetched');
  return { DB_USER, DB_PASSWORD };
}
```

**Step 2: Verify — build CLI**

```bash
cd cli && npm run build
```

Expected: compiles without errors.

**Step 3: Commit**

```bash
git add cli/src/lib/secrets.ts
git commit -m "feat(cli): add GCP Secret Manager module"
```

---

### Task 5: Rewrite docker.ts to support async exec and compose args

**Files:**
- Modify: `cli/src/lib/docker.ts`

**Step 1: Rewrite cli/src/lib/docker.ts**

The current implementation uses `spawnSync` everywhere. Rewrite to support both sync (for simple checks) and async (for long-running docker compose commands), and accept compose file/profile args. Follow the lightspun pattern.

```typescript
import { spawnSync, spawn, type SpawnOptions } from 'node:child_process';
import * as logger from './logger.js';

export interface ExecResult {
  code: number;
}

export function exec(
  args: string[],
  opts?: { cwd?: string; silent?: boolean; env?: Record<string, string> },
): Promise<ExecResult> {
  return new Promise((resolve, reject) => {
    const spawnOpts: SpawnOptions = {
      cwd: opts?.cwd,
      stdio: opts?.silent ? ['ignore', 'pipe', 'pipe'] : 'inherit',
      env: opts?.env ? { ...process.env, ...opts.env } : undefined,
    };

    const child = spawn('docker', ['compose', ...args], spawnOpts);

    child.on('error', (err) => {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        reject(new Error('docker not found. Is Docker installed and in your PATH?'));
      } else {
        reject(err);
      }
    });

    child.on('close', (code) => {
      resolve({ code: code ?? 1 });
    });
  });
}

export function containerExec(
  composeArgs: string[],
  container: string,
  command: string[],
  opts?: { cwd?: string },
): Promise<ExecResult> {
  return exec([...composeArgs, 'exec', container, ...command], opts);
}

export function isDockerRunning(): boolean {
  const result = spawnSync('docker', ['info'], { stdio: 'pipe' });
  return result.status === 0;
}
```

**Step 2: Verify — build CLI**

```bash
cd cli && npm run build
```

Expected: build will FAIL because other files (`status.ts`, `logs.ts`, `clean.ts`, `check.ts`, `up.ts`) import the old function signatures. That's expected — we fix those in the next tasks.

**Step 3: Commit (even with broken imports — they'll be fixed next)**

Do NOT commit yet. Move to Task 6 which fixes the consumers.

---

### Task 6: Update all redock subcommands for new docker.ts API

**Files:**
- Modify: `cli/src/commands/redock/status.ts`
- Modify: `cli/src/commands/redock/logs.ts`
- Modify: `cli/src/commands/redock/clean.ts`
- Modify: `cli/src/commands/redock/check.ts`

**Step 1: Rewrite status.ts**

```typescript
import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { exec } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('status')
    .description('Show running container status')
    .action(async () => {
      logger.header('Container Status');
      const root = getProjectRoot();
      await exec(['ps', '--format', 'table'], { cwd: root });
    });
}
```

**Step 2: Rewrite logs.ts**

```typescript
import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { exec } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('logs [service]')
    .description('Follow container logs')
    .option('--no-follow', 'Print logs without following')
    .addHelpText(
      'after',
      `
Examples:
  $ josi redock logs           # Follow all logs
  $ josi redock logs api       # Follow API logs only
  $ josi redock logs db        # Follow database logs
  $ josi redock logs --no-follow`
    )
    .action(async (service: string | undefined, opts: { follow: boolean }) => {
      logger.header('Container Logs');
      const root = getProjectRoot();
      const args = ['logs'];
      if (opts.follow) args.push('-f');
      if (service) args.push(service);
      await exec(args, { cwd: root });
    });
}
```

**Step 3: Rewrite clean.ts**

```typescript
import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { exec } from '../../lib/docker.js';
import { confirmAction } from '../../lib/prompt.js';

export function register(parent: Command): void {
  parent
    .command('clean')
    .description('Stop all containers and optionally remove volumes')
    .option('-v, --volumes', 'Also remove Docker volumes (database data)')
    .option('-y, --yes', 'Skip confirmation')
    .addHelpText(
      'after',
      `
Examples:
  $ josi redock clean          # Stop containers
  $ josi redock clean -v       # Stop and remove volumes (fresh DB)
  $ josi redock clean -v -y    # Skip confirmation`
    )
    .action(async (opts: { volumes?: boolean; yes?: boolean }) => {
      logger.header('Cleaning Up');
      const root = getProjectRoot();

      if (opts.volumes && !opts.yes) {
        const ok = await confirmAction(
          'This will delete all Docker volumes including database data. Continue?'
        );
        if (!ok) {
          logger.info('Cancelled.');
          return;
        }
      }

      logger.step('Stopping containers...');
      const args = ['down'];
      if (opts.volumes) args.push('-v', '--remove-orphans');
      await exec(args, { cwd: root });

      logger.blank();
      logger.success(
        opts.volumes
          ? 'Containers stopped and volumes removed.'
          : 'Containers stopped.'
      );
      logger.blank();
    });
}
```

**Step 4: Update check.ts — replace composeExec import with exec**

Replace the import and the `composeExec` call. Change:
```typescript
import { composeExec } from '../../lib/docker.js';
```
to:
```typescript
import { exec } from '../../lib/docker.js';
```

And change the compose validation section to use async exec. The `check` command action needs to become `async`. Replace the config validation block:

```typescript
// In the action callback, change the compose validation to:
if (existsSync(resolve(root, 'docker-compose.yml'))) {
  const result = await exec(['config', '--services'], {
    cwd: root,
    silent: true,
  });
  if (result.code === 0) {
    logger.pass('docker-compose.yml parses correctly');
  } else {
    logger.fail('docker-compose.yml has errors');
    logger.dim('  Run: docker compose config');
    issues++;
  }
}
```

Note: The `exec` function returns `ExecResult` (just `{ code }`) not a `SpawnSyncReturns<Buffer>`, so the services list output won't be captured. That's fine — the check just validates it parses. Remove the services display line.

**Step 5: Verify — build CLI**

```bash
cd cli && npm run build
```

Expected: compiles without errors.

**Step 6: Commit**

```bash
git add cli/src/lib/docker.ts cli/src/commands/redock/status.ts cli/src/commands/redock/logs.ts cli/src/commands/redock/clean.ts cli/src/commands/redock/check.ts
git commit -m "refactor(cli): migrate docker.ts to async exec, update all consumers"
```

---

### Task 7: Rewrite redock up command with env/mode support

**Files:**
- Modify: `cli/src/commands/redock/up.ts`

**Step 1: Rewrite cli/src/commands/redock/up.ts**

This is the core change. The `up` command now takes a required `<env>` argument, supports `--local`, fetches secrets in cloud mode, and uses compose overlays.

```typescript
import type { Command } from 'commander';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { VALID_ENVS, type Env, type UpOptions } from '../../types.js';
import { buildComposeConfig, composeFileArgs, composeProfileArgs, allComposeArgs } from '../../lib/compose.js';
import { exec, isDockerRunning } from '../../lib/docker.js';
import { fetchDbCredentials } from '../../lib/secrets.js';
import { getProjectRoot } from '../../lib/detect.js';
import * as logger from '../../lib/logger.js';

export function register(parent: Command): void {
  parent
    .command('up <env>')
    .description('Start services with specified environment (dev, prod)')
    .option('--local', 'Use local database instead of Cloud SQL')
    .option('--no-logs', 'Do not follow logs after starting')
    .option('--no-web', 'Do not start the web service')
    .option('--no-build', 'Skip rebuilding images')
    .addHelpText(
      'after',
      `
Environments:
  dev, prod

Examples:
  $ josi redock up dev            # Cloud mode: connect to dev Cloud SQL
  $ josi redock up prod           # Cloud mode: connect to prod Cloud SQL
  $ josi redock up dev --local    # Local mode: local Postgres
  $ josi redock up dev --no-logs  # Start without following logs`
    )
    .action(async (envArg: string, opts: UpOptions) => {
      if (!VALID_ENVS.includes(envArg as Env)) {
        logger.error(`Invalid environment '${envArg}'. Must be one of: ${VALID_ENVS.join(', ')}`);
        process.exit(1);
      }
      const env = envArg as Env;
      const mode = opts.local ? 'local' : 'cloud';

      if (!isDockerRunning()) {
        logger.error('Docker is not running. Start Docker Desktop first.');
        process.exit(1);
      }

      const root = getProjectRoot();

      // Validate required compose files exist
      const config = buildComposeConfig(env, mode);
      for (const file of config.files) {
        if (!existsSync(resolve(root, file))) {
          logger.error(`Missing compose file: ${file}`);
          process.exit(1);
        }
      }

      const fileArgs = composeFileArgs(config.files);
      const profileArgs = composeProfileArgs(config.profiles);

      logger.header(`Josi ${env} / ${mode} mode`);

      // Cloud mode: fetch DB credentials from Secret Manager
      let secretEnv: Record<string, string> | undefined;
      if (mode === 'cloud') {
        try {
          const creds = fetchDbCredentials(env);
          secretEnv = { ...creds };
        } catch (err) {
          logger.error(`Failed to fetch secrets: ${(err as Error).message}`);
          logger.dim('Make sure you have run: gcloud auth application-default login');
          process.exit(1);
        }
      }

      // Stop existing containers
      logger.step('Stopping existing containers...');
      await exec([...fileArgs, ...allComposeArgs(), 'kill'], {
        cwd: root,
        silent: true,
      });
      await exec([...fileArgs, ...allComposeArgs(), 'down', '-v', '--remove-orphans'], {
        cwd: root,
        silent: true,
      });

      // Build and start
      logger.step('Building and starting...');
      const upArgs = [...fileArgs, ...profileArgs, 'up', '-d'];
      if (opts.build !== false) upArgs.push('--build');
      const upResult = await exec(upArgs, { cwd: root, env: secretEnv });

      if (upResult.code !== 0) {
        logger.error('Failed to start containers');
        process.exit(1);
      }

      logger.blank();
      logger.success('Services started!');
      logger.blank();
      logger.dim(`  Mode:      ${mode}`);
      logger.dim(`  Env:       ${env}`);
      logger.dim('  API:       http://localhost:1954');
      logger.dim('  Docs:      http://localhost:1954/docs');
      if (mode === 'local') {
        logger.dim('  Postgres:  localhost:1961');
      } else {
        logger.dim('  Proxy:     localhost:15432');
      }
      logger.blank();

      // Follow logs unless --no-logs
      if (opts.logs !== false) {
        logger.step('Following logs... (Ctrl+C to stop)');
        await exec([...fileArgs, ...profileArgs, 'logs', '-f'], {
          cwd: root,
          env: secretEnv,
        });
      }
    });
}
```

**Step 2: Verify — build CLI**

```bash
cd cli && npm run build
```

Expected: compiles without errors.

**Step 3: Commit**

```bash
git add cli/src/commands/redock/up.ts
git commit -m "feat(cli): rewrite redock up with env/mode support and secret fetching"
```

---

### Task 8: Update check.ts to validate env-specific files

**Files:**
- Modify: `cli/src/commands/redock/check.ts`

**Step 1: Add env file validation to check command**

After the existing docker-compose.yml check, add checks for the overlay files:

```typescript
// Add after the docker-compose.yml existence check:
const envFiles = ['docker-compose.dev.yml', 'docker-compose.prod.yml', 'docker-compose.local.yml'];
for (const file of envFiles) {
  if (existsSync(resolve(root, file))) {
    logger.pass(`${file} exists`);
  } else {
    logger.fail(`${file} is missing`);
    issues++;
  }
}
```

**Step 2: Verify — build CLI**

```bash
cd cli && npm run build
```

**Step 3: Commit**

```bash
git add cli/src/commands/redock/check.ts
git commit -m "feat(cli): add env overlay file validation to redock check"
```

---

### Task 9: Update dependent CLI commands (open, db, test)

**Files:**
- Modify: `cli/src/commands/open.ts` — remove adminer URL reference if present
- Modify: `cli/src/commands/db/migrate.ts` — uses `containerExec` which changed signature
- Modify: `cli/src/commands/db/upgrade.ts` — same
- Modify: `cli/src/commands/db/downgrade.ts` — same
- Modify: `cli/src/commands/db/rollback.ts` — same

**Step 1: Check and update open.ts**

If `open.ts` references adminer, remove it. Check if db commands use the old `containerExec` from docker.ts.

Read each file. The old `containerExec(cwd, service, command)` is now `containerExec(composeArgs, container, command, opts)`. Update all callers to pass empty compose args (they run against whatever is currently up):

Old pattern:
```typescript
containerExec(root, 'api', ['poetry', 'run', 'alembic', ...])
```

New pattern:
```typescript
await containerExec([], 'api', ['poetry', 'run', 'alembic', ...], { cwd: root })
```

The db commands need to become async.

**Step 2: Verify — build CLI**

```bash
cd cli && npm run build
```

Expected: full clean compile, zero errors.

**Step 3: Commit**

```bash
git add -A && git commit -m "refactor(cli): update db and open commands for new docker.ts API"
```

---

### Task 10: End-to-end verification

**Step 1: Test local mode**

```bash
josi redock up dev --local --no-logs
```

Expected: starts `josi-db` and `josi-api` containers. API accessible at http://localhost:1954/docs. No redis, no adminer, no cloudsql-proxy.

**Step 2: Verify containers**

```bash
josi redock status
```

Expected: shows `josi-db`, `josi-api`, `josi-web` running.

**Step 3: Test cloud mode (dev)**

```bash
josi redock up dev --no-logs
```

Expected: fetches secrets from Secret Manager, starts `josi-cloudsql-proxy` and `josi-api`. No local postgres. API connects to Cloud SQL dev.

**Step 4: Clean up**

```bash
josi redock clean -v -y
```

**Step 5: Final commit (if any fixups needed)**

```bash
git add -A && git commit -m "fix: address issues from e2e testing"
```
