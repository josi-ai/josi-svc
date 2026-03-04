import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import { platform } from 'os';
import * as logger from '../lib/logger.js';
import { URLS } from '../types.js';

export function register(program: Command): void {
  program
    .command('open [target]')
    .description('Open API docs, GraphQL, or redoc in the browser')
    .addHelpText(
      'after',
      `
Targets:
  docs      Swagger UI (default)
  graphql   GraphQL Playground
  redoc     ReDoc documentation

Examples:
  $ josi open              # Open Swagger docs
  $ josi open docs         # Open Swagger docs
  $ josi open graphql      # Open GraphQL Playground
  $ josi open redoc        # Open ReDoc`
    )
    .action((target?: string) => {
      const urlMap: Record<string, string> = {
        docs: URLS.docs,
        graphql: URLS.graphql,
        redoc: URLS.redoc,
      };

      const key = target ?? 'docs';
      const url = urlMap[key];

      if (!url) {
        logger.error(`Unknown target: "${key}". Use: docs, graphql, or redoc`);
        process.exit(1);
      }

      logger.info(`Opening ${key}: ${url}`);

      const openCmd = platform() === 'darwin' ? 'open' : 'xdg-open';
      spawnSync(openCmd, [url], { stdio: 'ignore' });
    });
}
