import { execFileSync } from 'node:child_process';
import * as logger from './logger.js';

const GCP_PROJECT = 'josiam';

export function fetchSecret(secretName: string): string {
  const result = execFileSync(
    'gcloud',
    [
      'secrets', 'versions', 'access', 'latest',
      `--secret=${secretName}`,
      `--project=${GCP_PROJECT}`,
    ],
    { encoding: 'utf-8', timeout: 15_000 },
  );
  return result.trim();
}

export interface DbCredentials {
  DB_USER: string;
  DB_PASSWORD: string;
}

export function fetchDbCredentials(env: string): DbCredentials {
  logger.step(`Fetching DB credentials for ${env}...`);
  const DB_USER = fetchSecret(`josiam-db-user-${env}`);
  const rawPassword = fetchSecret(`josiam-db-password-${env}`);
  // URL-encode the password since it's interpolated into DATABASE_URL
  const DB_PASSWORD = encodeURIComponent(rawPassword);
  logger.success('DB credentials fetched');
  return { DB_USER, DB_PASSWORD };
}
