import type { Command } from 'commander';
import {
  scanHistory,
  checkCurrentFile,
  SENSITIVE_FILE_PATTERNS,
  SECRET_PATTERNS,
  type ScanMatch,
} from '../../lib/secrets-scan.js';
import { getProjectRoot } from '../../lib/detect.js';
import * as logger from '../../lib/logger.js';

export function register(program: Command): void {
  program
    .command('scan')
    .description('Scan git history for secrets in sensitive files')
    .option('--all-files', 'Scan all files, not just sensitive file patterns')
    .addHelpText(
      'after',
      `
Scans for: API keys (Stripe, OpenAI, Anthropic), private keys,
  database URLs, JWT secrets, passwords, and other sensitive patterns.

Reports: Active secrets (still in files) and historical secrets (removed
  but still in git history).

Examples:
  $ josi secrets scan              # Scan sensitive files only
  $ josi secrets scan --all-files  # Scan all files in history`
    )
    .action(async (opts: { allFiles?: boolean }) => {
      const root = getProjectRoot();

      logger.header('Secret Scanner');
      logger.info(
        `Checking ${opts.allFiles ? 'all files' : 'sensitive files'} across git history...`
      );

      const filePatterns = opts.allFiles ? ['*'] : SENSITIVE_FILE_PATTERNS;

      let commitCount = 0;
      const matches = await scanHistory(root, filePatterns, () => {
        commitCount++;
      });

      logger.info(`Scanned ${commitCount} commits`);

      if (matches.length === 0) {
        logger.success('No secrets found in git history');
        return;
      }

      logger.info('Checking current files for active secrets...');
      for (const match of matches) {
        const pattern = SECRET_PATTERNS.find((p) => p.name === match.patternName);
        if (pattern) {
          match.stillPresent = await checkCurrentFile(root, match.file, pattern.pattern);
        }
      }

      const uniqueFindings = deduplicateFindings(matches);
      const activeCount = uniqueFindings.filter((m) => m.stillPresent).length;
      const historicalCount = uniqueFindings.filter((m) => !m.stillPresent).length;

      if (activeCount > 0) {
        logger.header('ACTIVE — secrets still in current files');
        for (const match of uniqueFindings.filter((m) => m.stillPresent)) {
          logger.fail(match.file);
          console.log(`    Type:   ${match.patternName}`);
          console.log(`    Line:   ${match.line}`);
          console.log(
            `    Commit: ${match.commit.substring(0, 8)} (${match.commitDate.split('T')[0]}) by ${match.author}`
          );
          console.log('');
        }
      }

      if (historicalCount > 0) {
        logger.header('HISTORICAL — removed but still in git history');
        for (const match of uniqueFindings.filter((m) => !m.stillPresent)) {
          logger.warn(match.file);
          console.log(`    Type:   ${match.patternName}`);
          console.log(`    Line:   ${match.line}`);
          console.log(
            `    Commit: ${match.commit.substring(0, 8)} (${match.commitDate.split('T')[0]}) by ${match.author}`
          );
          console.log('');
        }
      }

      logger.header('Summary');
      if (activeCount > 0) {
        logger.fail(`${activeCount} active secret(s) — rotate these immediately`);
      }
      if (historicalCount > 0) {
        logger.warn(`${historicalCount} historical secret(s) — consider cleaning git history`);
      }
      logger.info(
        `Total: ${uniqueFindings.length} unique finding(s) from ${matches.length} match(es)`
      );

      if (activeCount > 0) {
        process.exit(2);
      } else if (historicalCount > 0) {
        process.exit(1);
      }
    });
}

function deduplicateFindings(matches: ScanMatch[]): ScanMatch[] {
  const seen = new Map<string, ScanMatch>();
  for (const match of matches) {
    const key = `${match.file}::${match.patternName}`;
    const existing = seen.get(key);
    if (!existing || match.commitDate > existing.commitDate) {
      seen.set(key, match);
    }
  }
  return Array.from(seen.values());
}
