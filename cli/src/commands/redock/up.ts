import type { Command } from 'commander';
import { existsSync, writeFileSync, mkdirSync, openSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawn, execFileSync, type ChildProcess } from 'node:child_process';
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
    .option('-d, --detach', 'Run in background and return the prompt')
    .option('--no-web', 'Skip starting the frontend')
    .option('--no-build', 'Skip rebuilding Docker images')
    .addHelpText(
      'after',
      `
Environments:
  dev, prod

Examples:
  $ josi redock up dev --local       # Full stack, foreground (Ctrl+C to stop)
  $ josi redock up dev --local -d    # Full stack, background
  $ josi redock up dev --no-web      # Backend only
  $ josi redock up dev               # Cloud DB + local frontend`
    )
    .action(async (envArg: string, opts: UpOptions & { detach?: boolean }) => {
      if (!VALID_ENVS.includes(envArg as Env)) {
        logger.error(`Invalid environment '${envArg}'. Must be one of: ${VALID_ENVS.join(', ')}`);
        process.exit(1);
      }
      const env = envArg as Env;
      const mode = opts.local ? 'local' : 'cloud';
      const startWeb = opts.web !== false;
      const detach = !!opts.detach;

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

      // Start backend (api depends on db + redis)
      logger.step('Starting backend (API, DB, Redis)...');
      const upArgs = [...fileArgs, ...profileArgs, 'up', '-d', '--pull', 'missing', 'api'];
      if (opts.build !== false) upArgs.push('--build');

      const upResult = await exec(upArgs, { cwd: root, env: secretEnv });

      if (upResult.code !== 0) {
        logger.error('Failed to start backend containers');
        process.exit(1);
      }

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

          // Kill any existing process on port 1989
          try {
            const pids = execFileSync('lsof', ['-ti:1989'], { encoding: 'utf8' }).trim();
            if (pids) {
              for (const pid of pids.split('\n')) {
                try { process.kill(Number(pid), 'SIGKILL'); } catch { /* already dead */ }
              }
              logger.dim('  Killed existing process on port 1989');
            }
          } catch { /* no process on port — fine */ }

          if (detach) {
            // Background mode: spawn detached, write PID file
            logger.step('Starting frontend in background...');

            const logDir = resolve(root, 'logs');
            if (!existsSync(logDir)) mkdirSync(logDir, { recursive: true });
            const logFile = resolve(logDir, 'web-dev.log');

            const out = openSync(logFile, 'a');
            const webChild = spawn('npx', ['next', 'dev', '-p', '1989'], {
              cwd: webDir,
              detached: true,
              stdio: ['ignore', out, out],
              env: {
                ...process.env,
                NEXT_PUBLIC_API_URL: apiUrl,
                NODE_OPTIONS: '--max-old-space-size=4096',
              },
            });

            // Write PID so `josi redock down` can kill it later
            const pidFile = resolve(root, '.web-dev.pid');
            writeFileSync(pidFile, String(webChild.pid));
            webChild.unref();

            logger.blank();
            logger.success('All services running!');
            logger.dim(`  Web:       http://localhost:1989`);
            logger.dim(`  API:       ${apiUrl}`);
            logger.dim(`  Logs:      tail -f logs/web-dev.log`);
            logger.dim(`  Stop web:  kill $(cat .web-dev.pid)`);
            logger.blank();

            process.exit(0);
          } else {
            // Foreground mode: inherit stdio, Ctrl+C kills both
            logger.step('Starting frontend on http://localhost:1989...');
            logger.blank();

            const webChild = spawn('npx', ['next', 'dev', '-p', '1989'], {
              cwd: webDir,
              stdio: 'inherit',
              env: {
                ...process.env,
                NEXT_PUBLIC_API_URL: apiUrl,
                NODE_OPTIONS: '--max-old-space-size=4096',
              },
            });

            webChild.on('error', (err) => {
              logger.error(`Frontend failed: ${err.message}`);
            });

            // Cleanup on exit
            const cleanup = () => {
              if (!webChild.killed) webChild.kill('SIGTERM');
            };
            process.on('SIGINT', () => { cleanup(); process.exit(0); });
            process.on('SIGTERM', () => { cleanup(); process.exit(0); });

            // Wait for frontend to exit
            await new Promise<void>((res) => {
              webChild.on('close', () => res());
            });
          }
        }
      } else {
        // No web — just show status
        logger.blank();
        logger.dim('  Frontend not started (use without --no-web to include it)');
        logger.blank();
      }
    });
}
