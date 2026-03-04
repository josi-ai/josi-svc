export interface ServiceConfig {
  name: string;
  port: number;
  url: string;
}

export const SERVICES: Record<string, ServiceConfig> = {
  api: { name: 'Josi API', port: 1954, url: 'http://localhost:1954' },
  db: { name: 'PostgreSQL', port: 1961, url: 'postgresql://josi:josi@localhost:1961/josi' },
  redis: { name: 'Redis', port: 1982, url: 'redis://localhost:1982/0' },
};

export const URLS = {
  docs: 'http://localhost:1954/docs',
  redoc: 'http://localhost:1954/redoc',
  graphql: 'http://localhost:1954/graphql',
  health: 'http://localhost:1954/api/v1/health',
};

export interface Tool {
  name: string;
  command: string;
  versionFlag: string;
  installMac?: string;
  installLinux?: string;
  required: boolean;
}
