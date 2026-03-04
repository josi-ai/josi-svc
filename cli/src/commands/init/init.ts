import type { Command } from 'commander';
import { platform } from 'os';
import * as logger from '../../lib/logger.js';
import { REQUIRED_TOOLS, checkTool, installTool, checkHomebrew, installHomebrew } from '../../lib/tools.js';
import { confirmAction } from '../../lib/prompt.js';

export function register(parent: Command): void {
  parent
    .command('init')
    .description('Bootstrap your development machine with all required tools')
    .addHelpText(
      'after',
      `
Examples:
  $ josi init          # Interactive setup wizard`
    )
    .action(async () => {
      logger.header('Josi Development Setup');

      const isMac = platform() === 'darwin';
      const isLinux = platform() === 'linux';

      if (!isMac && !isLinux) {
        logger.error('This setup supports macOS and Linux only.');
        logger.dim('For Windows, use WSL2 and re-run this command.');
        process.exit(1);
      }

      // Step 1: Package manager
      if (isMac) {
        logger.info('Checking Homebrew...');
        if (checkHomebrew()) {
          logger.pass('Homebrew');
        } else {
          const install = await confirmAction('Homebrew not found. Install it?');
          if (install) {
            if (!installHomebrew()) {
              logger.error('Failed to install Homebrew.');
              process.exit(1);
            }
            logger.success('Homebrew installed.');
          } else {
            logger.warn('Skipping Homebrew. Some tools may fail to install.');
          }
        }
      }

      // Step 2: Required tools
      logger.blank();
      logger.info('Checking required tools...');
      logger.blank();

      const missing: typeof REQUIRED_TOOLS = [];

      for (const tool of REQUIRED_TOOLS) {
        const { installed, version } = checkTool(tool);
        if (installed) {
          logger.pass(tool.name, version);
        } else {
          logger.fail(tool.name, 'not found');
          missing.push(tool);
        }
      }

      if (missing.length > 0) {
        logger.blank();
        const install = await confirmAction(
          `Install ${missing.length} missing tool(s)?`
        );
        if (install) {
          for (const tool of missing) {
            if (installTool(tool)) {
              logger.success(`${tool.name} installed.`);
            } else {
              logger.error(`Failed to install ${tool.name}.`);
            }
          }
        }
      }

      // Step 3: Poetry dependencies
      logger.blank();
      logger.info('Checking Poetry dependencies...');
      const poetryCheck = checkTool({
        name: 'Poetry',
        command: 'poetry',
        versionFlag: '--version',
        required: true,
      });
      if (poetryCheck.installed) {
        logger.dim('Run "poetry install" in the project root to install Python dependencies.');
      }

      // Step 4: Env file
      logger.blank();
      logger.info('Checking .env file...');
      const { existsSync, copyFileSync } = await import('fs');
      const { resolve } = await import('path');
      const { getProjectRoot } = await import('../../lib/detect.js');

      try {
        const root = getProjectRoot();
        const envPath = resolve(root, '.env');
        const examplePath = resolve(root, '.env.example');
        if (existsSync(envPath)) {
          logger.pass('.env file exists');
        } else if (existsSync(examplePath)) {
          copyFileSync(examplePath, envPath);
          logger.success('Created .env from .env.example');
          logger.dim('Edit .env to configure your environment variables.');
        } else {
          logger.warn('No .env.example found. Create .env manually.');
        }
      } catch {
        logger.dim('Run this command from the josi-svc directory to check .env.');
      }

      logger.blank();
      logger.success('Setup complete! Run "josi doctor" to verify everything works.');
      logger.blank();
    });
}
