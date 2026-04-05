/**
 * Pure helper functions for the charts listing page.
 *
 * No React imports -- these are plain TypeScript utilities.
 */

import type { ChartItem, PlanetData } from './chart-types';
import { TRADITION_STYLES } from './chart-types';

/* ---------- Planet / Sign Accessors ---------- */

export function getPlanets(chart: ChartItem): Record<string, PlanetData> {
  return chart.chart_data?.planets || chart.planet_positions || {};
}

export function getSunSign(chart: ChartItem): string {
  return getPlanets(chart)['Sun']?.sign || '';
}

export function getMoonSign(chart: ChartItem): string {
  return getPlanets(chart)['Moon']?.sign || '';
}

export function getChartName(chart: ChartItem): string {
  const sun = getSunSign(chart);
  const moon = getMoonSign(chart);
  const parts: string[] = [];
  if (sun) parts.push(`Sun ${sun}`);
  if (moon) parts.push(`Moon ${moon}`);
  return parts.length > 0 ? parts.join(', ') : 'Chart calculated';
}

export function getAscendant(chart: ChartItem): { sign: string; nakshatra?: string } {
  const asc = chart.chart_data?.ascendant;
  return { sign: asc?.sign || '', nakshatra: undefined };
}

export function getAscendantNakshatra(chart: ChartItem): string | undefined {
  // Try to find ascendant nakshatra from planet data (some APIs include it)
  const planets = getPlanets(chart);
  const asc = planets['Ascendant'] || planets['Lagna'];
  return asc?.nakshatra;
}

/* ---------- Formatting ---------- */

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/* ---------- Tradition Lookup ---------- */

export function getTradition(chart: ChartItem) {
  return (
    TRADITION_STYLES[chart.chart_type.toLowerCase()] || {
      label: chart.chart_type.charAt(0).toUpperCase() + chart.chart_type.slice(1),
      variant: 'outline' as const,
      color: 'var(--text-muted)',
    }
  );
}

/* ---------- Mini Chart Data ---------- */

/**
 * Build a simple planet-to-sign lookup for the mini chart.
 * Returns a map of sign abbreviation -> planet abbreviations in that sign.
 */
export function buildSignPlanetMap(chart: ChartItem): Record<string, string[]> {
  const SIGN_ABBR: Record<string, string> = {
    Aries: 'Ari', Taurus: 'Tau', Gemini: 'Gem', Cancer: 'Can',
    Leo: 'Leo', Virgo: 'Vir', Libra: 'Lib', Scorpio: 'Sco',
    Sagittarius: 'Sag', Capricorn: 'Cap', Aquarius: 'Aqu', Pisces: 'Pis',
  };
  const PLANET_ABBR: Record<string, string> = {
    Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me',
    Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke',
  };
  const planets = getPlanets(chart);
  const map: Record<string, string[]> = {};

  Object.entries(planets).forEach(([name, data]) => {
    if (!data.sign) return;
    const signKey = SIGN_ABBR[data.sign] || data.sign.slice(0, 3);
    const planetKey = PLANET_ABBR[name] || name.slice(0, 2);
    if (!map[signKey]) map[signKey] = [];
    map[signKey].push(planetKey);
  });

  // Mark ascendant
  const asc = chart.chart_data?.ascendant;
  if (asc?.sign) {
    const signKey = SIGN_ABBR[asc.sign] || asc.sign.slice(0, 3);
    if (!map[signKey]) map[signKey] = [];
    if (!map[signKey].includes('As')) map[signKey].push('As');
  }

  return map;
}
