import type { Command } from 'commander';
import { register as registerMigrate } from './migrate.js';
import { register as registerUpgrade } from './upgrade.js';
import { register as registerDowngrade } from './downgrade.js';
import { register as registerRollback } from './rollback.js';

export function register(program: Command): void {
  const db = program
    .command('db')
    .description('Database migration management (Alembic)');

  registerMigrate(db);
  registerUpgrade(db);
  registerDowngrade(db);
  registerRollback(db);
}
