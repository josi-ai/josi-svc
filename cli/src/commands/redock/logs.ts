import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { composeLogs } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('logs [service]')
    .description('Follow container logs')
    .option('--no-follow', 'Print logs without following')
    .addHelpText(
      'after',
      `
Examples:
  $ josi redock logs           # Follow all logs
  $ josi redock logs api       # Follow API logs only
  $ josi redock logs db        # Follow database logs
  $ josi redock logs --no-follow`
    )
    .action((service: string | undefined, opts: { follow: boolean }) => {
      logger.header('Container Logs');
      const root = getProjectRoot();
      composeLogs(root, service, opts.follow);
    });
}
