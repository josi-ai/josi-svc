import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../lib/logger.js';
import { getProjectRoot } from '../lib/detect.js';

export function register(program: Command): void {
  program
    .command('test')
    .description('Run the test suite with pytest')
    .option('-u, --unit', 'Run unit tests only')
    .option('-i, --integration', 'Run integration tests only')
    .option('-c, --coverage', 'Run with coverage report')
    .option('-k, --filter <pattern>', 'Filter tests by keyword')
    .option('-v, --verbose', 'Verbose output')
    .addHelpText(
      'after',
      `
Examples:
  $ josi test                       # Run all tests
  $ josi test --unit                # Unit tests only
  $ josi test --integration         # Integration tests only
  $ josi test --coverage            # With HTML coverage report
  $ josi test -k "test_vedic"       # Filter by keyword
  $ josi test -v                    # Verbose output`
    )
    .action(
      (opts: {
        unit?: boolean;
        integration?: boolean;
        coverage?: boolean;
        filter?: string;
        verbose?: boolean;
      }) => {
        logger.header('Running Tests');
        const root = getProjectRoot();

        const args = ['run', 'pytest'];

        if (opts.unit) {
          args.push('tests/unit');
          logger.info('Running unit tests...');
        } else if (opts.integration) {
          args.push('tests/integration');
          logger.info('Running integration tests...');
        } else {
          logger.info('Running all tests...');
        }

        if (opts.coverage) {
          args.push('--cov=josi', '--cov-report=html', '--cov-report=term');
        }

        if (opts.filter) {
          args.push('-k', opts.filter);
          logger.info(`Filter: "${opts.filter}"`);
        }

        if (opts.verbose) {
          args.push('-v');
        }

        logger.blank();

        const result = spawnSync('poetry', args, {
          cwd: root,
          stdio: 'inherit',
        });

        logger.blank();
        if (result.status === 0) {
          logger.success('All tests passed!');
          if (opts.coverage) {
            logger.dim('Coverage report: coverage/index.html');
          }
        } else {
          logger.error(`Tests failed with exit code ${result.status}`);
          process.exit(result.status ?? 1);
        }
        logger.blank();
      }
    );
}
