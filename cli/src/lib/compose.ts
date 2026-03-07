import type { Env, Mode, ComposeConfig } from '../types.js';

export function buildComposeConfig(env: Env, mode: Mode): ComposeConfig {
  const files = ['docker-compose.yml'];
  const profiles: string[] = [];

  if (mode === 'cloud') {
    files.push(`docker-compose.${env}.yml`);
    profiles.push('cloud');
  } else {
    files.push('docker-compose.local.yml');
    profiles.push('local');
  }

  return { files, profiles };
}

export function composeFileArgs(files: string[]): string[] {
  return files.flatMap((f) => ['-f', f]);
}

export function composeProfileArgs(profiles: string[]): string[] {
  return profiles.flatMap((p) => ['--profile', p]);
}

export function allComposeArgs(): string[] {
  return ['--profile', 'cloud', '--profile', 'local'];
}
