import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../lib/logger.js';
import { SERVICES } from '../types.js';

export function register(program: Command): void {
  program
    .command('services')
    .description('List all services with their ports and status')
    .action(() => {
      logger.header('Josi Services');

      const rows: string[][] = [];

      for (const [key, svc] of Object.entries(SERVICES)) {
        const result = spawnSync('lsof', ['-i', `:${svc.port}`, '-t'], {
          stdio: 'pipe',
          encoding: 'utf-8',
        });
        const running = (result.stdout ?? '').trim().length > 0;
        const status = running ? 'running' : 'stopped';

        rows.push([key, svc.name, String(svc.port), status]);
      }

      // Table header
      const cols = ['Service', 'Name', 'Port', 'Status'];
      const widths = cols.map((c, i) =>
        Math.max(c.length, ...rows.map((r) => r[i].length))
      );

      const hr = widths.map((w) => '─'.repeat(w + 2)).join('┼');
      const fmt = (row: string[]) =>
        row.map((c, i) => ` ${c.padEnd(widths[i])} `).join('│');

      console.log(`  ${fmt(cols)}`);
      console.log(`  ${hr}`);
      for (const row of rows) {
        console.log(`  ${fmt(row)}`);
      }
      logger.blank();

      logger.dim('Endpoints:');
      logger.dim('  API Docs:    http://localhost:1954/docs');
      logger.dim('  GraphQL:     http://localhost:1954/graphql');
      logger.dim('  Health:      http://localhost:1954/api/v1/health');
      logger.blank();
    });
}
