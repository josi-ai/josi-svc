export interface CulturalEvent {
  name: string; date_2026: string; end_date_2026: string | null;
  ethnicity_tags: string[]; tradition: string; description: string;
  significance: string; rituals: string[];
  astrological_significance: string | null;
}

export interface UserProfile { ethnicity: string[] | null; }

export const TRADITION_COLORS: Record<string, { bg: string; text: string; dot: string }> = {
  Hindu:     { bg: 'var(--gold-bg)', text: 'var(--amber)', dot: 'var(--gold-bright)' },
  Buddhist:  { bg: 'var(--blue-bg)', text: 'var(--blue)', dot: 'var(--blue)' },
  Sikh:      { bg: 'var(--amber-bg)', text: 'var(--amber)', dot: 'var(--amber)' },
  Jain:      { bg: 'var(--green-bg)', text: 'var(--green)', dot: 'var(--green)' },
  Islam:     { bg: 'var(--green-bg)', text: 'var(--green)', dot: 'var(--green)' },
  Christian: { bg: 'var(--purple-bg)', text: 'var(--purple)', dot: 'var(--purple)' },
};

export const ALL_TRADITIONS = Object.keys(TRADITION_COLORS);

export const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

export const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function getTraditionStyle(tradition: string) {
  return TRADITION_COLORS[tradition] || { bg: 'rgba(100,100,100,0.12)', text: 'var(--text-muted)', dot: 'var(--text-muted)' };
}

export function buildCalendarDays(year: number, month: number) {
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  return cells;
}

export function eventFallsOnDay(event: CulturalEvent, year: number, month: number, day: number): boolean {
  const target = new Date(year, month, day);
  const start = new Date(event.date_2026 + 'T00:00:00');
  const end = event.end_date_2026 ? new Date(event.end_date_2026 + 'T00:00:00') : start;
  return target >= start && target <= end;
}

export function formatDateRange(start: string, end: string | null): string {
  const s = new Date(start + 'T00:00:00');
  const opts: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' };
  if (!end) return s.toLocaleDateString('en-US', opts);
  const e = new Date(end + 'T00:00:00');
  if (s.getTime() === e.getTime()) return s.toLocaleDateString('en-US', opts);
  return `${s.toLocaleDateString('en-US', opts)} - ${e.toLocaleDateString('en-US', opts)}`;
}
