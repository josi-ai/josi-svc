const isTTY = process.stdout.isTTY && !process.env.NO_COLOR;

const colors = {
  reset: isTTY ? '\x1b[0m' : '',
  bold: isTTY ? '\x1b[1m' : '',
  dim: isTTY ? '\x1b[2m' : '',
  red: isTTY ? '\x1b[31m' : '',
  green: isTTY ? '\x1b[32m' : '',
  yellow: isTTY ? '\x1b[33m' : '',
  blue: isTTY ? '\x1b[34m' : '',
  magenta: isTTY ? '\x1b[35m' : '',
  cyan: isTTY ? '\x1b[36m' : '',
  gray: isTTY ? '\x1b[90m' : '',
};

export function header(text: string): void {
  console.log(`\n${colors.bold}${colors.cyan}▸ ${text}${colors.reset}\n`);
}

export function info(text: string): void {
  console.log(`  ${colors.blue}ℹ${colors.reset} ${text}`);
}

export function success(text: string): void {
  console.log(`  ${colors.green}✓${colors.reset} ${text}`);
}

export function warn(text: string): void {
  console.log(`  ${colors.yellow}⚠${colors.reset} ${text}`);
}

export function error(text: string): void {
  console.log(`  ${colors.red}✗${colors.reset} ${text}`);
}

export function pass(label: string, detail?: string): void {
  const d = detail ? ` ${colors.dim}${detail}${colors.reset}` : '';
  console.log(`  ${colors.green}✓${colors.reset} ${label}${d}`);
}

export function fail(label: string, detail?: string): void {
  const d = detail ? ` ${colors.dim}${detail}${colors.reset}` : '';
  console.log(`  ${colors.red}✗${colors.reset} ${label}${d}`);
}

export function dim(text: string): void {
  console.log(`  ${colors.dim}${text}${colors.reset}`);
}

export function step(text: string): void {
  console.log(`  ${colors.magenta}→${colors.reset} ${text}`);
}

export function blank(): void {
  console.log();
}
