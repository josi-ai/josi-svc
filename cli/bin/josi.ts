#!/usr/bin/env node

import { Command } from 'commander';

// Init commands
import { register as registerInit } from '../src/commands/init/init.js';
import { register as registerDoctor } from '../src/commands/init/doctor.js';

// Command groups
import { register as registerRedock } from '../src/commands/redock/index.js';
import { register as registerWeb } from '../src/commands/web/index.js';
import { register as registerDb } from '../src/commands/db/index.js';
import { register as registerSecrets } from '../src/commands/secrets/index.js';
import { register as registerGcp } from '../src/commands/gcp/index.js';

// Standalone commands
import { register as registerTest } from '../src/commands/test.js';
import { register as registerLint } from '../src/commands/lint.js';
import { register as registerCrud } from '../src/commands/crud.js';
import { register as registerOpen } from '../src/commands/open.js';
import { register as registerStatus } from '../src/commands/status.js';
import { register as registerNuke } from '../src/commands/nuke.js';
import { register as registerUpdate } from '../src/commands/update.js';
import { register as registerServices } from '../src/commands/services.js';
import { register as registerEnv } from '../src/commands/env.js';

const program = new Command();

program
  .name('josi')
  .description('Developer CLI for the Josi astrology platform')
  .version('1.0.0');

// Register all commands
registerInit(program);
registerDoctor(program);
registerRedock(program);
registerWeb(program);
registerDb(program);
registerTest(program);
registerLint(program);
registerCrud(program);
registerOpen(program);
registerStatus(program);
registerNuke(program);
registerUpdate(program);
registerServices(program);
registerEnv(program);
registerSecrets(program);
registerGcp(program);

program.parse();
