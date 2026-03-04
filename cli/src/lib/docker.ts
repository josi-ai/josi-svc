import { spawnSync, SpawnSyncReturns } from 'child_process';
import * as logger from './logger.js';

export interface ExecOptions {
  cwd: string;
  env?: Record<string, string>;
  stdio?: 'inherit' | 'pipe';
}

export function composeExec(
  args: string[],
  opts: ExecOptions
): SpawnSyncReturns<Buffer> {
  return spawnSync('docker', ['compose', ...args], {
    cwd: opts.cwd,
    stdio: opts.stdio ?? 'inherit',
    env: { ...process.env, ...opts.env },
  });
}

export function composeUp(cwd: string, build = true): void {
  const args = ['up', '-d'];
  if (build) args.push('--build');
  const result = composeExec(args, { cwd });
  if (result.status !== 0) {
    logger.error('Failed to start services.');
    process.exit(1);
  }
}

export function composeDown(cwd: string, volumes = false): void {
  const args = ['down'];
  if (volumes) args.push('-v', '--remove-orphans');
  composeExec(args, { cwd });
}

export function composeLogs(cwd: string, service?: string, follow = true): void {
  const args = ['logs'];
  if (follow) args.push('-f');
  if (service) args.push(service);
  composeExec(args, { cwd });
}

export function composePs(cwd: string): SpawnSyncReturns<Buffer> {
  return composeExec(['ps', '--format', 'table'], { cwd });
}

export function containerExec(
  cwd: string,
  service: string,
  command: string[]
): SpawnSyncReturns<Buffer> {
  return composeExec(['exec', service, ...command], { cwd });
}

export function isDockerRunning(): boolean {
  const result = spawnSync('docker', ['info'], { stdio: 'pipe' });
  return result.status === 0;
}
