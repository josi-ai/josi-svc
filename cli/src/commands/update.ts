import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import * as logger from '../lib/logger.js';

export function register(program: Command): void {
  program
    .command('update')
    .description('Update the josi CLI to the latest version')
    .action(() => {
      logger.header('Updating Josi CLI');

      // Resolve CLI directory (dist/bin/josi.js -> cli/)
      const __filename = fileURLToPath(import.meta.url);
      const cliDir = resolve(dirname(__filename), '..', '..');

      logger.step('Pulling latest changes...');
      const pullResult = spawnSync('git', ['pull', '--rebase'], {
        cwd: resolve(cliDir, '..'),
        stdio: 'inherit',
      });
      if (pullResult.status !== 0) {
        logger.error('Git pull failed.');
        process.exit(1);
      }

      logger.step('Installing dependencies...');
      const installResult = spawnSync('npm', ['install'], {
        cwd: cliDir,
        stdio: 'inherit',
      });
      if (installResult.status !== 0) {
        logger.error('npm install failed.');
        process.exit(1);
      }

      logger.step('Building...');
      const buildResult = spawnSync('npm', ['run', 'build'], {
        cwd: cliDir,
        stdio: 'inherit',
      });
      if (buildResult.status !== 0) {
        logger.error('Build failed.');
        process.exit(1);
      }

      logger.blank();
      logger.success('Josi CLI updated to latest version!');
      logger.blank();
    });
}
