import { spawnSync, spawn, type SpawnOptions } from 'node:child_process';

export interface ExecResult {
  code: number;
}

export function exec(
  args: string[],
  opts?: { cwd?: string; silent?: boolean; env?: Record<string, string> },
): Promise<ExecResult> {
  return new Promise((resolve, reject) => {
    const spawnOpts: SpawnOptions = {
      cwd: opts?.cwd,
      stdio: opts?.silent ? ['ignore', 'pipe', 'pipe'] : 'inherit',
      env: opts?.env ? { ...process.env, ...opts.env } : undefined,
    };

    const child = spawn('docker', ['compose', ...args], spawnOpts);

    child.on('error', (err) => {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        reject(new Error('docker not found. Is Docker installed and in your PATH?'));
      } else {
        reject(err);
      }
    });

    child.on('close', (code) => {
      resolve({ code: code ?? 1 });
    });
  });
}

export function containerExec(
  composeArgs: string[],
  container: string,
  command: string[],
  opts?: { cwd?: string },
): Promise<ExecResult> {
  return exec([...composeArgs, 'exec', container, ...command], opts);
}

export function isDockerRunning(): boolean {
  const result = spawnSync('docker', ['info'], { stdio: 'pipe' });
  return result.status === 0;
}
