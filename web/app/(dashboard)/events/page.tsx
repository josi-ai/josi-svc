'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import {
  type CulturalEvent, type UserProfile,
  ALL_TRADITIONS, MONTH_NAMES, DAY_LABELS,
  getTraditionStyle, buildCalendarDays, eventFallsOnDay,
} from './_components/event-types';
import { SkeletonCards, EmptyState, EventCard } from './_components/event-sub-components';

const navBtnStyle: React.CSSProperties = {
  width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center',
  fontSize: 18, color: 'var(--text-secondary)', background: 'var(--card)',
  border: '1px solid var(--border)', borderRadius: 10, cursor: 'pointer', transition: 'border-color 0.15s',
};

export default function CulturalEventsPage() {
  const { isAuthReady } = useAuth();
  const now = new Date();
  const [year] = useState(2026);
  const [month, setMonth] = useState(now.getMonth());
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set());

  const { data: profileData } = useQuery({
    queryKey: ['me-profile'],
    queryFn: () => apiClient.get<UserProfile>('/api/v1/me'),
    enabled: isAuthReady,
  });
  const userEthnicity = profileData?.data?.ethnicity || [];

  const ethnicityParam = userEthnicity.length > 0 ? userEthnicity.join(',') : '';
  const apiMonth = month + 1;

  const { data: eventsData, isLoading } = useQuery({
    queryKey: ['cultural-events', ethnicityParam, year, apiMonth],
    queryFn: () => apiClient.get<{ events: CulturalEvent[]; total: number }>(
      `/api/v1/events/cultural?year=${year}&month=${apiMonth}${ethnicityParam ? `&ethnicity=${encodeURIComponent(ethnicityParam)}` : ''}`
    ),
    enabled: isAuthReady,
  });

  const events = eventsData?.data?.events || [];

  const filteredEvents = useMemo(() => {
    if (activeFilters.size === 0) return events;
    return events.filter((e) => activeFilters.has(e.tradition));
  }, [events, activeFilters]);

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
    <div style={{ padding: '32px 0' }}>
      <h1 className="font-display" style={{ fontSize: 28, color: 'var(--text-primary)', fontWeight: 400, margin: '0 0 8px' }}>Cultural Events &amp; Festivals</h1>
      <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: '0 0 28px' }}>
        {userEthnicity.length > 0 ? `Showing events for: ${userEthnicity.join(', ')}` : 'Showing all cultural events'}
      </p>

      {/* Month Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <button onClick={prevMonth} style={navBtnStyle} aria-label="Previous month">&#8592;</button>
        <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{MONTH_NAMES[month]} {year}</h2>
        <button onClick={nextMonth} style={navBtnStyle} aria-label="Next month">&#8594;</button>
      </div>

      {/* Calendar Grid */}
      <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 20, marginBottom: 24 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2, marginBottom: 8 }}>
          {DAY_LABELS.map((d) => (
            <div key={d} style={{ textAlign: 'center', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-faint)', padding: '4px 0' }}>{d}</div>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2 }}>
          {calendarCells.map((day, idx) => {
            const traditions = day ? dayEventMap.get(day) : undefined;
            const isToday = isCurrentMonth && day === today;
            return (
              <div key={idx} style={{ minHeight: 52, padding: '6px 4px', textAlign: 'center', borderRadius: 8, background: isToday ? 'rgba(245,166,35,0.08)' : 'transparent', border: isToday ? '1px solid rgba(245,166,35,0.3)' : '1px solid transparent' }}>
                {day && (
                  <>
                    <div style={{ fontSize: 13, fontWeight: isToday ? 700 : 400, color: isToday ? 'var(--gold)' : 'var(--text-secondary)' }}>{day}</div>
                    {traditions && traditions.size > 0 && (
                      <div style={{ display: 'flex', justifyContent: 'center', gap: 3, marginTop: 4, flexWrap: 'wrap' }}>
                        {Array.from(traditions).map((t) => (
                          <span key={t} style={{ width: 6, height: 6, borderRadius: '50%', background: getTraditionStyle(t).dot, display: 'inline-block' }} />
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
              <button key={t} onClick={() => toggleFilter(t)} style={{
                padding: '6px 14px', fontSize: 12, fontWeight: 500, borderRadius: 20, cursor: 'pointer',
                border: `1px solid ${active ? style.dot : 'var(--border)'}`,
                background: active ? style.bg : 'transparent', color: active ? style.text : 'var(--text-muted)',
                opacity: active ? 1 : 0.5, transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: 6,
              }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: style.dot, display: 'inline-block' }} />
                {t}
              </button>
            );
          })}
        </div>
      )}

      {/* Events List */}
      {isLoading ? <SkeletonCards /> : filteredEvents.length === 0 ? (
        userEthnicity.length === 0 ? <EmptyState /> : (
          <div style={{ textAlign: 'center', padding: '40px 24px', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14 }}>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: 0 }}>No events found for {MONTH_NAMES[month]} {year}.</p>
          </div>
        )
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.2px', color: 'var(--text-faint)' }}>
            {filteredEvents.length} event{filteredEvents.length !== 1 ? 's' : ''} this month
          </div>
          {filteredEvents.map((event) => <EventCard key={`${event.name}-${event.date_2026}`} event={event} />)}
        </div>
      )}
    </div>
  );
}
