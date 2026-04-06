/* ================================================================
   Shared types and constants for chart visualization components
   ================================================================ */

export interface PlanetData {
  longitude: number;
  sign: string;
  sign_degree: number;
  house: number;
  nakshatra?: string;
  nakshatra_pada?: number;
  pada?: number;
  is_retrograde: boolean;
  speed?: number;
  dignity?: string;
}

export interface ChartProps {
  planets: Record<string, PlanetData>;
  ascSign?: string; // Ascendant sign name (e.g., "Aries")
}

export const PLANET_ABBREV: Record<string, string> = {
  Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me',
  Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke',
};

export const SIGN_ABBREV: Record<string, string> = {
  Aries: 'Ar', Taurus: 'Ta', Gemini: 'Ge', Cancer: 'Ca',
  Leo: 'Le', Virgo: 'Vi', Libra: 'Li', Scorpio: 'Sc',
  Sagittarius: 'Sg', Capricorn: 'Cp', Aquarius: 'Aq', Pisces: 'Pi',
};

export const SIGNS_ORDERED = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
];

/* South Indian chart: signs in fixed cell positions (row, col) */
export const SI_CELL_POSITIONS: { sign: string; row: number; col: number }[] = [
  { sign: 'Pisces', row: 0, col: 0 },
  { sign: 'Aries', row: 0, col: 1 },
  { sign: 'Taurus', row: 0, col: 2 },
  { sign: 'Gemini', row: 0, col: 3 },
  { sign: 'Cancer', row: 1, col: 3 },
  { sign: 'Leo', row: 2, col: 3 },
  { sign: 'Virgo', row: 3, col: 3 },
  { sign: 'Libra', row: 3, col: 2 },
  { sign: 'Scorpio', row: 3, col: 1 },
  { sign: 'Sagittarius', row: 3, col: 0 },
  { sign: 'Capricorn', row: 2, col: 0 },
  { sign: 'Aquarius', row: 1, col: 0 },
];

/* Sign Unicode glyphs for Western wheel */
export const SIGN_GLYPHS: Record<string, string> = {
  Aries: '\u2648', Taurus: '\u2649', Gemini: '\u264A', Cancer: '\u264B',
  Leo: '\u264C', Virgo: '\u264D', Libra: '\u264E', Scorpio: '\u264F',
  Sagittarius: '\u2650', Capricorn: '\u2651', Aquarius: '\u2652', Pisces: '\u2653',
};

/* Planet Unicode glyphs for Western wheel */
export const PLANET_GLYPHS: Record<string, string> = {
  Sun: '\u2609', Moon: '\u263D', Mars: '\u2642', Mercury: '\u263F',
  Jupiter: '\u2643', Venus: '\u2640', Saturn: '\u2644', Rahu: '\u260A', Ketu: '\u260B',
};

/* Element colors for Western wheel sign segments */
export const SIGN_ELEMENT_COLORS: Record<string, string> = {
  Aries: 'var(--element-fire)', Taurus: 'var(--element-earth)', Gemini: 'var(--element-air)', Cancer: 'var(--element-water)',
  Leo: 'var(--element-fire)', Virgo: 'var(--element-earth)', Libra: 'var(--element-air)', Scorpio: 'var(--element-water)',
  Sagittarius: 'var(--element-fire)', Capricorn: 'var(--element-earth)', Aquarius: 'var(--element-air)', Pisces: 'var(--element-water)',
};

/* Shared helper: group planets by their sign */
export function getPlanetsBySign(planets: Record<string, PlanetData>): Record<string, string[]> {
  const map: Record<string, string[]> = {};
  for (const [name, data] of Object.entries(planets)) {
    const sign = data.sign;
    if (!sign) continue;
    if (!map[sign]) map[sign] = [];
    map[sign].push(PLANET_ABBREV[name] || name.substring(0, 2));
  }
  return map;
}
