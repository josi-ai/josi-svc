import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../lib/logger.js';
import { getProjectRoot } from '../lib/detect.js';
import { exec, isDockerRunning } from '../lib/docker.js';

export function register(program: Command): void {
  const test = program
    .command('test')
    .description('Test suite management');

  test
    .command('run')
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
  $ josi test run                       # Run all tests
  $ josi test run --unit                # Unit tests only
  $ josi test run --integration         # Integration tests only
  $ josi test run --coverage            # With HTML coverage report
  $ josi test run -k "test_vedic"       # Filter by keyword
  $ josi test run -v                    # Verbose output`
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

  test
    .command('db-up')
    .description('Start the test database (pgvector on tmpfs)')
    .action(async () => {
      logger.header('Starting Test Database');

      if (!isDockerRunning()) {
        logger.error('Docker is not running. Start Docker Desktop first.');
        process.exit(1);
      }

      const root = getProjectRoot();
      logger.step('Starting test database...');

      const result = await exec(['--profile', 'test', 'up', '-d', 'db-test'], { cwd: root });

      if (result.code !== 0) {
        logger.error('Failed to start test database.');
        process.exit(1);
      }

      logger.blank();
      logger.success('Test database started!');
      logger.dim('  PostgreSQL: localhost:1962');
      logger.dim('  Database:   josi_test');
      logger.dim('  User:       josi / josi');
      logger.blank();
    });

  test
    .command('db-down')
    .description('Stop the test database')
    .action(async () => {
      logger.header('Stopping Test Database');
      const root = getProjectRoot();

      await exec(['--profile', 'test', 'down'], { cwd: root });

      logger.blank();
      logger.success('Test database stopped.');
      logger.blank();
    });

  // Default action: run all tests (backward compatible with `josi test`)
  test.action(() => {
    logger.header('Running Tests');
    const root = getProjectRoot();

    const result = spawnSync('poetry', ['run', 'pytest'], {
      cwd: root,
      stdio: 'inherit',
    });

    logger.blank();
    if (result.status === 0) {
      logger.success('All tests passed!');
    } else {
      logger.error(`Tests failed with exit code ${result.status}`);
      process.exit(result.status ?? 1);
    }
    logger.blank();
  });
}
