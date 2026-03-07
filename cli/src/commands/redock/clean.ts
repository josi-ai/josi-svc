import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { exec } from '../../lib/docker.js';
import { confirmAction } from '../../lib/prompt.js';

export function register(parent: Command): void {
  parent
    .command('clean')
    .description('Stop all containers and optionally remove volumes')
    .option('-v, --volumes', 'Also remove Docker volumes (database data)')
    .option('-y, --yes', 'Skip confirmation')
    .addHelpText(
      'after',
      `
Examples:
  $ josi redock clean          # Stop containers
  $ josi redock clean -v       # Stop and remove volumes (fresh DB)
  $ josi redock clean -v -y    # Skip confirmation`
    )
    .action(async (opts: { volumes?: boolean; yes?: boolean }) => {
      logger.header('Cleaning Up');
      const root = getProjectRoot();

      if (opts.volumes && !opts.yes) {
        const ok = await confirmAction(
          'This will delete all Docker volumes including database data. Continue?'
        );
        if (!ok) {
          logger.info('Cancelled.');
          return;
        }
      }

      logger.step('Stopping containers...');
      const args = ['down'];
      if (opts.volumes) args.push('-v', '--remove-orphans');
      await exec(args, { cwd: root });

      logger.blank();
      logger.success(
        opts.volumes
          ? 'Containers stopped and volumes removed.'
          : 'Containers stopped.'
      );
      logger.blank();
    });
}
