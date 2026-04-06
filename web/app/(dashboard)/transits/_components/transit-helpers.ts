/**
 * Helper functions and constants for the Transits page.
 */

export const PLANET_ORDER = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'];

export const ASPECT_COLORS: Record<string, string> = {
  Conjunction: 'var(--gold)',
  Trine: 'var(--green)',
  Sextile: 'var(--green)',
  Square: 'var(--red)',
  Opposition: 'var(--red)',
};

export const ASPECT_NATURE: Record<string, string> = {
  Conjunction: 'Fusion',
  Trine: 'Harmonious',
  Sextile: 'Harmonious',
  Square: 'Challenging',
  Opposition: 'Challenging',
};

export const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
export const DAY_HEADERS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function formatDegree(deg: number | undefined | null): string {
  if (deg == null || isNaN(deg)) return '\u2014';
  const d = Math.floor(deg);
  const m = Math.round((deg - d) * 60);
  return `${d}\u00B0${m.toString().padStart(2, '0')}\u2032`;
}

export function intensityColor(intensity: string): string {
  if (intensity === 'Strong') return 'var(--gold)';
  return 'var(--text-muted)';
}

export function intensityLabel(orb: number): string {
  if (orb < 2) return 'Strong';
  if (orb <= 5) return 'Moderate';
  return 'Weak';
}

export function eventTypeColor(eventType: string): string {
  if (eventType === 'sign_change') return 'var(--accent-blue, #3B82F6)';
  if (eventType === 'aspect') return 'var(--gold)';
  if (eventType === 'retrograde' || eventType === 'direct') return 'var(--red)';
  return 'var(--text-muted)';
}

export function eventTypeLabel(eventType: string): string {
  if (eventType === 'sign_change') return 'Sign Change';
  if (eventType === 'aspect') return 'Aspect';
  if (eventType === 'retrograde') return 'Retrograde';
  if (eventType === 'direct') return 'Direct';
  return eventType;
}

export function getMonthDays(year: number, month: number) {
  const firstDay = new Date(year, month, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  return { firstDay, daysInMonth };
}
