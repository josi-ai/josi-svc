import type { Command } from 'commander';
import * as logger from '../../lib/logger.js';
import { getProjectRoot } from '../../lib/detect.js';
import { composeExec, isDockerRunning } from '../../lib/docker.js';

export function register(parent: Command): void {
  parent
    .command('adminer')
    .description('Start the Adminer database management UI')
    .action(() => {
      logger.header('Starting Adminer');

      if (!isDockerRunning()) {
        logger.error('Docker is not running. Start Docker Desktop first.');
        process.exit(1);
      }

      const root = getProjectRoot();
      logger.step('Starting Adminer...');

      const result = composeExec(['--profile', 'tools', 'up', '-d', 'adminer'], { cwd: root });

      if (result.status !== 0) {
        logger.error('Failed to start Adminer.');
        process.exit(1);
      }

      logger.blank();
      logger.success('Adminer started!');
      logger.dim('  URL:      http://localhost:1980');
      logger.dim('  System:   PostgreSQL');
      logger.dim('  Server:   db');
      logger.dim('  Username: josi');
      logger.dim('  Password: josi');
      logger.dim('  Database: josi');
      logger.blank();
    });
}
