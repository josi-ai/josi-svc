import type { Command } from 'commander';
import { register as registerAuth } from './auth.js';
import { register as registerLogin } from './login.js';
import { register as registerAdc } from './adc.js';

export function register(program: Command): void {
  const gcp = program
    .command('gcp')
    .description('GCP authentication commands')
    .addHelpText(
      'after',
      `
Examples:
  $ josi gcp auth     # Run both ADC + browser login
  $ josi gcp login    # Browser login only
  $ josi gcp adc      # Application default credentials only`
    );

  registerAuth(gcp);
  registerLogin(gcp);
  registerAdc(gcp);
}
