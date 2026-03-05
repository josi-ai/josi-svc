import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('login')
    .description('Run gcloud auth login')
    .action(() => {
      logger.step('Logging into GCP...');
      const result = spawnSync('gcloud', ['auth', 'login'], { stdio: 'inherit' });
      if (result.status === 0) {
        logger.success('GCP login complete');
      } else {
        logger.error('GCP login failed');
        process.exit(1);
      }
    });
}
