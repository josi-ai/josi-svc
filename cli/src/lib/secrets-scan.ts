import { spawn } from 'node:child_process';

export interface SecretPattern {
  name: string;
  pattern: RegExp;
}

export const SECRET_PATTERNS: SecretPattern[] = [
  { name: 'DB password', pattern: /(?:DB_PASS(?:WORD)?|POSTGRES_PASSWORD|MYSQL_PASSWORD|DATABASE_PASSWORD)\s*[:=]\s*['"]?(?![\s'"${\}])[^\s'"]+/i },
  { name: 'Database URL with credentials', pattern: /(?:postgres|mysql|mongodb|redis):\/\/[^:\s]+:[^@\s]+@/i },
  { name: 'API key', pattern: /(?:API_KEY|APIKEY|api_key)\s*[:=]\s*['"]?(?![\s'"${\}])[A-Za-z0-9_\-]{20,}/i },
  { name: 'Auth token', pattern: /(?:AUTH_TOKEN|ACCESS_TOKEN|SECRET_TOKEN|BEARER_TOKEN)\s*[:=]\s*['"]?(?![\s'"${\}])[A-Za-z0-9_\-\.]{20,}/i },
  { name: 'Secret key', pattern: /(?:SECRET_KEY|APP_SECRET|JWT_SECRET|ENCRYPTION_KEY)\s*[:=]\s*['"]?(?![\s'"${\}])[A-Za-z0-9_\-\.]{16,}/i },
  { name: 'Stripe secret key', pattern: /sk_(?:live|test)_[A-Za-z0-9]{20,}/ },
  { name: 'Stripe publishable key', pattern: /pk_(?:live|test)_[A-Za-z0-9]{20,}/ },
  { name: 'OpenAI API key', pattern: /sk-[A-Za-z0-9]{20,}/ },
  { name: 'Anthropic API key', pattern: /sk-ant-[A-Za-z0-9_\-]{20,}/ },
  { name: 'Private key', pattern: /-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----/ },
  { name: 'Password assignment', pattern: /(?:_PASSWORD|_PASSWD|_PWD)\s*[:=]\s*['"]?(?![\s'"${\}])[^\s'"]{8,}/i },
  { name: 'Connection string', pattern: /(?:CONNECTION_STRING|CONN_STR)\s*[:=]\s*['"]?(?![\s'"${\}])[^\s'"]+/i },
  { name: 'SendGrid API key', pattern: /SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}/ },
  { name: 'Twilio auth token', pattern: /(?:TWILIO_AUTH_TOKEN)\s*[:=]\s*['"]?[a-f0-9]{32}/i },
  { name: 'Base64 secret', pattern: /(?:SECRET|KEY|TOKEN|CREDENTIAL|PASSWORD).*[:=]\s*['"]?[A-Za-z0-9+\/]{40,}={0,2}['"]?/i },
];

export const SENSITIVE_FILE_PATTERNS = [
  'docker-compose*.yml',
  'docker-compose*.yaml',
  '.env',
  '.env.*',
  '*.env',
  'sa-key.json',
  '**/sa-key.json',
];

export interface ScanMatch {
  file: string;
  commit: string;
  commitDate: string;
  author: string;
  patternName: string;
  line: string;
  stillPresent: boolean;
}

export function scanHistory(
  cwd: string,
  filePatterns: string[],
  onProgress?: (commit: string) => void,
): Promise<ScanMatch[]> {
  return new Promise((resolve, reject) => {
    const args = [
      'log', '--all', '--diff-filter=ACMR',
      '--format=%H||%aI||%an', '-p', '--', ...filePatterns,
    ];
    const child = spawn('git', args, { cwd, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    child.stdout!.on('data', (data: Buffer) => { output += data.toString(); });
    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code !== 0 && output.length === 0) { resolve([]); return; }
      const matches: ScanMatch[] = [];
      const lines = output.split('\n');
      let currentCommit = '', currentDate = '', currentAuthor = '', currentFile = '';
      for (const line of lines) {
        const commitMatch = line.match(/^([a-f0-9]{40})\|\|(.+)\|\|(.+)$/);
        if (commitMatch) {
          currentCommit = commitMatch[1]; currentDate = commitMatch[2]; currentAuthor = commitMatch[3];
          if (onProgress) onProgress(currentCommit.substring(0, 8));
          continue;
        }
        const fileMatch = line.match(/^\+\+\+ b\/(.+)$/);
        if (fileMatch) { currentFile = fileMatch[1]; continue; }
        if (!line.startsWith('+') || line.startsWith('+++')) continue;
        const addedLine = line.substring(1);
        for (const pattern of SECRET_PATTERNS) {
          if (pattern.pattern.test(addedLine)) {
            matches.push({ file: currentFile, commit: currentCommit, commitDate: currentDate, author: currentAuthor, patternName: pattern.name, line: maskSecret(addedLine.trim()), stillPresent: false });
            break;
          }
        }
      }
      resolve(matches);
    });
  });
}

export function checkCurrentFile(cwd: string, filePath: string, pattern: RegExp): Promise<boolean> {
  return new Promise((resolve) => {
    const child = spawn('git', ['show', `HEAD:${filePath}`], { cwd, stdio: ['ignore', 'pipe', 'pipe'] });
    let content = '';
    child.stdout!.on('data', (data: Buffer) => { content += data.toString(); });
    child.on('close', () => { resolve(pattern.test(content)); });
  });
}

function maskSecret(line: string): string {
  return line.replace(
    /([:=]\s*['"]?)([A-Za-z0-9+\/_\-.]{12,})/g,
    (_match, prefix: string, value: string) => {
      if (value.length <= 8) return `${prefix}${'*'.repeat(value.length)}`;
      const start = value.substring(0, 4);
      const end = value.substring(value.length - 4);
      return `${prefix}${start}${'*'.repeat(value.length - 8)}${end}`;
    },
  );
}
