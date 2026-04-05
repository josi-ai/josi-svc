/**
 * Local types and constants used by the charts listing page.
 *
 * These extend/override the centralized `@/types` shapes where the raw API
 * response needs to be narrowed for this page's specific access patterns
 * (e.g. typed `chart_data.planets` and `chart_data.ascendant`).
 */

/* ---------- Local Types ---------- */

export interface PlanetData {
  sign: string;
  nakshatra?: string;
  nakshatra_pada?: number;
  house?: number;
  sign_degree?: number;
  [key: string]: unknown;
}

export interface ChartDataInner {
  planets?: Record<string, PlanetData>;
  ascendant?: { sign: string; degree: number };
}

export interface ChartItem {
  chart_id: string;
  person_id: string;
  chart_type: string;
  house_system: string;
  ayanamsa: string;
  calculated_at: string;
  chart_data?: ChartDataInner;
  planet_positions?: Record<string, PlanetData>;
}

/* ---------- Constants ---------- */

export const TRADITION_FILTERS = [
  'All',
  'Vedic',
  'Western',
  'Chinese',
  'Hellenistic',
  'Mayan',
  'Celtic',
] as const;

export type TraditionFilter = (typeof TRADITION_FILTERS)[number];

export type ViewMode = 'grid' | 'list';

export type SortColumn = 'name' | 'sun_moon' | 'ascendant' | 'tradition' | 'date';
export type SortDir = 'asc' | 'desc';

export const TRADITION_STYLES: Record<
  string,
  { label: string; variant: 'default' | 'blue' | 'green' | 'outline'; color: string }
> = {
  vedic: { label: 'Vedic', variant: 'default', color: 'var(--gold)' },
  western: { label: 'Western', variant: 'blue', color: '#4A7FB5' },
  chinese: { label: 'Chinese', variant: 'green', color: '#528E62' },
  hellenistic: { label: 'Hellenistic', variant: 'outline', color: '#7B5AAF' },
  mayan: { label: 'Mayan', variant: 'outline', color: '#C46A50' },
  celtic: { label: 'Celtic', variant: 'outline', color: '#3A9DB5' },
};

/** Signs abbreviation map for the South Indian chart grid */
export const SIGN_CELLS: string[] = [
  'Pis', 'Ari', 'Tau', 'Gem',
  'Aqu', '',     '',    'Can',
  'Cap', '',     '',    'Leo',
  'Sag', 'Sco', 'Lib', 'Vir',
];
