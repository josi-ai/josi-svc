import type { ChartDetail, ChartDetailPlanetData } from '@/types';

/* ================================================================
   Constants
   ================================================================ */

export const TABS = ['Overview', 'Planets', 'Houses', 'Aspects'] as const;
export type Tab = (typeof TABS)[number];

export const PLANET_ORDER = [
  'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu',
];

export const TRADITION_STYLES: Record<string, { label: string; variant: 'default' | 'blue' | 'green' | 'outline'; color: string }> = {
  vedic: { label: 'Vedic', variant: 'default', color: 'var(--gold)' },
  western: { label: 'Western', variant: 'blue', color: 'var(--blue)' },
  chinese: { label: 'Chinese', variant: 'green', color: 'var(--green)' },
  hellenistic: { label: 'Hellenistic', variant: 'outline', color: 'var(--text-secondary)' },
  mayan: { label: 'Mayan', variant: 'outline', color: 'var(--text-secondary)' },
  celtic: { label: 'Celtic', variant: 'outline', color: 'var(--text-secondary)' },
};

export const TRADITIONS_LIST = ['Vedic', 'Western', 'Chinese'] as const;
export const CHART_FORMATS = ['South Indian', 'North Indian', 'Western Wheel'] as const;

/* ================================================================
   Helpers
   ================================================================ */

export function formatDegree(deg: number | undefined | null): string {
  if (deg == null || isNaN(deg)) return '\u2014';
  const d = Math.floor(deg);
  const m = Math.round((deg - d) * 60);
  return `${d}\u00B0${m.toString().padStart(2, '0')}\u2032`;
}

export function safeStr(val: unknown): string {
  if (val == null) return '\u2014';
  if (typeof val === 'object') {
    // Handle panchang objects that have a .name property
    if ('name' in (val as Record<string, unknown>)) return String((val as Record<string, unknown>).name);
    return '\u2014';
  }
  return String(val);
}

export function dignityStyle(dignity?: string): { color: string; fontWeight?: number } {
  if (!dignity) return { color: 'var(--text-faint)' };
  const d = dignity.toLowerCase();
  if (d === 'exalted' || d === 'own_sign' || d === 'own' || d === 'moolatrikona')
    return { color: 'var(--gold)', fontWeight: 600 };
  if (d === 'friendly' || d === 'friend')
    return { color: 'var(--green)', fontWeight: 500 };
  if (d === 'debilitated' || d === 'enemy')
    return { color: 'var(--red)', fontWeight: 600 };
  return { color: 'var(--text-secondary)' };
}

export function dignityLabel(dignity?: string): string {
  if (!dignity || dignity === 'neutral') return '\u2014';
  return dignity.charAt(0).toUpperCase() + dignity.slice(1).replace('_', ' ');
}

export function getPlanets(chart: ChartDetail): Record<string, ChartDetailPlanetData> {
  return chart.chart_data?.planets || chart.planet_positions || {};
}
