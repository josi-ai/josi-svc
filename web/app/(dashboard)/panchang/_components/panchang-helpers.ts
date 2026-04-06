/**
 * Helper functions for the Panchang page.
 */

import type { PanchangData, PanchangElement } from './panchang-types';

export function todayString(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export function formatPercent(val?: number): string {
  if (val == null) return '\u2014';
  return `${Math.round(val)}%`;
}

export function qualityColor(quality?: string): string {
  if (!quality) return 'var(--text-muted)';
  const q = quality.toLowerCase();
  if (q === 'auspicious') return 'var(--bar-good)';
  if (q === 'inauspicious') return 'var(--bar-avoid)';
  return 'var(--text-secondary)';
}

export function overallDayQuality(tithi?: PanchangElement, nakshatra?: PanchangElement, yoga?: PanchangElement): { label: string; color: string } {
  const scores: number[] = [];
  const toScore = (q?: string) => {
    if (!q) return 0.5;
    const lower = q.toLowerCase();
    if (lower === 'auspicious') return 1;
    if (lower === 'inauspicious') return 0;
    return 0.5;
  };
  if (yoga?.quality) scores.push(toScore(yoga.quality));
  if (tithi?.paksha) scores.push(tithi.paksha === 'Shukla' ? 0.7 : 0.4);
  if (nakshatra?.ruler) scores.push(0.5);

  const avg = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0.5;
  if (avg >= 0.7) return { label: 'Auspicious Day', color: 'var(--bar-good)' };
  if (avg <= 0.3) return { label: 'Challenging Day', color: 'var(--bar-avoid)' };
  return { label: 'Mixed Day', color: 'var(--gold)' };
}

export function dateString(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

/** Returns Monday of the week containing d */
export function getMonday(d: Date): Date {
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const m = new Date(d);
  m.setDate(diff);
  m.setHours(0, 0, 0, 0);
  return m;
}

/** Returns 7 date strings starting from Monday of the week containing dateStr */
export function weekDates(dateStr: string): string[] {
  const d = new Date(dateStr + 'T12:00:00');
  const mon = getMonday(d);
  const dates: string[] = [];
  for (let i = 0; i < 7; i++) {
    const day = new Date(mon);
    day.setDate(mon.getDate() + i);
    dates.push(dateString(day));
  }
  return dates;
}

/** Returns first day of month and all calendar grid dates (padded to full weeks) */
export function monthCalendarDates(dateStr: string): { year: number; month: number; grid: { date: string; inMonth: boolean }[] } {
  const d = new Date(dateStr + 'T12:00:00');
  const year = d.getFullYear();
  const month = d.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  const startMon = getMonday(firstDay);
  const endDate = new Date(lastDay);
  const endDow = endDate.getDay();
  if (endDow !== 0) endDate.setDate(endDate.getDate() + (7 - endDow));

  const grid: { date: string; inMonth: boolean }[] = [];
  const cursor = new Date(startMon);
  while (cursor <= endDate) {
    grid.push({
      date: dateString(cursor),
      inMonth: cursor.getMonth() === month,
    });
    cursor.setDate(cursor.getDate() + 1);
  }

  return { year, month, grid };
}

export function shortDay(dateStr: string): string {
  return new Date(dateStr + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short' });
}

export function dayNum(dateStr: string): number {
  return new Date(dateStr + 'T12:00:00').getDate();
}

export function monthYearLabel(dateStr: string): string {
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

/** Abbreviated tithi: "Shukla Dvitiya" -> "S2" */
export function tithiAbbrev(tithi?: PanchangElement): string {
  if (!tithi?.name) return '';
  const num = tithi.number;
  const paksha = tithi.paksha;
  const prefix = paksha === 'Shukla' ? 'S' : paksha === 'Krishna' ? 'K' : '';
  return num != null ? `${prefix}${num}` : tithi.name.slice(0, 3);
}

/** Quality dot color for a day */
export function dayQualityColor(data: PanchangData | null | undefined): string {
  if (!data) return 'var(--border)';
  const q = overallDayQuality(data.tithi, data.nakshatra, data.yoga);
  return q.color;
}
