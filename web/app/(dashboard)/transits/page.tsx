'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { RotateCcw, Star, Activity, ArrowRight, Globe, ChevronLeft, ChevronRight, Calendar, Filter } from 'lucide-react';

/* ================================================================
   Types
   ================================================================ */

interface PlanetPosition {
  sign: string;
  degree: number;
  retrograde: boolean;
  speed?: number;
}

interface MajorTransit {
  planet: string;
  current_sign: string;
  current_degree: number;
  natal_sign: string;
  natal_degree: number;
  aspect: string;
  orb: number;
  intensity: string;
  effects: string;
}

interface ForecastEvent {
  date: string;
  planet: string;
  event_type: string;       // 'sign_change' | 'aspect' | 'retrograde' | 'direct'
  description: string;
  sign?: string;
  aspect_type?: string;
  target_planet?: string;
}

interface ForecastData {
  person_id: string;
  events: ForecastEvent[];
  start_date: string;
  end_date: string;
}

interface TransitData {
  person_id: string;
  current_date: string;
  major_transits: MajorTransit[];
  current_planetary_positions: Record<string, PlanetPosition>;
}

/* ================================================================
   Constants
   ================================================================ */

const PLANET_ORDER = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'];

const ASPECT_COLORS: Record<string, string> = {
  Conjunction: 'var(--gold)',
  Trine: 'var(--green)',
  Sextile: 'var(--green)',
  Square: 'var(--red)',
  Opposition: 'var(--red)',
};

const ASPECT_NATURE: Record<string, string> = {
  Conjunction: 'Fusion',
  Trine: 'Harmonious',
  Sextile: 'Harmonious',
  Square: 'Challenging',
  Opposition: 'Challenging',
};

/* ================================================================
   Helpers
   ================================================================ */

function formatDegree(deg: number | undefined | null): string {
  if (deg == null || isNaN(deg)) return '\u2014';
  const d = Math.floor(deg);
  const m = Math.round((deg - d) * 60);
  return `${d}\u00B0${m.toString().padStart(2, '0')}\u2032`;
}

function intensityColor(intensity: string): string {
  if (intensity === 'Strong') return 'var(--gold)';
  return 'var(--text-muted)';
}

function intensityLabel(orb: number): string {
  if (orb < 2) return 'Strong';
  if (orb <= 5) return 'Moderate';
  return 'Weak';
}

/* ================================================================
   Sub-components
   ================================================================ */

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h4
      style={{
        fontSize: 10,
        textTransform: 'uppercase',
        letterSpacing: 1.2,
        color: 'var(--text-faint)',
        marginBottom: 10,
        paddingLeft: 2,
        fontWeight: 600,
      }}
    >
      {children}
    </h4>
  );
}

function TransitSummaryCard({ transits }: { transits: MajorTransit[] }) {
  const strongTransits = transits.filter((t) => t.orb < 2);
  const highlight = strongTransits[0] || transits[0];

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        padding: 20,
        marginBottom: 24,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div
          style={{
            width: 32, height: 32, borderRadius: 10,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'var(--gold-bg)',
          }}
        >
          <Activity style={{ width: 15, height: 15, color: 'var(--gold)' }} />
        </div>
        <div>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
            Transit Summary
          </h3>
          <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {transits.length} active aspect{transits.length !== 1 ? 's' : ''}
            {strongTransits.length > 0 && ` \u00B7 ${strongTransits.length} strong`}
          </p>
        </div>
      </div>
      {highlight && (
        <div
          style={{
            padding: 12,
            borderRadius: 8,
            background: 'var(--gold-bg)',
            display: 'flex', alignItems: 'flex-start', gap: 8,
          }}
        >
          <Star style={{ width: 14, height: 14, color: 'var(--gold)', marginTop: 1, flexShrink: 0 }} />
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
              {highlight.planet} {highlight.aspect.toLowerCase()} natal {highlight.planet}
            </p>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {highlight.effects}
            </p>
          </div>
        </div>
      )}
      {transits.length === 0 && (
        <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
          No major transit aspects are active right now. Slow-moving planets are between exact aspects.
        </p>
      )}
    </div>
  );
}

function PlanetaryPositionsTable({ positions }: { positions: Record<string, PlanetPosition> }) {
  const ordered = PLANET_ORDER.filter((p) => positions[p]);
  const extra = Object.keys(positions).filter((p) => !PLANET_ORDER.includes(p));
  const allPlanets = [...ordered, ...extra];

  const headerStyle: React.CSSProperties = {
    padding: '10px 16px',
    fontSize: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    color: 'var(--text-faint)',
    fontWeight: 600,
    textAlign: 'left',
    borderBottom: '1px solid var(--border)',
  };

  const cellStyle: React.CSSProperties = {
    padding: '10px 16px',
    fontSize: 13,
    color: 'var(--text-secondary)',
    borderBottom: '1px solid var(--border)',
  };

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        overflow: 'hidden',
        marginBottom: 28,
      }}
    >
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={headerStyle}>Planet</th>
              <th style={headerStyle}>Sign</th>
              <th style={headerStyle}>Degree</th>
              <th style={{ ...headerStyle, textAlign: 'center' }}>Retrograde</th>
            </tr>
          </thead>
          <tbody>
            {allPlanets.map((name) => {
              const p = positions[name];
              if (!p) return null;
              const isRetro = p.retrograde;
              return (
                <tr
                  key={name}
                  style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td
                    style={{
                      ...cellStyle,
                      fontWeight: 600,
                      color: isRetro ? 'var(--red)' : 'var(--text-primary)',
                    }}
                  >
                    {name}
                  </td>
                  <td style={cellStyle}>{p.sign || '\u2014'}</td>
                  <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>
                    {formatDegree(p.degree)}
                  </td>
                  <td style={{ ...cellStyle, textAlign: 'center' }}>
                    {isRetro ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, color: 'var(--red)', fontWeight: 600, fontSize: 11 }}>
                        <RotateCcw style={{ width: 11, height: 11 }} /> Yes
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)' }}>{'\u2014'}</span>
                    )}
                  </td>
                </tr>
              );
            })}
            {allPlanets.length === 0 && (
              <tr>
                <td colSpan={4} style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                  No planetary position data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TransitAspectsSection({ transits }: { transits: MajorTransit[] }) {
  if (transits.length === 0) {
    return (
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--card)',
          padding: 32,
          textAlign: 'center',
          marginBottom: 28,
        }}
      >
        <Globe style={{ width: 24, height: 24, color: 'var(--text-faint)', margin: '0 auto 8px' }} />
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          No major transit aspects within orb right now
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        overflow: 'hidden',
        marginBottom: 28,
      }}
    >
      {transits.map((t, i) => {
        const aspectColor = ASPECT_COLORS[t.aspect] || 'var(--text-muted)';
        const nature = ASPECT_NATURE[t.aspect] || 'Neutral';
        const orbIntensity = intensityLabel(t.orb);

        return (
          <div
            key={i}
            style={{
              padding: '14px 18px',
              borderBottom: i < transits.length - 1 ? '1px solid var(--border)' : 'none',
              transition: 'background 0.15s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
          >
            {/* Aspect row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
                {t.planet}
              </span>
              <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>
                {t.current_sign} {formatDegree(t.current_degree)}
              </span>
              <ArrowRight style={{ width: 12, height: 12, color: aspectColor }} />
              <span
                style={{
                  fontSize: 11, fontWeight: 600,
                  color: aspectColor,
                  padding: '2px 8px',
                  borderRadius: 4,
                  background: nature === 'Harmonious' ? 'var(--green-bg)' : nature === 'Challenging' ? 'var(--red-bg)' : 'var(--gold-bg)',
                }}
              >
                {t.aspect}
              </span>
              <ArrowRight style={{ width: 12, height: 12, color: aspectColor }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
                Natal {t.planet}
              </span>
              <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>
                {t.natal_sign} {formatDegree(t.natal_degree)}
              </span>
            </div>

            {/* Details row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Orb: <span style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{t.orb.toFixed(2)}{'\u00B0'}</span>
              </span>
              <span
                style={{
                  fontSize: 10, fontWeight: 600,
                  color: intensityColor(orbIntensity),
                  padding: '1px 6px',
                  borderRadius: 4,
                  border: `1px solid ${orbIntensity === 'Strong' ? 'var(--gold)' : 'var(--border)'}`,
                }}
              >
                {orbIntensity}
              </span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', flex: 1 }}>
                {t.effects}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ================================================================
   Transit Calendar (T41)
   ================================================================ */

function getMonthDays(year: number, month: number) {
  const firstDay = new Date(year, month, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  return { firstDay, daysInMonth };
}

function eventTypeColor(eventType: string): string {
  if (eventType === 'sign_change') return 'var(--accent-blue, #3B82F6)';
  if (eventType === 'aspect') return 'var(--gold)';
  if (eventType === 'retrograde' || eventType === 'direct') return 'var(--red)';
  return 'var(--text-muted)';
}

function eventTypeLabel(eventType: string): string {
  if (eventType === 'sign_change') return 'Sign Change';
  if (eventType === 'aspect') return 'Aspect';
  if (eventType === 'retrograde') return 'Retrograde';
  if (eventType === 'direct') return 'Direct';
  return eventType;
}

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const DAY_HEADERS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function TransitCalendar({ events, fallback }: { events: ForecastEvent[] | null; fallback: boolean }) {
  const [monthOffset, setMonthOffset] = useState(0);

  const now = new Date();
  const viewYear = new Date(now.getFullYear(), now.getMonth() + monthOffset, 1).getFullYear();
  const viewMonth = new Date(now.getFullYear(), now.getMonth() + monthOffset, 1).getMonth();
  const { firstDay, daysInMonth } = getMonthDays(viewYear, viewMonth);

  // Group events by day
  const eventsByDay = useMemo(() => {
    if (!events) return {};
    const map: Record<number, ForecastEvent[]> = {};
    events.forEach((e) => {
      const d = new Date(e.date);
      if (d.getFullYear() === viewYear && d.getMonth() === viewMonth) {
        const day = d.getDate();
        if (!map[day]) map[day] = [];
        map[day].push(e);
      }
    });
    return map;
  }, [events, viewYear, viewMonth]);

  const today = new Date();
  const isCurrentMonth = today.getFullYear() === viewYear && today.getMonth() === viewMonth;

  if (fallback) {
    return (
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--card)',
          padding: 32,
          textAlign: 'center',
          marginBottom: 28,
        }}
      >
        <Calendar style={{ width: 24, height: 24, color: 'var(--text-faint)', margin: '0 auto 8px' }} />
        <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
          Transit Calendar Coming Soon
        </p>
        <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          A monthly view of sign changes, exact aspects, and retrograde stations will appear here.
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        overflow: 'hidden',
        marginBottom: 28,
      }}
    >
      {/* Month nav */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 18px', borderBottom: '1px solid var(--border)' }}>
        <button
          onClick={() => setMonthOffset((p) => p - 1)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--text-secondary)', display: 'flex' }}
        >
          <ChevronLeft style={{ width: 18, height: 18 }} />
        </button>
        <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
          {MONTH_NAMES[viewMonth]} {viewYear}
        </span>
        <button
          onClick={() => setMonthOffset((p) => p + 1)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--text-secondary)', display: 'flex' }}
        >
          <ChevronRight style={{ width: 18, height: 18 }} />
        </button>
      </div>

      {/* Day headers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)' }}>
        {DAY_HEADERS.map((d) => (
          <div key={d} style={{ padding: '8px 4px', textAlign: 'center', fontSize: 10, fontWeight: 600, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8 }}>
            {d}
          </div>
        ))}
      </div>

      {/* Day cells */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)' }}>
        {/* Empty cells for offset */}
        {Array.from({ length: firstDay }).map((_, i) => (
          <div key={`empty-${i}`} style={{ minHeight: 64, borderTop: '1px solid var(--border)' }} />
        ))}
        {/* Day cells */}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1;
          const dayEvents = eventsByDay[day] || [];
          const isToday = isCurrentMonth && today.getDate() === day;

          return (
            <div
              key={day}
              style={{
                minHeight: 64,
                padding: '4px 5px',
                borderTop: '1px solid var(--border)',
                borderLeft: (firstDay + i) % 7 !== 0 ? '1px solid var(--border)' : 'none',
                background: isToday ? 'var(--gold-bg)' : 'transparent',
              }}
            >
              <div style={{
                fontSize: 11,
                fontWeight: isToday ? 700 : 400,
                color: isToday ? 'var(--gold)' : 'var(--text-secondary)',
                marginBottom: 2,
              }}>
                {day}
              </div>
              {dayEvents.slice(0, 3).map((ev, j) => (
                <div
                  key={j}
                  title={`${ev.planet}: ${ev.description}`}
                  style={{
                    fontSize: 8,
                    fontWeight: 600,
                    color: eventTypeColor(ev.event_type),
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    lineHeight: 1.6,
                  }}
                >
                  {ev.planet.slice(0, 3)}
                </div>
              ))}
              {dayEvents.length > 3 && (
                <div style={{ fontSize: 8, color: 'var(--text-faint)' }}>+{dayEvents.length - 3}</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: 16, padding: '10px 18px', borderTop: '1px solid var(--border)', flexWrap: 'wrap' }}>
        {[
          { color: 'var(--accent-blue, #3B82F6)', label: 'Sign changes' },
          { color: 'var(--gold)', label: 'Exact aspects' },
          { color: 'var(--red)', label: 'Retrograde stations' },
        ].map((l) => (
          <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <div style={{ width: 8, height: 8, borderRadius: 2, background: l.color }} />
            <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{l.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ================================================================
   Transit Forecast Timeline (T42)
   ================================================================ */

type TimelineFilter = 'all' | 'sign_change' | 'aspect' | 'retrograde';

function TransitTimeline({ events, fallback }: { events: ForecastEvent[] | null; fallback: boolean }) {
  const [filter, setFilter] = useState<TimelineFilter>('all');

  const filtered = useMemo(() => {
    if (!events) return [];
    if (filter === 'all') return events;
    if (filter === 'retrograde') return events.filter((e) => e.event_type === 'retrograde' || e.event_type === 'direct');
    return events.filter((e) => e.event_type === filter);
  }, [events, filter]);

  // Group by month
  const grouped = useMemo(() => {
    const map: Record<string, ForecastEvent[]> = {};
    filtered.forEach((e) => {
      const d = new Date(e.date);
      const key = `${MONTH_NAMES[d.getMonth()]} ${d.getFullYear()}`;
      if (!map[key]) map[key] = [];
      map[key].push(e);
    });
    return map;
  }, [filtered]);

  const filterButtons: { key: TimelineFilter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'sign_change', label: 'Sign Changes' },
    { key: 'aspect', label: 'Aspects' },
    { key: 'retrograde', label: 'Retrogrades' },
  ];

  if (fallback) {
    return (
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--card)',
          padding: 32,
          textAlign: 'center',
          marginBottom: 28,
        }}
      >
        <Activity style={{ width: 24, height: 24, color: 'var(--text-faint)', margin: '0 auto 8px' }} />
        <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
          Transit Forecast Coming Soon
        </p>
        <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          A 90-day timeline of upcoming transit events will appear here.
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        overflow: 'hidden',
        marginBottom: 28,
      }}
    >
      {/* Header + Filters */}
      <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Filter style={{ width: 14, height: 14, color: 'var(--text-faint)' }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
            90-Day Forecast
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 'auto' }}>
            {filtered.length} event{filtered.length !== 1 ? 's' : ''}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {filterButtons.map((fb) => (
            <button
              key={fb.key}
              onClick={() => setFilter(fb.key)}
              style={{
                padding: '5px 12px',
                fontSize: 11,
                fontWeight: 600,
                borderRadius: 6,
                border: `1px solid ${filter === fb.key ? 'var(--gold)' : 'var(--border)'}`,
                background: filter === fb.key ? 'var(--gold-bg)' : 'transparent',
                color: filter === fb.key ? 'var(--gold)' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              {fb.label}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div style={{ maxHeight: 480, overflowY: 'auto', padding: '0 18px 16px' }}>
        {Object.keys(grouped).length === 0 && (
          <p style={{ fontSize: 13, color: 'var(--text-muted)', textAlign: 'center', padding: '24px 0' }}>
            No events match this filter.
          </p>
        )}
        {Object.entries(grouped).map(([month, monthEvents]) => (
          <div key={month}>
            <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.2, color: 'var(--text-faint)', padding: '14px 0 6px' }}>
              {month}
            </div>
            {monthEvents.map((ev, i) => {
              const d = new Date(ev.date);
              const dayStr = d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
              const color = eventTypeColor(ev.event_type);

              return (
                <div key={i} style={{ display: 'flex', gap: 12, paddingBottom: 10, position: 'relative' }}>
                  {/* Timeline line */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 16, flexShrink: 0 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: color, marginTop: 4 }} />
                    {i < monthEvents.length - 1 && (
                      <div style={{ width: 1, flex: 1, background: 'var(--border)', marginTop: 2 }} />
                    )}
                  </div>
                  {/* Content */}
                  <div style={{ flex: 1, paddingBottom: 4 }}>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
                      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>
                        {dayStr}
                      </span>
                      <span style={{
                        fontSize: 9, fontWeight: 700, padding: '1px 6px', borderRadius: 4,
                        background: color + '18', color,
                        textTransform: 'uppercase', letterSpacing: 0.5,
                      }}>
                        {eventTypeLabel(ev.event_type)}
                      </span>
                    </div>
                    <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: '2px 0 0', lineHeight: 1.5 }}>
                      <strong>{ev.planet}</strong>{ev.sign ? ` enters ${ev.sign}` : ''}{ev.aspect_type ? ` ${ev.aspect_type}` : ''}{ev.target_planet ? ` ${ev.target_planet}` : ''}
                      {ev.description ? ` \u2014 ${ev.description}` : ''}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      {/* Summary skeleton */}
      <div
        style={{
          height: 120, borderRadius: 12,
          background: 'var(--border)', opacity: 0.3,
          marginBottom: 24, animation: 'pulse 2s infinite',
        }}
      />
      {/* Table skeleton */}
      <div
        style={{
          height: 320, borderRadius: 12,
          background: 'var(--border)', opacity: 0.25,
          marginBottom: 28, animation: 'pulse 2s infinite',
          animationDelay: '0.2s',
        }}
      />
      {/* Aspects skeleton */}
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            height: 72, borderRadius: 12,
            background: 'var(--border)', opacity: 0.2,
            marginBottom: 10, animation: 'pulse 2s infinite',
            animationDelay: `${0.3 + i * 0.1}s`,
          }}
        />
      ))}
    </div>
  );
}

/* ================================================================
   Main Page
   ================================================================ */

export default function TransitsPage() {
  const [personId, setPersonId] = useState<string>('');

  const { data: response, isLoading, error } = useQuery({
    queryKey: ['transits', personId],
    queryFn: () => apiClient.get<TransitData>(`/api/v1/transits/current/${personId}`),
    enabled: !!personId,
  });

  // Forecast query (30 days for calendar)
  const { data: forecastResponse, isError: forecastError } = useQuery({
    queryKey: ['transit-forecast', personId, 90],
    queryFn: () => apiClient.get<ForecastData>(`/api/v1/transits/forecast/${personId}?days=90`),
    enabled: !!personId,
    retry: false,
  });

  const forecastEvents = forecastResponse?.data?.events ?? null;
  const forecastUnavailable = forecastError || (!!personId && forecastEvents === null && !forecastResponse);

  const data = response?.data;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 4px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28, flexWrap: 'wrap', gap: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 36, height: 36, borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'var(--gold-bg)',
            }}
          >
            <Globe style={{ width: 18, height: 18, color: 'var(--gold)' }} />
          </div>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              Current Transits
            </h1>
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Planetary positions affecting your chart
            </p>
          </div>
        </div>
        <div style={{ minWidth: 200 }}>
          <ProfileSelector value={personId} onChange={setPersonId} />
        </div>
      </div>

      {/* No profile */}
      {!personId && (
        <div
          style={{
            border: '1px solid var(--border)',
            borderRadius: 12,
            background: 'var(--card)',
            padding: 48,
            textAlign: 'center',
          }}
        >
          <div
            style={{
              width: 48, height: 48, borderRadius: '50%', margin: '0 auto 14px',
              background: 'var(--gold-bg)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <Globe style={{ width: 22, height: 22, color: 'var(--gold)' }} />
          </div>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 4 }}>
            Select a profile to get started
          </p>
          <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            See how current planetary positions affect your natal chart
          </p>
        </div>
      )}

      {/* Loading */}
      {isLoading && <LoadingSkeleton />}

      {/* Error */}
      {error && !isLoading && (
        <div
          style={{
            border: '1px solid var(--red)',
            borderRadius: 12,
            background: 'var(--red-bg)',
            padding: 16,
            marginBottom: 24,
            display: 'flex', alignItems: 'center', gap: 10,
          }}
        >
          <Star style={{ width: 16, height: 16, color: 'var(--red)', flexShrink: 0 }} />
          <p style={{ fontSize: 13, color: 'var(--red)' }}>
            {(error as Error).message || 'Failed to load transit data'}
          </p>
        </div>
      )}

      {/* Results */}
      {data && !isLoading && (
        <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
          {/* Transit Summary */}
          <TransitSummaryCard transits={data.major_transits} />

          {/* Current Planetary Positions */}
          <SectionHeading>Current Planetary Positions</SectionHeading>
          <PlanetaryPositionsTable positions={data.current_planetary_positions} />

          {/* Active Transit Aspects */}
          <SectionHeading>Active Transit Aspects</SectionHeading>
          <TransitAspectsSection transits={data.major_transits} />

          {/* Transit Calendar (T41) */}
          <SectionHeading>Transit Calendar</SectionHeading>
          <TransitCalendar events={forecastEvents} fallback={!!forecastUnavailable} />

          {/* Transit Forecast Timeline (T42) */}
          <SectionHeading>Forecast Timeline</SectionHeading>
          <TransitTimeline events={forecastEvents} fallback={!!forecastUnavailable} />
        </div>
      )}
    </div>
  );
}
