import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { exec } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('status')
    .description('Show running container status')
    .action(async () => {
      logger.header('Container Status');
      const root = getProjectRoot();
      await exec(['ps', '--format', 'table'], { cwd: root });
    });
}
