'use client';

import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import type { ForecastEvent } from './transit-types';
import { MONTH_NAMES, DAY_HEADERS, eventTypeColor, getMonthDays } from './transit-helpers';

export function TransitCalendar({ events, fallback }: { events: ForecastEvent[] | null; fallback: boolean }) {
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
