'use client';

import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  type MonthlyData, type DayQuality,
  cardS, DAYS_SHORT, fd, Spinner,
} from './muhurta-shared';

export function MonthlyView({ year, month, lat, lng, tz, onSelectDay }: { year: number; month: number; lat: number; lng: number; tz: string; onSelectDay: (d: string) => void }) {
  const firstDay = new Date(year, month, 1).getDay(), daysInMonth = new Date(year, month + 1, 0).getDate(), todayStr = fd(new Date());
  const { data: calRes, isLoading, isError } = useQuery({
    queryKey: ['muhurta-monthly', year, month, lat, lng, tz],
    queryFn: () => apiClient.post<MonthlyData>('/api/v1/muhurta/monthly-calendar', { year, month: month + 1, latitude: lat, longitude: lng, timezone: tz }),
    retry: false, staleTime: 1000 * 60 * 60,
  });
  const dayMap = useMemo(() => { const m: Record<number, DayQuality> = {}; calRes?.data?.days?.forEach(d => { m[new Date(d.date).getDate()] = d; }); return m; }, [calRes]);
  const qC = (q: string) => q === 'auspicious' ? 'var(--green)' : q === 'inauspicious' ? 'var(--red)' : 'var(--gold)';
  const qB = (q: string) => q === 'auspicious' ? 'var(--green-bg)' : q === 'inauspicious' ? 'var(--red-bg)' : 'var(--gold-bg)';

  return (
    <div style={{ ...cardS, padding: 0, overflow: 'hidden' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', borderBottom: '1px solid var(--border)' }}>
        {DAYS_SHORT.map(d => <div key={d} style={{ padding: '10px 4px', textAlign: 'center', fontSize: 10, fontWeight: 600, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8 }}>{d}</div>)}
      </div>
      {isError ? (
        <div style={{ padding: '40px 24px', textAlign: 'center' }}><p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>Monthly calendar unavailable. Use the activity search below.</p></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)' }}>
          {Array.from({ length: firstDay }).map((_, i) => <div key={`e${i}`} style={{ minHeight: 64, borderTop: '1px solid var(--border)' }} />)}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1, ds = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`, isToday = ds === todayStr, info = dayMap[day], dot = info?.quality ? qC(info.quality) : undefined;
            return (
              <div key={day} onClick={() => onSelectDay(ds)} style={{ minHeight: 64, padding: '6px', cursor: 'pointer', borderTop: '1px solid var(--border)', borderLeft: (firstDay + i) % 7 !== 0 ? '1px solid var(--border)' : 'none', background: isToday ? 'var(--gold-bg)' : info?.quality ? qB(info.quality) : 'transparent', transition: 'background 0.15s' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span style={{ fontSize: 12, fontWeight: isToday ? 700 : 400, color: isToday ? 'var(--gold)' : 'var(--text-secondary)' }}>{day}</span>
                  {dot && <div style={{ width: 6, height: 6, borderRadius: '50%', background: dot }} />}
                </div>
                {info?.tithi && <div style={{ fontSize: 8, color: 'var(--text-faint)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{info.tithi}</div>}
              </div>
            );
          })}
        </div>
      )}
      {isLoading && <div style={{ padding: '10px 20px', textAlign: 'center', borderTop: '1px solid var(--border)' }}><div style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}><Spinner /><span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Loading...</span></div></div>}
      <div style={{ display: 'flex', gap: 16, padding: '10px 20px', borderTop: '1px solid var(--border)', flexWrap: 'wrap' }}>
        {[{ c: 'var(--green)', l: 'Auspicious' }, { c: 'var(--gold)', l: 'Mixed' }, { c: 'var(--red)', l: 'Inauspicious' }].map(x => (
          <div key={x.l} style={{ display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width: 6, height: 6, borderRadius: '50%', background: x.c }} /><span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{x.l}</span></div>
        ))}
        <span style={{ fontSize: 10, color: 'var(--text-faint)', marginLeft: 'auto' }}>Click a day for details</span>
      </div>
    </div>
  );
}
