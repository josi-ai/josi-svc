import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../../lib/logger.js';
import { REQUIRED_TOOLS, checkTool } from '../../lib/tools.js';
import { isDockerRunning } from '../../lib/docker.js';
import { SERVICES } from '../../types.js';

export function register(parent: Command): void {
  parent
    .command('doctor')
    .description('Verify your development environment is set up correctly')
    .addHelpText(
      'after',
      `
Examples:
  $ josi doctor        # Run all health checks`
    )
    .action(async () => {
      logger.header('Josi Doctor');
      let allGood = true;

      // 1. Required tools
      logger.info('Tools');
      logger.blank();
      for (const tool of REQUIRED_TOOLS) {
        const { installed, version } = checkTool(tool);
        if (installed) {
          logger.pass(tool.name, version);
        } else {
          logger.fail(tool.name, tool.required ? 'REQUIRED' : 'optional');
          if (tool.required) allGood = false;
        }
      }

      // 2. Docker daemon
      logger.blank();
      logger.info('Docker Daemon');
      logger.blank();
      if (isDockerRunning()) {
        logger.pass('Docker daemon is running');
      } else {
        logger.fail('Docker daemon is not running');
        logger.dim('Start Docker Desktop or run: sudo systemctl start docker');
        allGood = false;
      }

      // 3. Port availability
      logger.blank();
      logger.info('Port Availability');
      logger.blank();
      for (const [key, svc] of Object.entries(SERVICES)) {
        const result = spawnSync('lsof', ['-i', `:${svc.port}`, '-t'], {
          stdio: 'pipe',
          encoding: 'utf-8',
        });
        const inUse = (result.stdout ?? '').trim().length > 0;
        if (inUse) {
          // Check if it's our container
          const dockerCheck = spawnSync(
            'docker',
            ['compose', 'ps', '--format', '{{.Name}}'],
            { stdio: 'pipe', encoding: 'utf-8' }
          );
          const containers = (dockerCheck.stdout ?? '').trim();
          if (containers.includes(key)) {
            logger.pass(`Port ${svc.port} (${svc.name})`, 'josi container');
          } else {
            logger.warn(`Port ${svc.port} (${svc.name}) in use by another process`);
          }
        } else {
          logger.pass(`Port ${svc.port} (${svc.name})`, 'available');
        }
      }

      // 4. Project files
      logger.blank();
      logger.info('Project Files');
      logger.blank();
      try {
        const { getProjectRoot, validateProjectDir } = await import(
          '../../lib/detect.js'
        );
        const root = getProjectRoot();
        if (validateProjectDir(root)) {
          logger.pass('Project structure valid');
        } else {
          allGood = false;
        }

        // Check .env
        const { existsSync } = await import('fs');
        const { resolve } = await import('path');
        if (existsSync(resolve(root, '.env'))) {
          logger.pass('.env file');
        } else {
          logger.warn('.env file missing — run "josi env setup"');
        }

        // Check poetry venv
        const poetryResult = spawnSync('poetry', ['env', 'info', '--path'], {
          cwd: root,
          stdio: 'pipe',
          encoding: 'utf-8',
        });
        if (poetryResult.status === 0) {
          logger.pass('Poetry virtualenv', (poetryResult.stdout ?? '').trim());
        } else {
          logger.warn('No Poetry virtualenv — run "poetry install"');
        }
      } catch {
        logger.warn('Not inside josi-svc — skipping project checks');
      }

      // Summary
      logger.blank();
      if (allGood) {
        logger.success('All checks passed! You\'re ready to develop.');
      } else {
        logger.error(
          'Some checks failed. Fix the issues above and re-run "josi doctor".'
        );
      }
      logger.blank();
    });
}
