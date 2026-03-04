import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../lib/logger.js';
import { isDockerRunning, composeExec } from '../lib/docker.js';
import { SERVICES } from '../types.js';

export function register(program: Command): void {
  program
    .command('status')
    .description('Show development environment dashboard')
    .action(async () => {
      logger.header('Josi Status Dashboard');

      // Docker daemon
      logger.info('Docker');
      logger.blank();
      if (isDockerRunning()) {
        logger.pass('Docker daemon running');
      } else {
        logger.fail('Docker daemon not running');
        logger.blank();
        return;
      }

      // Containers
      logger.blank();
      logger.info('Containers');
      logger.blank();
      try {
        const { getProjectRoot } = await import('../lib/detect.js');
        const root = getProjectRoot();
        const result = composeExec(['ps', '--format', 'json'], {
          cwd: root,
          stdio: 'pipe',
        });
        const output = result.stdout?.toString() ?? '';
        if (output.trim()) {
          // Parse JSON lines
          const lines = output.trim().split('\n');
          for (const line of lines) {
            try {
              const container = JSON.parse(line);
              const name = container.Name ?? container.Service ?? 'unknown';
              const state = container.State ?? container.Status ?? 'unknown';
              if (state === 'running') {
                logger.pass(name, state);
              } else {
                logger.fail(name, state);
              }
            } catch {
              // Not JSON, show raw
              logger.dim(line);
            }
          }
        } else {
          logger.dim('No containers running');
        }
      } catch {
        logger.dim('Not in josi-svc directory — skipping container check');
      }

      // Service connectivity
      logger.blank();
      logger.info('Service Connectivity');
      logger.blank();

      for (const [, svc] of Object.entries(SERVICES)) {
        const result = spawnSync('lsof', ['-i', `:${svc.port}`, '-t'], {
          stdio: 'pipe',
          encoding: 'utf-8',
        });
        const listening = (result.stdout ?? '').trim().length > 0;
        if (listening) {
          logger.pass(`${svc.name}`, `listening on :${svc.port}`);
        } else {
          logger.fail(`${svc.name}`, `not listening on :${svc.port}`);
        }
      }

      // API health
      logger.blank();
      logger.info('API Health');
      logger.blank();
      const healthResult = spawnSync(
        'curl',
        ['-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:1954/api/v1/health'],
        { stdio: 'pipe', encoding: 'utf-8', timeout: 5000 }
      );
      const statusCode = (healthResult.stdout ?? '').trim();
      if (statusCode === '200') {
        logger.pass('API health check', 'HTTP 200');
      } else if (statusCode) {
        logger.fail('API health check', `HTTP ${statusCode}`);
      } else {
        logger.fail('API health check', 'unreachable');
      }

      logger.blank();
    });
}
