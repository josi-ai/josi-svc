import { existsSync } from 'fs';
import { resolve, basename } from 'path';
import * as logger from './logger.js';

export function getProjectRoot(): string {
  // Walk up from cwd looking for pyproject.toml + docker-compose.yml
  let dir = process.cwd();
  for (let i = 0; i < 10; i++) {
    if (
      existsSync(resolve(dir, 'pyproject.toml')) &&
      existsSync(resolve(dir, 'docker-compose.yml'))
    ) {
      return dir;
    }
    const parent = resolve(dir, '..');
    if (parent === dir) break;
    dir = parent;
  }

  // Fallback: check if we're inside cli/ subdirectory
  const cliParent = resolve(process.cwd(), '..');
  if (
    basename(process.cwd()) === 'cli' &&
    existsSync(resolve(cliParent, 'pyproject.toml'))
  ) {
    return cliParent;
  }

  logger.error('Not inside the josi-svc project directory.');
  logger.dim('Run this command from the josi-svc root or any subdirectory.');
  process.exit(1);
}

export function validateProjectDir(root: string): boolean {
  const required = ['pyproject.toml', 'docker-compose.yml', 'src/josi'];
  const missing = required.filter((f) => !existsSync(resolve(root, f)));
  if (missing.length > 0) {
    logger.error(`Missing project files: ${missing.join(', ')}`);
    return false;
  }
  return true;
}
