export interface ServiceConfig {
  name: string;
  port: number;
  url: string;
}

export const SERVICES: Record<string, ServiceConfig> = {
  api: { name: 'Josi API', port: 1954, url: 'http://localhost:1954' },
  db: { name: 'PostgreSQL', port: 1961, url: 'postgresql+asyncpg://josi:josi@localhost:1961/josi' },
  'db-test': { name: 'Test DB', port: 1962, url: 'postgresql+asyncpg://josi:josi@localhost:1962/josi_test' },
  web: { name: 'Josi Web', port: 1989, url: 'http://localhost:1989' },
};

export const URLS = {
  docs: 'http://localhost:1954/docs',
  redoc: 'http://localhost:1954/redoc',
  graphql: 'http://localhost:1954/graphql',
  health: 'http://localhost:1954/api/v1/health',
  web: 'http://localhost:1989',
};

export interface Tool {
  name: string;
  command: string;
  versionFlag: string;
  installMac?: string;
  installLinux?: string;
  required: boolean;
}

export const VALID_ENVS = ['dev', 'prod'] as const;
export type Env = (typeof VALID_ENVS)[number];

export const VALID_MODES = ['cloud', 'local'] as const;
export type Mode = (typeof VALID_MODES)[number];

export interface UpOptions {
  local?: boolean;
  logs?: boolean;
  web?: boolean;
  build?: boolean;
}

export interface ComposeConfig {
  files: string[];
  profiles: string[];
}

export interface EnvConfig {
  project: string;
  instance: string;
}

export const ENV_CONFIGS: Record<Env, EnvConfig> = {
  dev:  { project: 'josiam', instance: 'josiam:us-central1:josiam-dev' },
  prod: { project: 'josiam', instance: 'josiam:us-central1:josiam-prod' },
};
