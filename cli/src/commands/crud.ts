import type { Command } from 'commander';
import { spawnSync } from 'child_process';
import * as logger from '../lib/logger.js';
import { getProjectRoot } from '../lib/detect.js';

export function register(program: Command): void {
  program
    .command('crud <model>')
    .description('Generate CRUD scaffolding for a SQLModel class')
    .requiredOption('-m, --module <name>', 'Module name for generated files')
    .addHelpText(
      'after',
      `
Arguments:
  model    Fully qualified model path (e.g., josi.models.person_model.Person)

Examples:
  $ josi crud josi.models.person_model.Person --module person
  $ josi crud josi.models.chart_model.Chart --module chart`
    )
    .action((model: string, opts: { module: string }) => {
      logger.header('Generate CRUD');
      const root = getProjectRoot();

      logger.step(`Generating CRUD for ${model} (module: ${opts.module})`);
      logger.blank();

      const result = spawnSync(
        'poetry',
        ['run', 'generate-crud', model, '--module', opts.module],
        { cwd: root, stdio: 'inherit' }
      );

      logger.blank();
      if (result.status === 0) {
        logger.success('CRUD scaffolding generated!');
        logger.blank();
        logger.dim('Next steps:');
        logger.dim(`  1. Add router to src/josi/api/v1/__init__.py`);
        logger.dim(`  2. Update GraphQL schema in src/josi/graphql/router.py`);
        logger.dim(`  3. Generate migration: josi db migrate "Add ${opts.module}"`);
        logger.dim(`  4. Apply migration: josi db upgrade`);
      } else {
        logger.error('CRUD generation failed.');
        process.exit(1);
      }
      logger.blank();
    });
}
