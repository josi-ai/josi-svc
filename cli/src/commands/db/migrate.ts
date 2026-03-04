import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { containerExec, isDockerRunning } from '../../lib/docker.js';
import { getCurrentBranch, getParentBranch, getNewMigrationFiles, pullAndRebase, hasUncommittedChanges } from '../../lib/git.js';
import { confirmAction } from '../../lib/prompt.js';

export function register(parent: Command): void {
  parent
    .command('migrate <message>')
    .description('Auto-generate a new Alembic migration')
    .option('--skip-conflict-check', 'Skip migration conflict detection')
    .addHelpText(
      'after',
      `
Examples:
  $ josi db migrate "add user preferences table"
  $ josi db migrate "add index on charts.person_id"
  $ josi db migrate "rename column" --skip-conflict-check`
    )
    .action(async (message: string, opts: { skipConflictCheck?: boolean }) => {
      logger.header('Generate Migration');

      if (!isDockerRunning()) {
        logger.error('Docker is not running. Start services with "josi redock up" first.');
        process.exit(1);
      }

      const root = getProjectRoot();
      const branch = getCurrentBranch(root);
      logger.info(`Current branch: ${branch}`);

      // Conflict detection
      if (!opts.skipConflictCheck) {
        logger.step('Checking for migration conflicts...');

        if (hasUncommittedChanges(root)) {
          logger.warn('You have uncommitted changes. Commit or stash before pulling.');
        }

        const parentBranch = getParentBranch(root);
        const newMigrations = getNewMigrationFiles(root, parentBranch);

        if (newMigrations.length > 0) {
          logger.warn(`Found ${newMigrations.length} new migration(s) on ${parentBranch}:`);
          for (const file of newMigrations) {
            logger.dim(`  ${file}`);
          }
          logger.blank();
          const rebase = await confirmAction(
            `Pull and rebase on ${parentBranch} to avoid conflicts?`,
            true
          );
          if (rebase) {
            logger.step(`Rebasing on ${parentBranch}...`);
            if (!pullAndRebase(root)) {
              logger.error('Rebase failed. Resolve conflicts manually.');
              process.exit(1);
            }
            logger.success('Rebase complete.');
          }
        } else {
          logger.pass('No migration conflicts detected.');
        }
      }

      // Generate migration
      logger.step(`Generating migration: "${message}"`);
      const result = containerExec(root, 'api', [
        'poetry',
        'run',
        'alembic',
        'revision',
        '--autogenerate',
        '-m',
        message,
      ]);

      if (result.status !== 0) {
        logger.error('Migration generation failed.');
        logger.dim('Make sure services are running: josi redock up');
        process.exit(1);
      }

      logger.blank();
      logger.success('Migration generated! Review the file before applying.');
      logger.dim('Apply with: josi db upgrade');
      logger.blank();
    });
}
