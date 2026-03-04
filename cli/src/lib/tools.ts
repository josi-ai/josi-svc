import { spawnSync } from 'child_process';
import { platform } from 'os';
import type { Tool } from '../types.js';
import * as logger from './logger.js';

export const REQUIRED_TOOLS: Tool[] = [
  {
    name: 'Docker',
    command: 'docker',
    versionFlag: '--version',
    installMac: 'brew install --cask docker',
    installLinux: 'sudo apt-get install -y docker.io',
    required: true,
  },
  {
    name: 'Docker Compose',
    command: 'docker',
    versionFlag: 'compose version',
    installMac: '(included with Docker Desktop)',
    installLinux: 'sudo apt-get install -y docker-compose-plugin',
    required: true,
  },
  {
    name: 'Python 3.12+',
    command: 'python3',
    versionFlag: '--version',
    installMac: 'brew install python@3.12',
    installLinux: 'sudo apt-get install -y python3.12',
    required: true,
  },
  {
    name: 'Poetry',
    command: 'poetry',
    versionFlag: '--version',
    installMac: 'curl -sSL https://install.python-poetry.org | python3 -',
    installLinux: 'curl -sSL https://install.python-poetry.org | python3 -',
    required: true,
  },
  {
    name: 'Git',
    command: 'git',
    versionFlag: '--version',
    installMac: 'brew install git',
    installLinux: 'sudo apt-get install -y git',
    required: true,
  },
  {
    name: 'Node.js',
    command: 'node',
    versionFlag: '--version',
    installMac: 'brew install node',
    installLinux: 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs',
    required: true,
  },
  {
    name: 'PostgreSQL Client',
    command: 'psql',
    versionFlag: '--version',
    installMac: 'brew install libpq && brew link --force libpq',
    installLinux: 'sudo apt-get install -y postgresql-client',
    required: false,
  },
];

export function checkTool(tool: Tool): { installed: boolean; version: string } {
  try {
    const args = tool.versionFlag.split(' ');
    const cmd = tool.command;
    const result = spawnSync(cmd, args, {
      stdio: ['ignore', 'pipe', 'pipe'],
      encoding: 'utf-8',
    });
    if (result.status === 0) {
      const version = (result.stdout ?? '').trim().split('\n')[0];
      return { installed: true, version };
    }
  } catch {
    // tool not found
  }
  return { installed: false, version: '' };
}

export function installTool(tool: Tool): boolean {
  const isMac = platform() === 'darwin';
  const cmd = isMac ? tool.installMac : tool.installLinux;
  if (!cmd) {
    logger.error(`No install command for ${tool.name} on this platform.`);
    return false;
  }
  logger.step(`Installing ${tool.name}: ${cmd}`);
  const result = spawnSync('sh', ['-c', cmd], { stdio: 'inherit' });
  return result.status === 0;
}

export function checkHomebrew(): boolean {
  const result = spawnSync('brew', ['--version'], { stdio: 'pipe' });
  return result.status === 0;
}

export function installHomebrew(): boolean {
  logger.step('Installing Homebrew...');
  const result = spawnSync(
    'sh',
    ['-c', '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'],
    { stdio: 'inherit' }
  );
  return result.status === 0;
}
