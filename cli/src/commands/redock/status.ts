import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { composePs } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('status')
    .description('Show running container status')
    .action(() => {
      logger.header('Container Status');
      const root = getProjectRoot();
      composePs(root);
    });
}
