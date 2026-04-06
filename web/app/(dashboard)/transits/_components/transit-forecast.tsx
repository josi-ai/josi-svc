'use client';

import { useState, useMemo } from 'react';
import { Activity, Filter } from 'lucide-react';
import type { ForecastEvent } from './transit-types';
import { MONTH_NAMES, eventTypeColor, eventTypeLabel } from './transit-helpers';

type TimelineFilter = 'all' | 'sign_change' | 'aspect' | 'retrograde';

export function TransitTimeline({ events, fallback }: { events: ForecastEvent[] | null; fallback: boolean }) {
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
