import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { composeUp, isDockerRunning } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('up')
    .description('Start all services (db, redis, api) with Docker Compose')
    .option('--no-build', 'Skip rebuilding the API image')
    .addHelpText(
      'after',
      `
Examples:
  $ josi redock up              # Start with rebuild
  $ josi redock up --no-build   # Start without rebuild`
    )
    .action((opts: { build: boolean }) => {
      logger.header('Starting Josi Services');

      if (!isDockerRunning()) {
        logger.error('Docker is not running. Start Docker Desktop first.');
        process.exit(1);
      }

      const root = getProjectRoot();

      logger.step(opts.build ? 'Building and starting services...' : 'Starting services...');
      composeUp(root, opts.build);

      logger.blank();
      logger.success('Services started!');
      logger.blank();
      logger.dim('  API:       http://localhost:1954');
      logger.dim('  Docs:      http://localhost:1954/docs');
      logger.dim('  GraphQL:   http://localhost:1954/graphql');
      logger.dim('  Postgres:  localhost:1961');
      logger.dim('  Redis:     localhost:1982');
      logger.blank();
      logger.dim('Run "josi redock logs" to follow logs.');
      logger.dim('Run "josi open adminer" for DB management UI.');
      logger.blank();
    });
}
