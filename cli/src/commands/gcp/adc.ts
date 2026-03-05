import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('adc')
    .description('Run gcloud auth application-default login')
    .action(() => {
      logger.step('Setting up application default credentials...');
      const result = spawnSync('gcloud', ['auth', 'application-default', 'login'], {
        stdio: 'inherit',
      });
      if (result.status === 0) {
        logger.success('Application default credentials set');
      } else {
        logger.error('ADC login failed');
        process.exit(1);
      }
    });
}
