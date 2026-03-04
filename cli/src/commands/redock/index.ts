import type { Command } from 'commander';
import { register as registerUp } from './up.js';
import { register as registerStatus } from './status.js';
import { register as registerLogs } from './logs.js';
import { register as registerClean } from './clean.js';

export function register(program: Command): void {
  const redock = program
    .command('redock')
    .description('Docker Compose service management');

  registerUp(redock);
  registerStatus(redock);
  registerLogs(redock);
  registerClean(redock);
}
