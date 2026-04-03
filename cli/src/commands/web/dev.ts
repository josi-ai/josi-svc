import type { Command } from 'commander';
import { spawn, execFileSync } from 'node:child_process';
import { existsSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';
import { getProjectRoot } from '../../lib/detect.js';
import * as logger from '../../lib/logger.js';

export function register(parent: Command): void {
  parent
    .command('dev')
    .description('Start Next.js dev server locally (recommended over Docker)')
    .option('--port <port>', 'Port to run on', '1989')
    .option('--clean', 'Remove .next cache before starting')
    .action(async (opts: { port: string; clean?: boolean }) => {
      const root = getProjectRoot();
      const webDir = resolve(root, 'web');

      if (!existsSync(webDir)) {
        logger.error('web/ directory not found');
        process.exit(1);
      }

      // Check node_modules exist
      if (!existsSync(resolve(webDir, 'node_modules'))) {
        logger.step('Installing dependencies...');
        const install = spawn('npm', ['install'], {
          cwd: webDir,
          stdio: 'inherit',
        });
        await new Promise<void>((res, rej) => {
          install.on('close', (code) => (code === 0 ? res() : rej(new Error('npm install failed'))));
          install.on('error', rej);
        });
      }

      // Clean .next cache if requested or if it looks stale
      const nextDir = resolve(webDir, '.next');
      if (opts.clean && existsSync(nextDir)) {
        logger.step('Cleaning .next cache...');
        rmSync(nextDir, { recursive: true, force: true });
      }

      logger.header('Josi Web (local dev)');
      logger.blank();
      logger.dim(`  URL:   http://localhost:${opts.port}`);
      logger.dim('  API:   http://localhost:1954 (must be running via josi redock up)');
      logger.blank();

      // Kill any existing process on the target port
      try {
        const pids = execFileSync('lsof', [`-ti:${opts.port}`], { encoding: 'utf8' }).trim();
        if (pids) {
          for (const pid of pids.split('\n')) {
            try { process.kill(Number(pid), 'SIGKILL'); } catch { /* already dead */ }
          }
          logger.dim(`  Killed existing process on port ${opts.port}`);
        }
      } catch { /* no process on port — fine */ }

      // Start Next.js dev server
      const child = spawn('npx', ['next', 'dev', '-p', opts.port], {
        cwd: webDir,
        stdio: 'inherit',
        env: { ...process.env, NODE_OPTIONS: '--max-old-space-size=4096' },
      });

      child.on('error', (err) => {
        logger.error(`Failed to start: ${err.message}`);
        process.exit(1);
      });

      child.on('close', (code) => {
        process.exit(code ?? 0);
      });

      // Forward SIGINT/SIGTERM to child
      const cleanup = () => {
        child.kill('SIGTERM');
      };
      process.on('SIGINT', cleanup);
      process.on('SIGTERM', cleanup);
    });
}
