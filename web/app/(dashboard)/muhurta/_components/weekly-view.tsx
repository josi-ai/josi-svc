'use client';

import React, { useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  type PanchangDetail,
  cardS, DAYS_SHORT, MONTHS,
  fd, addD, dayQuality, Spinner,
} from './muhurta-shared';

export function WeeklyView({ startDate, lat, lng, tz }: { startDate: Date; lat: number; lng: number; tz: string }) {
  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => addD(startDate, i)), [startDate]);
  const todayStr = fd(new Date());

  const queries = useQueries({
    queries: days.map(d => ({
      queryKey: ['panchang-weekly', fd(d), lat, lng, tz],
      queryFn: async () => { const r = await apiClient.get<{ detailed_panchang?: PanchangDetail } & PanchangDetail>(`/api/v1/panchang/?date=${encodeURIComponent(fd(d) + 'T06:00:00')}&latitude=${lat}&longitude=${lng}&timezone=${encodeURIComponent(tz)}`); return { date: d, p: (r.data?.detailed_panchang || r.data) as PanchangDetail }; },
      staleTime: 1000 * 60 * 30,
    })),
  });

  return (
    <div>
      {queries.some(q => q.isLoading) && <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}><Spinner /><span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading week...</span></div>}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(125px, 1fr))', gap: 10 }}>
        {queries.map((q, i) => {
          const d = days[i], ds = fd(d), isToday = ds === todayStr, p = q.data?.p, qual = p ? dayQuality(p) : null;
          return (
            <div key={ds} style={{ ...cardS, padding: '14px 12px', textAlign: 'center', borderColor: isToday ? 'var(--gold)' : 'var(--border)', boxShadow: isToday ? '0 0 0 1px var(--gold), 0 0 12px rgba(200,145,58,0.1)' : 'var(--shadow-card)' }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: isToday ? 'var(--gold)' : 'var(--text-primary)', marginBottom: 2 }}>{DAYS_SHORT[d.getDay()]}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 10 }}>{d.getDate()} {MONTHS[d.getMonth()].slice(0, 3)}</div>
              {q.isLoading ? <div className="animate-pulse" style={{ height: 8, borderRadius: 4, background: 'var(--border-subtle)', marginBottom: 10 }} />
                : qual ? <div style={{ width: 10, height: 10, borderRadius: '50%', background: qual.color, margin: '0 auto 10px', boxShadow: `0 0 6px ${qual.color}` }} />
                : <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--border)', margin: '0 auto 10px' }} />}
              {p?.auspicious_times?.abhijit_muhurta && <div style={{ fontSize: 10, color: 'var(--gold)', fontWeight: 500, marginBottom: 4 }}>{p.auspicious_times.abhijit_muhurta.split(/\s*[-\u2013]\s*/)[0]?.trim()} best</div>}
              {p?.inauspicious_times?.rahu_kaal && <div style={{ fontSize: 9, color: 'var(--red)', fontWeight: 500 }}>Rahu: {p.inauspicious_times.rahu_kaal}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
