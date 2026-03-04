import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../lib/logger.js';
import { getProjectRoot } from '../lib/detect.js';

export function register(program: Command): void {
  program
    .command('lint')
    .description('Run code quality checks (black, flake8, mypy)')
    .option('--fix', 'Auto-format with black (instead of check-only)')
    .option('--black-only', 'Only run black')
    .option('--flake8-only', 'Only run flake8')
    .option('--mypy-only', 'Only run mypy')
    .addHelpText(
      'after',
      `
Examples:
  $ josi lint              # Check all (black --check, flake8, mypy)
  $ josi lint --fix        # Auto-format with black, then check
  $ josi lint --mypy-only  # Only run type checking`
    )
    .action(
      (opts: {
        fix?: boolean;
        blackOnly?: boolean;
        flake8Only?: boolean;
        mypyOnly?: boolean;
      }) => {
        logger.header('Code Quality Checks');
        const root = getProjectRoot();
        let allPassed = true;

        const runAll = !opts.blackOnly && !opts.flake8Only && !opts.mypyOnly;

        // Black
        if (runAll || opts.blackOnly) {
          const blackArgs = opts.fix
            ? ['run', 'black', 'src/']
            : ['run', 'black', '--check', 'src/'];
          logger.step(opts.fix ? 'Formatting with black...' : 'Checking black...');
          const result = spawnSync('poetry', blackArgs, {
            cwd: root,
            stdio: 'inherit',
          });
          if (result.status === 0) {
            logger.pass('black');
          } else {
            logger.fail('black', opts.fix ? 'formatting errors' : 'run "josi lint --fix" to auto-format');
            allPassed = false;
          }
        }

        // Flake8
        if (runAll || opts.flake8Only) {
          logger.step('Checking flake8...');
          const result = spawnSync('poetry', ['run', 'flake8', 'src/'], {
            cwd: root,
            stdio: 'inherit',
          });
          if (result.status === 0) {
            logger.pass('flake8');
          } else {
            logger.fail('flake8');
            allPassed = false;
          }
        }

        // Mypy
        if (runAll || opts.mypyOnly) {
          logger.step('Type checking with mypy...');
          const result = spawnSync('poetry', ['run', 'mypy', 'src/'], {
            cwd: root,
            stdio: 'inherit',
          });
          if (result.status === 0) {
            logger.pass('mypy');
          } else {
            logger.fail('mypy');
            allPassed = false;
          }
        }

        logger.blank();
        if (allPassed) {
          logger.success('All checks passed!');
        } else {
          logger.error('Some checks failed. Fix the issues above.');
          process.exit(1);
        }
        logger.blank();
      }
    );
}
