import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { containerExec, isDockerRunning } from '../../lib/docker.js';
import { confirmAction } from '../../lib/prompt.js';

export function register(parent: Command): void {
  parent
    .command('downgrade <revision>')
    .description('Downgrade database to a specific revision')
    .option('-y, --yes', 'Skip confirmation')
    .addHelpText(
      'after',
      `
Examples:
  $ josi db downgrade -1       # Downgrade one step
  $ josi db downgrade abc123   # Downgrade to specific revision`
    )
    .action(async (revision: string, opts: { yes?: boolean }) => {
      logger.header('Downgrade Database');

      if (!isDockerRunning()) {
        logger.error('Docker is not running.');
        process.exit(1);
      }

      if (!opts.yes) {
        const ok = await confirmAction(
          `Downgrade database to revision "${revision}"? This may cause data loss.`
        );
        if (!ok) {
          logger.info('Cancelled.');
          return;
        }
      }

      const root = getProjectRoot();
      logger.step(`Downgrading to: ${revision}`);

      const result = await containerExec([], 'api', [
        'poetry',
        'run',
        'alembic',
        'downgrade',
        revision,
      ], { cwd: root });

      if (result.code !== 0) {
        logger.error('Migration downgrade failed.');
        process.exit(1);
      }

      logger.blank();
      logger.success('Database downgraded successfully.');
      logger.blank();
    });
}
