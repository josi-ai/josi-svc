import type { Command } from 'commander';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { getProjectRoot } from '../../lib/detect.js';
import { exec } from '../../lib/docker.js';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('check')
    .description('Validate Docker and project setup')
    .addHelpText(
      'after',
      `
Validates:
  - docker-compose.yml exists and parses correctly
  - Environment overlay files exist
  - Dockerfile exists
  - Python version in Dockerfile matches pyproject.toml
  - Required project files exist (src/, pyproject.toml, poetry.lock)
  - Alembic config is present
  - Docker Compose config merges correctly

Examples:
  $ josi redock check`
    )
    .action(async () => {
      const root = getProjectRoot();
      let issues = 0;

      logger.header('Redock Setup Check');

      // --- Docker Compose ---
      logger.info('Docker Compose files');

      if (existsSync(resolve(root, 'docker-compose.yml'))) {
        logger.pass('docker-compose.yml exists');
      } else {
        logger.fail('docker-compose.yml is missing');
        issues++;
      }

      const envFiles = ['docker-compose.dev.yml', 'docker-compose.prod.yml', 'docker-compose.local.yml'];
      for (const file of envFiles) {
        if (existsSync(resolve(root, file))) {
          logger.pass(`${file} exists`);
        } else {
          logger.fail(`${file} is missing`);
          issues++;
        }
      }

      // --- Dockerfile ---
      logger.blank();
      logger.info('Dockerfile');

      const dockerfile = resolve(root, 'Dockerfile');
      if (existsSync(dockerfile)) {
        logger.pass('Dockerfile exists');

        const content = readFileSync(dockerfile, 'utf-8');
        const pythonMatch = content.match(/^FROM python:(\d+\.\d+)/m);

        if (pythonMatch) {
          const dockerPython = pythonMatch[1];
          logger.pass(`Dockerfile Python version: ${dockerPython}`);

          const pyprojectPath = resolve(root, 'pyproject.toml');
          if (existsSync(pyprojectPath)) {
            const pyproject = readFileSync(pyprojectPath, 'utf-8');
            const pyMatch = pyproject.match(/python\s*=\s*"[\^~>=<]*(\d+\.\d+)/m);

            if (pyMatch) {
              const pyprojectPython = pyMatch[1];
              if (dockerPython === pyprojectPython) {
                logger.pass('Python versions match');
              } else {
                logger.fail(
                  `Python version mismatch: Dockerfile=${dockerPython}, pyproject.toml=${pyprojectPython}`
                );
                issues++;
              }
            }
          }
        }
      } else {
        logger.fail('Dockerfile is missing');
        issues++;
      }

      // --- Docker Compose Validation ---
      logger.blank();
      logger.info('Docker Compose validation');

      if (existsSync(resolve(root, 'docker-compose.yml'))) {
        const result = await exec(['config', '--services'], {
          cwd: root,
          silent: true,
        });
        if (result.code === 0) {
          logger.pass('docker-compose.yml parses correctly');
        } else {
          logger.fail('docker-compose.yml has errors');
          logger.dim('  Run: docker compose config');
          issues++;
        }
      }

      // --- Project Files ---
      logger.blank();
      logger.info('Project files');

      const requiredFiles: Array<{ path: string; label: string; required: boolean }> = [
        { path: 'src/josi', label: 'src/josi/', required: true },
        { path: 'pyproject.toml', label: 'pyproject.toml', required: true },
        { path: 'poetry.lock', label: 'poetry.lock', required: false },
        { path: 'alembic.ini', label: 'alembic.ini', required: true },
        { path: 'src/alembic', label: 'src/alembic/', required: true },
        { path: '.env', label: '.env', required: false },
        { path: '.env.example', label: '.env.example', required: true },
      ];

      for (const file of requiredFiles) {
        if (existsSync(resolve(root, file.path))) {
          logger.pass(`${file.label} exists`);
        } else if (file.required) {
          logger.fail(`${file.label} is missing`);
          issues++;
        } else {
          logger.warn(`${file.label} is missing`);
        }
      }

      // --- Entrypoint ---
      const entrypoint = resolve(root, 'entrypoint.sh');
      if (existsSync(entrypoint)) {
        logger.pass('entrypoint.sh exists');
        try {
          const stats = statSync(entrypoint);
          if (stats.mode & 0o111) {
            logger.pass('entrypoint.sh is executable');
          } else {
            logger.warn('entrypoint.sh is not executable (chmod +x entrypoint.sh)');
          }
        } catch {
          // ignore
        }
      }

      // --- Summary ---
      logger.blank();
      if (issues === 0) {
        logger.success('All checks passed!');
      } else {
        logger.error(`Found ${issues} issue(s) that need fixing.`);
        process.exit(1);
      }
      logger.blank();
    });
}
