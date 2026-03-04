import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { containerExec, isDockerRunning } from '../../lib/docker.js';
import { confirmAction } from '../../lib/prompt.js';

export function register(parent: Command): void {
  parent
    .command('rollback')
    .description('Undo the last migration')
    .option('-y, --yes', 'Skip confirmation')
    .action(async (opts: { yes?: boolean }) => {
      logger.header('Rollback Last Migration');

      if (!isDockerRunning()) {
        logger.error('Docker is not running.');
        process.exit(1);
      }

      if (!opts.yes) {
        const ok = await confirmAction(
          'Roll back the last migration? This may cause data loss.'
        );
        if (!ok) {
          logger.info('Cancelled.');
          return;
        }
      }

      const root = getProjectRoot();
      logger.step('Rolling back last migration...');

      const result = containerExec(root, 'api', [
        'poetry',
        'run',
        'alembic',
        'downgrade',
        '-1',
      ]);

      if (result.status !== 0) {
        logger.error('Rollback failed.');
        process.exit(1);
      }

      logger.blank();
      logger.success('Last migration rolled back.');
      logger.blank();
    });
}
