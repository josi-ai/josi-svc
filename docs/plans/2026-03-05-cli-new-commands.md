# CLI New Commands Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add four new command groups to the josi CLI: `secrets scan`, `redock check`, `gcp auth/login/adc`, and auto-commit prompt in `db migrate`.

**Architecture:** Each command follows the existing josi CLI pattern: export a `register(program)` function, use the shared logger/detect/prompt/git libs. The secrets scanner needs async `spawn` for streaming git log output. Everything else uses sync `spawnSync`.

**Tech Stack:** TypeScript, Commander.js, Node.js child_process, existing josi CLI libs (logger, detect, git, prompt, docker, tools)

---

### Task 1: Add `secrets scan` lib — secret pattern matching and git history scanning

**Files:**
- Create: `cli/src/lib/secrets-scan.ts`

**Step 1: Create the secrets-scan library**

```typescript
import { spawn } from 'node:child_process';

export interface SecretPattern {
  name: string;
  pattern: RegExp;
}

export const SECRET_PATTERNS: SecretPattern[] = [
  // Database credentials
  { name: 'DB password', pattern: /(?:DB_PASS(?:WORD)?|POSTGRES_PASSWORD|MYSQL_PASSWORD|DATABASE_PASSWORD)\s*[:=]\s*['"]?(?![\s'"${\}])[^\s'"]+/i },
  { name: 'Database URL with credentials', pattern: /(?:postgres|mysql|mongodb|redis):\/\/[^:\s]+:[^@\s]+@/i },

  // API keys
  { name: 'API key', pattern: /(?:API_KEY|APIKEY|api_key)\s*[:=]\s*['"]?(?![\s'"${\}])[A-Za-z0-9_\-]{20,}/i },
  { name: 'Auth token', pattern: /(?:AUTH_TOKEN|ACCESS_TOKEN|SECRET_TOKEN|BEARER_TOKEN)\s*[:=]\s*['"]?(?![\s'"${\}])[A-Za-z0-9_\-\.]{20,}/i },
  { name: 'Secret key', pattern: /(?:SECRET_KEY|APP_SECRET|JWT_SECRET|ENCRYPTION_KEY)\s*[:=]\s*['"]?(?![\s'"${\}])[A-Za-z0-9_\-\.]{16,}/i },

  // Stripe
  { name: 'Stripe secret key', pattern: /sk_(?:live|test)_[A-Za-z0-9]{20,}/ },
  { name: 'Stripe publishable key', pattern: /pk_(?:live|test)_[A-Za-z0-9]{20,}/ },

  // OpenAI / LLM
  { name: 'OpenAI API key', pattern: /sk-[A-Za-z0-9]{20,}/ },
  { name: 'Anthropic API key', pattern: /sk-ant-[A-Za-z0-9_\-]{20,}/ },

  // Private keys
  { name: 'Private key', pattern: /-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----/ },

  // Generic password assignments
  { name: 'Password assignment', pattern: /(?:_PASSWORD|_PASSWD|_PWD)\s*[:=]\s*['"]?(?![\s'"${\}])[^\s'"]{8,}/i },

  // Connection strings
  { name: 'Connection string', pattern: /(?:CONNECTION_STRING|CONN_STR)\s*[:=]\s*['"]?(?![\s'"${\}])[^\s'"]+/i },

  // SendGrid / Twilio
  { name: 'SendGrid API key', pattern: /SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}/ },
  { name: 'Twilio auth token', pattern: /(?:TWILIO_AUTH_TOKEN)\s*[:=]\s*['"]?[a-f0-9]{32}/i },

  // Base64-encoded secrets
  { name: 'Base64 secret', pattern: /(?:SECRET|KEY|TOKEN|CREDENTIAL|PASSWORD).*[:=]\s*['"]?[A-Za-z0-9+\/]{40,}={0,2}['"]?/i },
];

export const SENSITIVE_FILE_PATTERNS = [
  'docker-compose*.yml',
  'docker-compose*.yaml',
  '.env',
  '.env.*',
  '*.env',
  'sa-key.json',
  '**/sa-key.json',
];

export interface ScanMatch {
  file: string;
  commit: string;
  commitDate: string;
  author: string;
  patternName: string;
  line: string;
  stillPresent: boolean;
}

export function scanHistory(
  cwd: string,
  filePatterns: string[],
  onProgress?: (commit: string) => void,
): Promise<ScanMatch[]> {
  return new Promise((resolve, reject) => {
    const args = [
      'log',
      '--all',
      '--diff-filter=ACMR',
      '--format=%H||%aI||%an',
      '-p',
      '--',
      ...filePatterns,
    ];

    const child = spawn('git', args, {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let output = '';
    child.stdout!.on('data', (data: Buffer) => {
      output += data.toString();
    });

    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code !== 0 && output.length === 0) {
        resolve([]);
        return;
      }

      const matches: ScanMatch[] = [];
      const lines = output.split('\n');

      let currentCommit = '';
      let currentDate = '';
      let currentAuthor = '';
      let currentFile = '';

      for (const line of lines) {
        const commitMatch = line.match(/^([a-f0-9]{40})\|\|(.+)\|\|(.+)$/);
        if (commitMatch) {
          currentCommit = commitMatch[1];
          currentDate = commitMatch[2];
          currentAuthor = commitMatch[3];
          if (onProgress) onProgress(currentCommit.substring(0, 8));
          continue;
        }

        const fileMatch = line.match(/^\+\+\+ b\/(.+)$/);
        if (fileMatch) {
          currentFile = fileMatch[1];
          continue;
        }

        if (!line.startsWith('+') || line.startsWith('+++')) continue;
        const addedLine = line.substring(1);

        for (const pattern of SECRET_PATTERNS) {
          if (pattern.pattern.test(addedLine)) {
            matches.push({
              file: currentFile,
              commit: currentCommit,
              commitDate: currentDate,
              author: currentAuthor,
              patternName: pattern.name,
              line: maskSecret(addedLine.trim()),
              stillPresent: false,
            });
            break;
          }
        }
      }

      resolve(matches);
    });
  });
}

export function checkCurrentFile(
  cwd: string,
  filePath: string,
  pattern: RegExp,
): Promise<boolean> {
  return new Promise((resolve) => {
    const child = spawn('git', ['show', `HEAD:${filePath}`], {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let content = '';
    child.stdout!.on('data', (data: Buffer) => {
      content += data.toString();
    });

    child.on('close', () => {
      resolve(pattern.test(content));
    });
  });
}

function maskSecret(line: string): string {
  return line.replace(
    /([:=]\s*['"]?)([A-Za-z0-9+\/_\-.]{12,})/g,
    (_match, prefix: string, value: string) => {
      if (value.length <= 8) return `${prefix}${'*'.repeat(value.length)}`;
      const start = value.substring(0, 4);
      const end = value.substring(value.length - 4);
      return `${prefix}${start}${'*'.repeat(value.length - 8)}${end}`;
    },
  );
}
```

**Step 2: Commit**

```bash
git add cli/src/lib/secrets-scan.ts
git commit -m "feat(cli): add secrets scanning library"
```

---

### Task 2: Add `josi secrets scan` command

**Files:**
- Create: `cli/src/commands/secrets/index.ts`
- Create: `cli/src/commands/secrets/scan.ts`
- Modify: `cli/bin/josi.ts`

**Step 1: Create the secrets group index**

Create `cli/src/commands/secrets/index.ts`:

```typescript
import type { Command } from 'commander';
import { register as registerScan } from './scan.js';

export function register(program: Command): void {
  const secrets = program
    .command('secrets')
    .description('Secret scanning and management');

  registerScan(secrets);
}
```

**Step 2: Create the scan command**

Create `cli/src/commands/secrets/scan.ts`:

```typescript
import type { Command } from 'commander';
import {
  scanHistory,
  checkCurrentFile,
  SENSITIVE_FILE_PATTERNS,
  SECRET_PATTERNS,
  type ScanMatch,
} from '../../lib/secrets-scan.js';
import { getProjectRoot } from '../../lib/detect.js';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('scan')
    .description('Scan git history for secrets in sensitive files')
    .option('--all-files', 'Scan all files, not just sensitive file patterns')
    .addHelpText(
      'after',
      `
Scans for: API keys (Stripe, OpenAI, Anthropic), private keys,
  database URLs, JWT secrets, passwords, and other sensitive patterns.

Reports: Active secrets (still in files) and historical secrets (removed
  but still in git history).

Examples:
  $ josi secrets scan              # Scan sensitive files only
  $ josi secrets scan --all-files  # Scan all files in history`
    )
    .action(async (opts: { allFiles?: boolean }) => {
      const root = getProjectRoot();

      logger.header('Secret Scanner');
      logger.info(
        `Checking ${opts.allFiles ? 'all files' : 'sensitive files'} across git history...`
      );

      const filePatterns = opts.allFiles ? ['*'] : SENSITIVE_FILE_PATTERNS;

      let commitCount = 0;
      const matches = await scanHistory(root, filePatterns, () => {
        commitCount++;
      });

      logger.info(`Scanned ${commitCount} commits`);

      if (matches.length === 0) {
        logger.success('No secrets found in git history');
        return;
      }

      // Check which secrets are still in current files
      logger.info('Checking current files for active secrets...');
      for (const match of matches) {
        const pattern = SECRET_PATTERNS.find((p) => p.name === match.patternName);
        if (pattern) {
          match.stillPresent = await checkCurrentFile(root, match.file, pattern.pattern);
        }
      }

      const uniqueFindings = deduplicateFindings(matches);
      const activeCount = uniqueFindings.filter((m) => m.stillPresent).length;
      const historicalCount = uniqueFindings.filter((m) => !m.stillPresent).length;

      if (activeCount > 0) {
        logger.header('ACTIVE — secrets still in current files');
        for (const match of uniqueFindings.filter((m) => m.stillPresent)) {
          logger.fail(match.file);
          console.log(`    Type:   ${match.patternName}`);
          console.log(`    Line:   ${match.line}`);
          console.log(
            `    Commit: ${match.commit.substring(0, 8)} (${match.commitDate.split('T')[0]}) by ${match.author}`
          );
          console.log('');
        }
      }

      if (historicalCount > 0) {
        logger.header('HISTORICAL — removed but still in git history');
        for (const match of uniqueFindings.filter((m) => !m.stillPresent)) {
          logger.warn(match.file);
          console.log(`    Type:   ${match.patternName}`);
          console.log(`    Line:   ${match.line}`);
          console.log(
            `    Commit: ${match.commit.substring(0, 8)} (${match.commitDate.split('T')[0]}) by ${match.author}`
          );
          console.log('');
        }
      }

      logger.header('Summary');
      if (activeCount > 0) {
        logger.fail(`${activeCount} active secret(s) — rotate these immediately`);
      }
      if (historicalCount > 0) {
        logger.warn(`${historicalCount} historical secret(s) — consider cleaning git history`);
      }
      logger.info(
        `Total: ${uniqueFindings.length} unique finding(s) from ${matches.length} match(es)`
      );

      if (activeCount > 0) {
        process.exit(2);
      } else if (historicalCount > 0) {
        process.exit(1);
      }
    });
}

function deduplicateFindings(matches: ScanMatch[]): ScanMatch[] {
  const seen = new Map<string, ScanMatch>();
  for (const match of matches) {
    const key = `${match.file}::${match.patternName}`;
    const existing = seen.get(key);
    if (!existing || match.commitDate > existing.commitDate) {
      seen.set(key, match);
    }
  }
  return Array.from(seen.values());
}
```

**Step 3: Register in josi.ts**

Add to `cli/bin/josi.ts` after the existing imports:

```typescript
import { register as registerSecrets } from '../src/commands/secrets/index.js';
```

Add after `registerEnv(program);`:

```typescript
registerSecrets(program);
```

**Step 4: Build and test**

Run: `cd cli && npm run build`
Run: `./cli/bin/josi.ts secrets scan`
Expected: Scanner runs and reports findings (or "No secrets found")

**Step 5: Commit**

```bash
git add cli/src/commands/secrets/ cli/bin/josi.ts
git commit -m "feat(cli): add secrets scan command"
```

---

### Task 3: Add `josi redock check` command

**Files:**
- Create: `cli/src/commands/redock/check.ts`
- Modify: `cli/src/commands/redock/index.ts`

**Step 1: Create the check command**

Create `cli/src/commands/redock/check.ts`:

```typescript
import type { Command } from 'commander';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { getProjectRoot } from '../../lib/detect.js';
import { composeExec } from '../../lib/docker.js';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('check')
    .description('Validate Docker and project setup')
    .addHelpText(
      'after',
      `
Validates:
  - docker-compose.yml exists and parses correctly
  - Dockerfile exists
  - Python version in Dockerfile matches pyproject.toml
  - Required project files exist (src/, pyproject.toml, poetry.lock)
  - Alembic config is present
  - Docker Compose config merges correctly

Examples:
  $ josi redock check`
    )
    .action(() => {
      const root = getProjectRoot();
      let issues = 0;

      logger.header('Redock Setup Check');

      // --- Docker Compose ---
      logger.info('Docker Compose files');

      if (existsSync(resolve(root, 'docker-compose.yml'))) {
        logger.pass('docker-compose.yml exists');
      } else {
        logger.fail('docker-compose.yml is missing');
        issues++;
      }

      // --- Dockerfile ---
      logger.blank();
      logger.info('Dockerfile');

      const dockerfile = resolve(root, 'Dockerfile');
      if (existsSync(dockerfile)) {
        logger.pass('Dockerfile exists');

        const content = readFileSync(dockerfile, 'utf-8');
        const pythonMatch = content.match(/^FROM python:(\d+\.\d+)/m);

        if (pythonMatch) {
          const dockerPython = pythonMatch[1];
          logger.pass(`Dockerfile Python version: ${dockerPython}`);

          const pyprojectPath = resolve(root, 'pyproject.toml');
          if (existsSync(pyprojectPath)) {
            const pyproject = readFileSync(pyprojectPath, 'utf-8');
            const pyMatch = pyproject.match(/python\s*=\s*"[\^~>=<]*(\d+\.\d+)/m);

            if (pyMatch) {
              const pyprojectPython = pyMatch[1];
              if (dockerPython === pyprojectPython) {
                logger.pass('Python versions match');
              } else {
                logger.fail(
                  `Python version mismatch: Dockerfile=${dockerPython}, pyproject.toml=${pyprojectPython}`
                );
                issues++;
              }
            }
          }
        }
      } else {
        logger.fail('Dockerfile is missing');
        issues++;
      }

      // --- Docker Compose Validation ---
      logger.blank();
      logger.info('Docker Compose validation');

      if (existsSync(resolve(root, 'docker-compose.yml'))) {
        const result = composeExec(['config', '--services'], {
          cwd: root,
          stdio: 'pipe',
        });
        if (result.status === 0) {
          logger.pass('docker-compose.yml parses correctly');
          const services = (result.stdout?.toString() ?? '').trim().split('\n').filter(Boolean);
          logger.dim(`  Services: ${services.join(', ')}`);
        } else {
          logger.fail('docker-compose.yml has errors');
          logger.dim('  Run: docker compose config');
          issues++;
        }
      }

      // --- Project Files ---
      logger.blank();
      logger.info('Project files');

      const requiredFiles: Array<{ path: string; label: string; required: boolean }> = [
        { path: 'src/josi', label: 'src/josi/', required: true },
        { path: 'pyproject.toml', label: 'pyproject.toml', required: true },
        { path: 'poetry.lock', label: 'poetry.lock', required: false },
        { path: 'alembic.ini', label: 'alembic.ini', required: true },
        { path: 'src/alembic', label: 'src/alembic/', required: true },
        { path: '.env', label: '.env', required: false },
        { path: '.env.example', label: '.env.example', required: true },
      ];

      for (const file of requiredFiles) {
        if (existsSync(resolve(root, file.path))) {
          logger.pass(`${file.label} exists`);
        } else if (file.required) {
          logger.fail(`${file.label} is missing`);
          issues++;
        } else {
          logger.warn(`${file.label} is missing`);
        }
      }

      // --- Entrypoint ---
      const entrypoint = resolve(root, 'entrypoint.sh');
      if (existsSync(entrypoint)) {
        logger.pass('entrypoint.sh exists');
        try {
          const stats = statSync(entrypoint);
          if (stats.mode & 0o111) {
            logger.pass('entrypoint.sh is executable');
          } else {
            logger.warn('entrypoint.sh is not executable (chmod +x entrypoint.sh)');
          }
        } catch {
          // ignore
        }
      }

      // --- Summary ---
      logger.blank();
      if (issues === 0) {
        logger.success('All checks passed!');
      } else {
        logger.error(`Found ${issues} issue(s) that need fixing.`);
        process.exit(1);
      }
      logger.blank();
    });
}
```

**Step 2: Register in redock group**

Add to `cli/src/commands/redock/index.ts`:

Import:
```typescript
import { register as registerCheck } from './check.js';
```

Add inside the `register` function, after `registerAdminer(redock);`:
```typescript
registerCheck(redock);
```

**Step 3: Build and test**

Run: `cd cli && npm run build`
Run: `./cli/bin/josi.ts redock check`
Expected: Shows validation results for the project

**Step 4: Commit**

```bash
git add cli/src/commands/redock/check.ts cli/src/commands/redock/index.ts
git commit -m "feat(cli): add redock check command"
```

---

### Task 4: Add `josi gcp` command group

**Files:**
- Create: `cli/src/commands/gcp/index.ts`
- Create: `cli/src/commands/gcp/auth.ts`
- Create: `cli/src/commands/gcp/login.ts`
- Create: `cli/src/commands/gcp/adc.ts`
- Modify: `cli/bin/josi.ts`

**Step 1: Create the GCP group index**

Create `cli/src/commands/gcp/index.ts`:

```typescript
import type { Command } from 'commander';
import { register as registerAuth } from './auth.js';
import { register as registerLogin } from './login.js';
import { register as registerAdc } from './adc.js';

export function register(program: Command): void {
  const gcp = program
    .command('gcp')
    .description('GCP authentication commands')
    .addHelpText(
      'after',
      `
Examples:
  $ josi gcp auth     # Run both ADC + browser login
  $ josi gcp login    # Browser login only
  $ josi gcp adc      # Application default credentials only`
    );

  registerAuth(gcp);
  registerLogin(gcp);
  registerAdc(gcp);
}
```

**Step 2: Create auth.ts**

Create `cli/src/commands/gcp/auth.ts`:

```typescript
import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('auth')
    .description('Run both ADC and browser login')
    .action(() => {
      logger.header('GCP Authentication');

      logger.step('Setting up application default credentials...');
      const adc = spawnSync('gcloud', ['auth', 'application-default', 'login'], {
        stdio: 'inherit',
      });
      if (adc.status !== 0) {
        logger.error('ADC login failed');
        process.exit(1);
      }
      logger.success('Application default credentials set');

      logger.step('Logging into GCP...');
      const login = spawnSync('gcloud', ['auth', 'login'], { stdio: 'inherit' });
      if (login.status !== 0) {
        logger.error('GCP login failed');
        process.exit(1);
      }
      logger.success('GCP login complete');
    });
}
```

**Step 3: Create login.ts**

Create `cli/src/commands/gcp/login.ts`:

```typescript
import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('login')
    .description('Run gcloud auth login')
    .action(() => {
      logger.step('Logging into GCP...');
      const result = spawnSync('gcloud', ['auth', 'login'], { stdio: 'inherit' });
      if (result.status === 0) {
        logger.success('GCP login complete');
      } else {
        logger.error('GCP login failed');
        process.exit(1);
      }
    });
}
```

**Step 4: Create adc.ts**

Create `cli/src/commands/gcp/adc.ts`:

```typescript
import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('adc')
    .description('Run gcloud auth application-default login')
    .action(() => {
      logger.step('Setting up application default credentials...');
      const result = spawnSync('gcloud', ['auth', 'application-default', 'login'], {
        stdio: 'inherit',
      });
      if (result.status === 0) {
        logger.success('Application default credentials set');
      } else {
        logger.error('ADC login failed');
        process.exit(1);
      }
    });
}
```

**Step 5: Register in josi.ts**

Add to `cli/bin/josi.ts` after the secrets import:

```typescript
import { register as registerGcp } from '../src/commands/gcp/index.js';
```

Add after `registerSecrets(program);`:

```typescript
registerGcp(program);
```

**Step 6: Build and test**

Run: `cd cli && npm run build`
Run: `./cli/bin/josi.ts gcp --help`
Expected: Shows auth, login, adc subcommands

**Step 7: Commit**

```bash
git add cli/src/commands/gcp/ cli/bin/josi.ts
git commit -m "feat(cli): add gcp auth commands"
```

---

### Task 5: Add auto-commit prompt to `josi db migrate`

**Files:**
- Modify: `cli/src/commands/db/migrate.ts`

**Step 1: Add auto-commit prompt after migration generation**

In `cli/src/commands/db/migrate.ts`, add a `gitExec` import at line 5:

```typescript
import { getCurrentBranch, getParentBranch, getNewMigrationFiles, pullAndRebase, hasUncommittedChanges, gitExec } from '../../lib/git.js';
```

Replace lines 85-88 (the success block at the end of the action) with:

```typescript
      logger.blank();
      logger.success('Migration generated! Review the file before applying.');

      // Show new migration files
      const { stdout: newFiles } = gitExec(
        ['status', '--short', '--', 'src/alembic/versions/'],
        root
      );
      if (newFiles) {
        logger.info('New files:');
        logger.dim(newFiles);
      }

      // Offer to commit
      const shouldCommit = await confirmAction('Commit this migration?');
      if (shouldCommit) {
        const { status: addStatus } = gitExec(
          ['add', 'src/alembic/versions/'],
          root
        );
        if (addStatus !== 0) {
          logger.error('Failed to stage migration files.');
          process.exit(1);
        }

        const { status: commitStatus } = gitExec(
          ['commit', '-m', `alembic: ${message}`],
          root
        );
        if (commitStatus !== 0) {
          logger.error('Commit failed.');
          process.exit(1);
        }
        logger.success('Migration committed.');
      } else {
        logger.dim('Apply with: josi db upgrade');
      }
      logger.blank();
```

**Step 2: Build and test**

Run: `cd cli && npm run build`
Run: `./cli/bin/josi.ts db migrate --help`
Expected: Help text shows (no functional change to help)

**Step 3: Commit**

```bash
git add cli/src/commands/db/migrate.ts
git commit -m "feat(cli): add auto-commit prompt to db migrate"
```

---

### Task 6: Final build and verify all commands

**Step 1: Full build**

Run: `cd cli && npm run build`
Expected: No TypeScript errors

**Step 2: Verify help output for all new commands**

Run: `./cli/bin/josi.ts --help`
Expected: Shows `secrets`, `gcp` groups and all existing commands

Run: `./cli/bin/josi.ts secrets --help`
Expected: Shows `scan` subcommand

Run: `./cli/bin/josi.ts redock --help`
Expected: Shows `check` alongside up, status, logs, clean, adminer

Run: `./cli/bin/josi.ts gcp --help`
Expected: Shows auth, login, adc subcommands

**Step 3: Smoke test secrets scan**

Run: `./cli/bin/josi.ts secrets scan`
Expected: Scans git history, reports findings or "No secrets found"

**Step 4: Smoke test redock check**

Run: `./cli/bin/josi.ts redock check`
Expected: Shows validation results for project setup

**Step 5: Final commit if any fixes needed**

```bash
git add -A cli/
git commit -m "feat(cli): add secrets scan, redock check, gcp auth commands"
```
