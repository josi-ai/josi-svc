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
