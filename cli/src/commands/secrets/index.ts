import type { Command } from 'commander';
import { register as registerScan } from './scan.js';

export function register(program: Command): void {
  const secrets = program
    .command('secrets')
    .description('Secret scanning and management');

  registerScan(secrets);
}
