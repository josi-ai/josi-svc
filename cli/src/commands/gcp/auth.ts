import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('auth')
    .description('Run both ADC and browser login')
    .action(() => {
      logger.header('GCP Authentication');

      logger.step('Setting up application default credentials...');
      const adc = spawnSync('gcloud', ['auth', 'application-default', 'login'], {
        stdio: 'inherit',
      });
      if (adc.status !== 0) {
        logger.error('ADC login failed');
        process.exit(1);
      }
      logger.success('Application default credentials set');

      logger.step('Logging into GCP...');
      const login = spawnSync('gcloud', ['auth', 'login'], { stdio: 'inherit' });
      if (login.status !== 0) {
        logger.error('GCP login failed');
        process.exit(1);
      }
      logger.success('GCP login complete');
    });
}
