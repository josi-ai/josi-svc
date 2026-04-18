# Claude Memory: Local Dev Setup (`josi redock up`)

This file documents how the `josi` CLI starts the service locally, in a format
suitable for Claude Code's per-project memory system. Any developer working on
this repo can copy the memory block below into their Claude memory so future
Claude sessions know how local dev is wired without re-deriving it.

## How to install into your Claude memory

Claude Code stores per-project memory at:

```
~/.claude/projects/<sanitized-project-path>/memory/
```

For this repo on macOS that resolves to:

```
~/.claude/projects/-Users-<you>-Developer-josi-josi-svc/memory/
```

Steps:

1. Create the directory if it does not exist:
   ```bash
   mkdir -p ~/.claude/projects/-Users-$(whoami)-Developer-josi-josi-svc/memory
   ```
2. Save the **memory file** block below as `local_dev_setup.md` in that
   directory (keep the YAML frontmatter intact).
3. Add this one-line pointer to that directory's `MEMORY.md` index (create it
   if missing — no frontmatter, just a list):
   ```markdown
   - [Local Dev Setup](local_dev_setup.md) — what `josi redock up` needs and what it starts
   ```

That's it. Next time you open Claude Code in this repo it will load this
memory automatically.

---

## Memory file — copy everything below into `local_dev_setup.md`

```markdown
---
name: Local Dev Setup (josi CLI)
description: What josi redock up needs on the host, what compose files/profiles it uses, and which services + ports it starts for local vs cloud DB modes
type: reference
---

# Running Josi locally via `josi redock up`

The `josi` CLI (TypeScript, in `cli/src/`) is a thin orchestrator over
`docker compose`. It does NOT replace compose — it builds an arg list of
`-f` files plus `--profile` flags, fetches secrets when needed, and spawns
the frontend on the host.

## Host prerequisites

- **Docker Desktop running.** `cli/src/commands/redock/up.ts` calls
  `isDockerRunning()` (runs `docker info`) and exits if Docker is down.
- **Node + npm on the host.** The frontend runs OUTSIDE Docker via
  `npx next dev -p 1989` (`up.ts:182`). If `web/node_modules` is missing,
  the CLI runs `npm install` first.
- **Port 1989 free.** The CLI proactively kills any process on it via
  `lsof -ti:1989` before starting Next.
- **`josi` CLI built/linked.** Run `npm install && npm run build && npm link`
  inside `cli/` so the `josi` binary resolves on PATH.
- **Cloud mode only:** `gcloud auth application-default login` must have been
  run, because `cli/src/lib/secrets.ts` pulls DB creds from GCP Secret Manager
  (`josiam-db-user-{env}`, `josiam-db-password-{env}`) under project `josiam`.
  Local mode (`--local`) needs no GCP auth.

## Project files the CLI expects

Validated at startup in `up.ts:52`:

- `docker-compose.yml` — base (api, web, redis, cloudsql-proxy stub)
- `docker-compose.local.yml` — overlay; adds `db` (pgvector/pg16) on
  `localhost:1961` with creds `josi/josi/josi`
- `docker-compose.dev.yml` / `docker-compose.prod.yml` — cloud overlays;
  enable the `cloudsql-proxy` service on `localhost:15432`
- `.env.local` — both `api` and `web` services load it via `env_file:`.
  **Without this file, compose fails to start.** Copy from `.env.example`.

## Compose invocation built by the CLI

`cli/src/lib/compose.ts` resolves env+mode → files+profiles:

| Command | Files | Profiles |
|---|---|---|
| `josi redock up dev --local` | `docker-compose.yml`, `docker-compose.local.yml` | `local` |
| `josi redock up dev` | `docker-compose.yml`, `docker-compose.dev.yml` | `cloud` |
| `josi redock up prod` | `docker-compose.yml`, `docker-compose.prod.yml` | `cloud` |

Effective command for `up dev --local`:

```
docker compose -f docker-compose.yml -f docker-compose.local.yml \
  --profile local up -d --pull missing api --build
```

The `--profile local` flag is what activates the `db` service
(gated by `profiles: [local]` in `docker-compose.yml`). Without the profile
flag, no Postgres comes up. Same gating exists for `cloud` (cloudsql-proxy)
and `test` (db-test).

## What gets started (local mode)

| Service | Where | Port | Notes |
|---|---|---|---|
| `db` | Docker | `localhost:1961` | pgvector/pg16, creds `josi/josi/josi`, healthcheck-gated |
| `redis` | Docker | `localhost:6399` | redis:7-alpine, used for session cache + usage counters |
| `api` | Docker | `localhost:1954` | FastAPI, hot-reload mount of `./src`, `AUTO_DB_MIGRATION=True` runs Alembic on boot |
| `web` | Host (NOT Docker) | `localhost:1989` | Next.js via `npx next dev`, `NEXT_PUBLIC_API_URL=http://localhost:1954`, `NODE_OPTIONS=--max-old-space-size=4096` |

Note the asymmetry: the `web` service IS defined in `docker-compose.yml` but
the CLI deliberately ignores it and runs Next.js on the host. This is for HMR
speed and to avoid the bind-mount + node_modules-volume dance that breaks
Turbopack. The defined `web` compose service is essentially fallback/CI-only.

## Common flags

- `--local` → use local Postgres instead of Cloud SQL
- `-d, --detach` → background mode; writes PID to `.web-dev.pid`,
  logs to `logs/web-dev.log`
- `--no-web` → backend only
- `--no-build` → skip rebuilding Docker images

## Minimum bootstrap (clean clone → running)

1. Install Docker Desktop, Node, the `josi` CLI (`cd cli && npm i && npm run build && npm link`).
2. `cp .env.example .env.local` and fill in keys (Clerk, OpenAI, etc.).
3. `josi redock up dev --local` — backend in Docker, frontend on host, no GCP needed.

URLs after start:

- API: http://localhost:1954
- API Docs: http://localhost:1954/docs
- Web: http://localhost:1989
- Postgres: localhost:1961 (local mode) or localhost:15432 (cloud mode via proxy)
- Redis: localhost:6399
```
