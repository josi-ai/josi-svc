import { spawnSync } from 'child_process';

export function gitExec(
  args: string[],
  cwd: string
): { stdout: string; status: number } {
  const result = spawnSync('git', args, {
    cwd,
    stdio: ['ignore', 'pipe', 'pipe'],
    encoding: 'utf-8',
  });
  return {
    stdout: (result.stdout ?? '').trim(),
    status: result.status ?? 1,
  };
}

export function getCurrentBranch(cwd: string): string {
  const { stdout } = gitExec(['rev-parse', '--abbrev-ref', 'HEAD'], cwd);
  return stdout;
}

export function getParentBranch(cwd: string): string {
  // Try to find the closest ancestor branch (main or development)
  const candidates = ['main', 'master', 'development'];
  for (const branch of candidates) {
    const { status } = gitExec(['rev-parse', '--verify', branch], cwd);
    if (status === 0) return branch;
  }
  return 'main';
}

export function hasUncommittedChanges(cwd: string): boolean {
  const { stdout } = gitExec(['status', '--porcelain'], cwd);
  return stdout.length > 0;
}

export function pullAndRebase(cwd: string): boolean {
  const branch = getCurrentBranch(cwd);
  const result = spawnSync('git', ['pull', '--rebase', 'origin', branch], {
    cwd,
    stdio: 'inherit',
  });
  return result.status === 0;
}

export function getNewMigrationFiles(
  cwd: string,
  baseBranch: string
): string[] {
  const { stdout } = gitExec(
    ['diff', '--name-only', `${baseBranch}...HEAD`, '--', 'src/alembic/versions/'],
    cwd
  );
  if (!stdout) return [];
  return stdout.split('\n').filter(Boolean);
}
