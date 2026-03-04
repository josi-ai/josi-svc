import type { Command } from 'commander';
import { existsSync, readFileSync, copyFileSync } from 'fs';
import { resolve } from 'path';
import * as logger from '../lib/logger.js';
import { getProjectRoot } from '../lib/detect.js';

export function register(program: Command): void {
  const env = program
    .command('env')
    .description('Manage environment configuration');

  env
    .command('check')
    .description('Validate .env file has all required variables')
    .action(() => {
      logger.header('Environment Check');
      const root = getProjectRoot();
      const envPath = resolve(root, '.env');
      const examplePath = resolve(root, '.env.example');

      if (!existsSync(envPath)) {
        logger.error('.env file not found. Run "josi env setup" to create one.');
        process.exit(1);
      }

      if (!existsSync(examplePath)) {
        logger.warn('.env.example not found. Cannot validate variables.');
        return;
      }

      const envContent = readFileSync(envPath, 'utf-8');
      const exampleContent = readFileSync(examplePath, 'utf-8');

      const parseKeys = (content: string): Set<string> => {
        const keys = new Set<string>();
        for (const line of content.split('\n')) {
          const trimmed = line.trim();
          if (trimmed && !trimmed.startsWith('#')) {
            const match = trimmed.match(/^([A-Z_][A-Z0-9_]*)=/);
            if (match) keys.add(match[1]);
          }
        }
        return keys;
      };

      const envKeys = parseKeys(envContent);
      const exampleKeys = parseKeys(exampleContent);

      const missing = [...exampleKeys].filter((k) => !envKeys.has(k));
      const extra = [...envKeys].filter((k) => !exampleKeys.has(k));

      if (missing.length === 0) {
        logger.pass('All required variables present');
      } else {
        logger.fail(`Missing ${missing.length} variable(s):`);
        for (const key of missing) {
          logger.dim(`  - ${key}`);
        }
      }

      if (extra.length > 0) {
        logger.blank();
        logger.info(`${extra.length} extra variable(s) not in .env.example:`);
        for (const key of extra) {
          logger.dim(`  + ${key}`);
        }
      }

      logger.blank();
    });

  env
    .command('setup')
    .description('Create .env from .env.example')
    .action(() => {
      logger.header('Environment Setup');
      const root = getProjectRoot();
      const envPath = resolve(root, '.env');
      const examplePath = resolve(root, '.env.example');

      if (existsSync(envPath)) {
        logger.warn('.env already exists. Delete it first to recreate.');
        return;
      }

      if (!existsSync(examplePath)) {
        logger.error('.env.example not found.');
        process.exit(1);
      }

      copyFileSync(examplePath, envPath);
      logger.success('Created .env from .env.example');
      logger.dim('Edit .env to configure your environment variables.');
      logger.blank();
    });
}
