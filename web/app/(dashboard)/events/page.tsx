'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

/* ---------- Types ---------- */

interface CulturalEvent {
  name: string;
  date_2026: string;
  end_date_2026: string | null;
  ethnicity_tags: string[];
  tradition: string;
  description: string;
  significance: string;
  rituals: string[];
  astrological_significance: string | null;
}

interface UserProfile {
  ethnicity: string[] | null;
}

/* ---------- Constants ---------- */

const TRADITION_COLORS: Record<string, { bg: string; text: string; dot: string }> = {
  Hindu:     { bg: 'var(--gold-bg)', text: 'var(--amber)', dot: 'var(--gold-bright)' },
  Buddhist:  { bg: 'var(--blue-bg)', text: 'var(--blue)', dot: 'var(--blue)' },
  Sikh:      { bg: 'var(--amber-bg)', text: 'var(--amber)', dot: 'var(--amber)' },
  Jain:      { bg: 'var(--green-bg)', text: 'var(--green)', dot: 'var(--green)' },
  Islam:     { bg: 'var(--green-bg)', text: 'var(--green)', dot: 'var(--green)' },
  Christian: { bg: 'var(--purple-bg)', text: 'var(--purple)', dot: 'var(--purple)' },
};

const ALL_TRADITIONS = Object.keys(TRADITION_COLORS);

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/* ---------- Helpers ---------- */

function getTraditionStyle(tradition: string) {
  return TRADITION_COLORS[tradition] || { bg: 'rgba(100,100,100,0.12)', text: 'var(--text-muted)', dot: 'var(--text-muted)' };
}

function buildCalendarDays(year: number, month: number) {
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  return cells;
}

function eventFallsOnDay(event: CulturalEvent, year: number, month: number, day: number): boolean {
  const target = new Date(year, month, day);
  const start = new Date(event.date_2026 + 'T00:00:00');
  const end = event.end_date_2026 ? new Date(event.end_date_2026 + 'T00:00:00') : start;
  return target >= start && target <= end;
}

function formatDateRange(start: string, end: string | null): string {
  const s = new Date(start + 'T00:00:00');
  const opts: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' };
  if (!end) return s.toLocaleDateString('en-US', opts);
  const e = new Date(end + 'T00:00:00');
  if (s.getTime() === e.getTime()) return s.toLocaleDateString('en-US', opts);
  return `${s.toLocaleDateString('en-US', opts)} - ${e.toLocaleDateString('en-US', opts)}`;
}

/* ---------- Skeleton ---------- */

function SkeletonCards() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {[1, 2, 3].map((i) => (
        <div key={i} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 24 }}>
          <div style={{ height: 18, width: '40%', background: 'var(--border)', borderRadius: 6, marginBottom: 12 }} />
          <div style={{ height: 12, width: '25%', background: 'var(--border)', borderRadius: 4, marginBottom: 16 }} />
          <div style={{ height: 12, width: '90%', background: 'var(--border)', borderRadius: 4, marginBottom: 8 }} />
          <div style={{ height: 12, width: '70%', background: 'var(--border)', borderRadius: 4 }} />
        </div>
      ))}
    </div>
  );
}

/* ---------- Empty state ---------- */

function EmptyState() {
  return (
    <div style={{
      textAlign: 'center', padding: '60px 24px',
      background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
    }}>
      <div style={{ fontSize: 40, marginBottom: 16 }}>&#x1F3AA;</div>
      <h3 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 8px' }}>
        No events to display
      </h3>
      <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: '0 0 20px', maxWidth: 400, marginInline: 'auto' }}>
        Set your ethnicity in Settings to see cultural events relevant to your background.
      </p>
      <Link
        href="/settings"
        style={{
          display: 'inline-block', padding: '10px 24px', fontSize: 14, fontWeight: 600,
          color: 'var(--primary-foreground)', background: 'var(--gold)', borderRadius: 10, textDecoration: 'none',
        }}
      >
        Go to Settings
      </Link>
    </div>
  );
}

/* ---------- Event Card ---------- */

function EventCard({ event }: { event: CulturalEvent }) {
  const style = getTraditionStyle(event.tradition);
  return (
    <div style={{
      background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
      padding: 24, transition: 'border-color 0.15s',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontSize: 17, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{event.name}</h3>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '4px 0 0' }}>
            {formatDateRange(event.date_2026, event.end_date_2026)}
          </p>
        </div>
        <span style={{
          padding: '4px 10px', fontSize: 11, fontWeight: 600, borderRadius: 20,
          background: style.bg, color: style.text, whiteSpace: 'nowrap', flexShrink: 0,
        }}>
          {event.tradition}
        </span>
      </div>

      <p style={{ fontSize: 14, color: 'var(--text-secondary)', margin: '12px 0 0', lineHeight: 1.5 }}>
        {event.description}
      </p>

      {event.significance && (
        <div style={{ margin: '14px 0 0', padding: '12px 14px', borderRadius: 10, background: 'var(--background)', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.2px', color: 'var(--text-faint)', marginBottom: 6 }}>
            Significance
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.55 }}>{event.significance}</p>
        </div>
      )}

      {event.rituals && event.rituals.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.2px', color: 'var(--text-faint)', marginBottom: 8 }}>
            Rituals &amp; Observances
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {event.rituals.map((r) => (
              <span key={r} style={{
                padding: '4px 10px', fontSize: 12, color: 'var(--text-secondary)',
                background: 'var(--background)', border: '1px solid var(--border)', borderRadius: 16,
              }}>
                {r}
              </span>
            ))}
          </div>
        </div>
      )}

      {event.astrological_significance && (
        <div style={{ marginTop: 14, display: 'flex', alignItems: 'flex-start', gap: 8 }}>
          <span style={{ fontSize: 14, flexShrink: 0, marginTop: 1 }}>&#x2728;</span>
          <p style={{ fontSize: 12, color: 'var(--gold)', margin: 0, lineHeight: 1.5, fontStyle: 'italic' }}>
            {event.astrological_significance}
          </p>
        </div>
      )}
    </div>
  );
}

/* ---------- Main Page ---------- */

export default function CulturalEventsPage() {
  const { isAuthReady } = useAuth();
  const now = new Date();
  const [year] = useState(2026);
  const [month, setMonth] = useState(now.getMonth()); // 0-indexed
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set());

  // Fetch user profile for ethnicity
  const { data: profileData } = useQuery({
    queryKey: ['me-profile'],
    queryFn: () => apiClient.get<UserProfile>('/api/v1/me'),
    enabled: isAuthReady,
  });
  const userEthnicity = profileData?.data?.ethnicity || [];

  // Fetch events
  const ethnicityParam = userEthnicity.length > 0 ? userEthnicity.join(',') : '';
  const apiMonth = month + 1;

  const { data: eventsData, isLoading } = useQuery({
    queryKey: ['cultural-events', ethnicityParam, year, apiMonth],
    queryFn: () =>
      apiClient.get<{ events: CulturalEvent[]; total: number }>(
        `/api/v1/events/cultural?year=${year}&month=${apiMonth}${ethnicityParam ? `&ethnicity=${encodeURIComponent(ethnicityParam)}` : ''}`
      ),
    enabled: isAuthReady,
  });

  const events = eventsData?.data?.events || [];

  // Apply tradition filter
  const filteredEvents = useMemo(() => {
    if (activeFilters.size === 0) return events;
    return events.filter((e) => activeFilters.has(e.tradition));
  }, [events, activeFilters]);

  // Map day -> traditions with events
  const dayEventMap = useMemo(() => {
    const map = new Map<number, Set<string>>();
    for (const evt of filteredEvents) {
      const cells = buildCalendarDays(year, month);
      for (const cell of cells) {
        if (cell && eventFallsOnDay(evt, year, month, cell)) {
          if (!map.has(cell)) map.set(cell, new Set());
          map.get(cell)!.add(evt.tradition);
        }
      }
    }
    return map;
  }, [filteredEvents, year, month]);

  const calendarCells = useMemo(() => buildCalendarDays(year, month), [year, month]);

  // Tradition filter toggles
  const traditionsInEvents = useMemo(() => {
    const set = new Set<string>();
    events.forEach((e) => set.add(e.tradition));
    return ALL_TRADITIONS.filter((t) => set.has(t));
  }, [events]);

  const toggleFilter = (tradition: string) => {
    setActiveFilters((prev) => {
      const next = new Set(prev);
      if (next.has(tradition)) next.delete(tradition);
      else next.add(tradition);
      return next;
    });
  };

  const prevMonth = () => setMonth((m) => (m === 0 ? 11 : m - 1));
  const nextMonth = () => setMonth((m) => (m === 11 ? 0 : m + 1));

  const today = now.getDate();
  const isCurrentMonth = now.getMonth() === month && now.getFullYear() === year;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 16px' }}>
      {/* Header */}
      <h1 className="font-display" style={{ fontSize: 28, color: 'var(--text-primary)', fontWeight: 400, margin: '0 0 8px' }}>
        Cultural Events &amp; Festivals
      </h1>
      <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: '0 0 28px' }}>
        {userEthnicity.length > 0
          ? `Showing events for: ${userEthnicity.join(', ')}`
          : 'Showing all cultural events'}
      </p>

      {/* Month Navigation */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 20,
      }}>
        <button onClick={prevMonth} style={navBtnStyle} aria-label="Previous month">
          &#8592;
        </button>
        <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
          {MONTH_NAMES[month]} {year}
        </h2>
        <button onClick={nextMonth} style={navBtnStyle} aria-label="Next month">
          &#8594;
        </button>
      </div>

      {/* Calendar Grid */}
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
        padding: 20, marginBottom: 24,
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2, marginBottom: 8 }}>
          {DAY_LABELS.map((d) => (
            <div key={d} style={{
              textAlign: 'center', fontSize: 11, fontWeight: 600, textTransform: 'uppercase',
              letterSpacing: '1px', color: 'var(--text-faint)', padding: '4px 0',
            }}>
              {d}
            </div>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2 }}>
          {calendarCells.map((day, idx) => {
            const traditions = day ? dayEventMap.get(day) : undefined;
            const isToday = isCurrentMonth && day === today;
            return (
              <div key={idx} style={{
                minHeight: 52, padding: '6px 4px', textAlign: 'center', borderRadius: 8,
                background: isToday ? 'rgba(245,166,35,0.08)' : 'transparent',
                border: isToday ? '1px solid rgba(245,166,35,0.3)' : '1px solid transparent',
              }}>
                {day && (
                  <>
                    <div style={{
                      fontSize: 13, fontWeight: isToday ? 700 : 400,
                      color: isToday ? 'var(--gold)' : 'var(--text-secondary)',
                    }}>
                      {day}
                    </div>
                    {traditions && traditions.size > 0 && (
                      <div style={{ display: 'flex', justifyContent: 'center', gap: 3, marginTop: 4, flexWrap: 'wrap' }}>
                        {Array.from(traditions).map((t) => (
                          <span key={t} style={{
                            width: 6, height: 6, borderRadius: '50%',
                            background: getTraditionStyle(t).dot,
                            display: 'inline-block',
                          }} />
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Tradition Filters */}
      {traditionsInEvents.length > 1 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
          {traditionsInEvents.map((t) => {
            const active = activeFilters.size === 0 || activeFilters.has(t);
            const style = getTraditionStyle(t);
            return (
              <button
                key={t}
                onClick={() => toggleFilter(t)}
                style={{
                  padding: '6px 14px', fontSize: 12, fontWeight: 500, borderRadius: 20, cursor: 'pointer',
                  border: `1px solid ${active ? style.dot : 'var(--border)'}`,
                  background: active ? style.bg : 'transparent',
                  color: active ? style.text : 'var(--text-muted)',
                  opacity: active ? 1 : 0.5,
                  transition: 'all 0.15s',
                  display: 'flex', alignItems: 'center', gap: 6,
                }}
              >
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: style.dot, display: 'inline-block' }} />
                {t}
              </button>
            );
          })}
        </div>
      )}

      {/* Events List */}
      {isLoading ? (
        <SkeletonCards />
      ) : filteredEvents.length === 0 ? (
        userEthnicity.length === 0 ? <EmptyState /> : (
          <div style={{
            textAlign: 'center', padding: '40px 24px',
            background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
          }}>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: 0 }}>
              No events found for {MONTH_NAMES[month]} {year}.
            </p>
          </div>
        )
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.2px', color: 'var(--text-faint)' }}>
            {filteredEvents.length} event{filteredEvents.length !== 1 ? 's' : ''} this month
          </div>
          {filteredEvents.map((event) => (
            <EventCard key={`${event.name}-${event.date_2026}`} event={event} />
          ))}
        </div>
      )}
    </div>
  );
}

/* ---------- Styles ---------- */

const navBtnStyle: React.CSSProperties = {
  width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center',
  fontSize: 18, color: 'var(--text-secondary)', background: 'var(--card)',
  border: '1px solid var(--border)', borderRadius: 10, cursor: 'pointer',
  transition: 'border-color 0.15s',
};
