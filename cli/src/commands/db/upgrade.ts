import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { containerExec, isDockerRunning } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('upgrade')
    .description('Apply all pending migrations')
    .option('-r, --revision <rev>', 'Upgrade to a specific revision', 'head')
    .addHelpText(
      'after',
      `
Examples:
  $ josi db upgrade            # Apply all pending migrations
  $ josi db upgrade -r abc123  # Upgrade to specific revision`
    )
    .action((opts: { revision: string }) => {
      logger.header('Upgrade Database');

      if (!isDockerRunning()) {
        logger.error('Docker is not running.');
        process.exit(1);
      }

      const root = getProjectRoot();
      logger.step(`Upgrading to: ${opts.revision}`);

      const result = containerExec(root, 'api', [
        'poetry',
        'run',
        'alembic',
        'upgrade',
        opts.revision,
      ]);

      if (result.status !== 0) {
        logger.error('Migration upgrade failed.');
        process.exit(1);
      }

      logger.blank();
      logger.success('Database upgraded successfully.');
      logger.blank();
    });
}
