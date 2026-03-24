import type { Command } from 'commander';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawn, type ChildProcess } from 'node:child_process';
import { VALID_ENVS, type Env, type UpOptions } from '../../types.js';
import { buildComposeConfig, composeFileArgs, composeProfileArgs, allComposeArgs } from '../../lib/compose.js';
import { exec, isDockerRunning } from '../../lib/docker.js';
import { fetchDbCredentials } from '../../lib/secrets.js';
import { getProjectRoot } from '../../lib/detect.js';
import * as logger from '../../lib/logger.js';

export function register(parent: Command): void {
  parent
    .command('up <env>')
    .description('Start all services: backend (Docker) + frontend (local)')
    .option('--local', 'Use local database instead of Cloud SQL')
    .option('--no-logs', 'Do not follow backend logs')
    .option('--no-web', 'Skip starting the frontend')
    .option('--no-build', 'Skip rebuilding Docker images')
    .addHelpText(
      'after',
      `
Environments:
  dev, prod

Examples:
  $ josi redock up dev --local    # Full stack: local DB + local frontend
  $ josi redock up dev            # Cloud DB + local frontend
  $ josi redock up dev --no-web   # Backend only, no frontend`
    )
    .action(async (envArg: string, opts: UpOptions) => {
      if (!VALID_ENVS.includes(envArg as Env)) {
        logger.error(`Invalid environment '${envArg}'. Must be one of: ${VALID_ENVS.join(', ')}`);
        process.exit(1);
      }
      const env = envArg as Env;
      const mode = opts.local ? 'local' : 'cloud';
      const startWeb = opts.web !== false;

      if (!isDockerRunning()) {
        logger.error('Docker is not running. Start Docker Desktop first.');
        process.exit(1);
      }

      const root = getProjectRoot();
      const webDir = resolve(root, 'web');

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

      // Stop existing containers (backend only — web runs locally)
      logger.step('Stopping existing containers...');
      await exec([...fileArgs, ...allComposeArgs(), 'kill'], {
        cwd: root,
        silent: true,
      });
      await exec([...fileArgs, ...allComposeArgs(), 'down', '-v', '--remove-orphans'], {
        cwd: root,
        silent: true,
      });

      // Build and start backend only (api + db + redis)
      logger.step('Starting backend (API, DB, Redis)...');
      const upArgs = [...fileArgs, ...profileArgs, 'up', '-d', '--pull', 'missing', 'api'];
      if (opts.build !== false) upArgs.push('--build');

      const upResult = await exec(upArgs, { cwd: root, env: secretEnv });

      if (upResult.code !== 0) {
        logger.error('Failed to start backend containers');
        process.exit(1);
      }

      // Determine API URL for the frontend
      // In both local and cloud mode, the API container runs on localhost:1954
      const apiUrl = 'http://localhost:1954';

      logger.blank();
      logger.success('Backend started!');
      logger.dim(`  API:       ${apiUrl}`);
      logger.dim('  Docs:      http://localhost:1954/docs');
      if (mode === 'local') {
        logger.dim('  Postgres:  localhost:1961');
      } else {
        logger.dim('  Proxy:     localhost:15432');
      }
      logger.dim('  Redis:     localhost:6399');
      logger.blank();

      // Start frontend locally
      let webChild: ChildProcess | null = null;
      if (startWeb) {
        if (!existsSync(webDir)) {
          logger.error('web/ directory not found — skipping frontend');
        } else {
          // Install deps if needed
          if (!existsSync(resolve(webDir, 'node_modules'))) {
            logger.step('Installing frontend dependencies...');
            const install = spawn('npm', ['install'], {
              cwd: webDir,
              stdio: 'inherit',
            });
            await new Promise<void>((res, rej) => {
              install.on('close', (code) => (code === 0 ? res() : rej(new Error('npm install failed'))));
              install.on('error', rej);
            });
          }

          logger.step('Starting frontend on http://localhost:1989...');
          logger.blank();

          webChild = spawn('npx', ['next', 'dev', '-p', '1989'], {
            cwd: webDir,
            stdio: 'inherit',
            env: {
              ...process.env,
              NEXT_PUBLIC_API_URL: apiUrl,
            },
          });

          webChild.on('error', (err) => {
            logger.error(`Frontend failed: ${err.message}`);
          });
        }
      }

      // Cleanup: kill frontend when process exits
      const cleanup = () => {
        if (webChild && !webChild.killed) {
          webChild.kill('SIGTERM');
        }
      };
      process.on('SIGINT', () => { cleanup(); process.exit(0); });
      process.on('SIGTERM', () => { cleanup(); process.exit(0); });

      // Follow backend logs unless --no-logs
      if (opts.logs !== false && !startWeb) {
        // If no web, follow Docker logs
        logger.step('Following backend logs... (Ctrl+C to stop)');
        await exec([...fileArgs, ...profileArgs, 'logs', '-f'], {
          cwd: root,
          env: secretEnv,
        });
      } else if (startWeb && webChild) {
        // If web is running, just wait for it (its stdio is inherited)
        await new Promise<void>((res) => {
          webChild!.on('close', () => res());
        });
      }
    });
}
