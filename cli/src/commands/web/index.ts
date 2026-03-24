import type { Command } from 'commander';
import { register as registerDev } from './dev.js';

export function register(program: Command): void {
  const web = program
    .command('web')
    .description('Frontend development commands');

  registerDev(web);
}
