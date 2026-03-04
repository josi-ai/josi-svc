import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../lib/logger.js';
import { confirmAction } from '../lib/prompt.js';

export function register(program: Command): void {
  program
    .command('nuke')
    .description('Stop all containers, remove volumes, and prune Docker')
    .option('-y, --yes', 'Skip confirmation')
    .addHelpText(
      'after',
      `
Examples:
  $ josi nuke          # Interactive confirmation
  $ josi nuke -y       # Skip confirmation`
    )
    .action(async (opts: { yes?: boolean }) => {
      logger.header('Nuke Everything');

      if (!opts.yes) {
        const ok = await confirmAction(
          'This will stop all josi containers, remove volumes, and prune Docker. Continue?'
        );
        if (!ok) {
          logger.info('Cancelled.');
          return;
        }
      }

      // Stop containers
      logger.step('Stopping all josi containers...');
      try {
        const { getProjectRoot } = await import('../lib/detect.js');
        const root = getProjectRoot();
        spawnSync('docker', ['compose', 'down', '-v', '--remove-orphans'], {
          cwd: root,
          stdio: 'inherit',
        });

        } catch {
        logger.dim('Could not find project root, skipping compose down.');
      }

      // Kill processes on known ports
      logger.step('Killing processes on josi ports...');
      for (const port of [1954, 1961, 1982]) {
        const result = spawnSync('lsof', ['-i', `:${port}`, '-t'], {
          stdio: 'pipe',
          encoding: 'utf-8',
        });
        const pids = (result.stdout ?? '').trim();
        if (pids) {
          for (const pid of pids.split('\n')) {
            spawnSync('kill', ['-9', pid.trim()], { stdio: 'pipe' });
          }
          logger.dim(`  Killed process(es) on port ${port}`);
        }
      }

      // Docker prune
      logger.step('Pruning unused Docker resources...');
      spawnSync('docker', ['system', 'prune', '-f'], { stdio: 'inherit' });

      logger.blank();
      logger.success('Everything nuked. Run "josi redock up" to start fresh.');
      logger.blank();
    });
}
