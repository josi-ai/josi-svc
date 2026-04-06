'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  type PanchangDetail,
  cardS, PERIOD_META,
  buildSegs, dayQuality,
  Spinner, TimelineBar,
} from './muhurta-shared';

export function DailyView({ date, lat, lng, tz }: { date: string; lat: number; lng: number; tz: string }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['panchang-daily', date, lat, lng, tz],
    queryFn: async () => { const r = await apiClient.get<{ detailed_panchang?: PanchangDetail } & PanchangDetail>(`/api/v1/panchang/?date=${encodeURIComponent(date + 'T06:00:00')}&latitude=${lat}&longitude=${lng}&timezone=${encodeURIComponent(tz)}`); return (r.data?.detailed_panchang || r.data) as PanchangDetail; },
    staleTime: 1000 * 60 * 30,
  });

  if (isLoading) return <div style={{ ...cardS, display: 'flex', alignItems: 'center', gap: 8 }}><Spinner /><span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading...</span></div>;
  if (isError || !data) return <div style={cardS}><p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>Could not load data for this date.</p></div>;

  const q = dayQuality(data), segs = buildSegs(data);
  const periods: { name: string; time: string }[] = [];
  if (data.auspicious_times?.brahma_muhurta) periods.push({ name: 'Brahma Muhurta', time: data.auspicious_times.brahma_muhurta });
  if (data.sunrise) periods.push({ name: 'Sunrise', time: data.sunrise });
  if (data.inauspicious_times?.rahu_kaal) periods.push({ name: 'Rahu Kaal', time: data.inauspicious_times.rahu_kaal });
  if (data.auspicious_times?.abhijit_muhurta) periods.push({ name: 'Abhijit Muhurta', time: data.auspicious_times.abhijit_muhurta });
  if (data.inauspicious_times?.gulika_kaal) periods.push({ name: 'Gulika Kaal', time: data.inauspicious_times.gulika_kaal });
  if (data.inauspicious_times?.yamaganda) periods.push({ name: 'Yamaganda', time: data.inauspicious_times.yamaganda });
  if (data.sunset) periods.push({ name: 'Sunset', time: data.sunset });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={cardS}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <span style={{ padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, background: q.bg, color: q.color }}>{q.label}</span>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            {data.tithi?.name && `Tithi: ${data.tithi.name}`}{data.yoga?.name && ` \u00B7 Yoga: ${data.yoga.name}`}{data.nakshatra?.name && ` \u00B7 ${data.nakshatra.name}`}
          </span>
        </div>
        <TimelineBar segments={segs} height={40} />
        <div style={{ display: 'flex', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
          {[{ l: 'Favorable', c: 'var(--bar-good)' }, { l: 'Inauspicious', c: 'var(--bar-avoid)' }, { l: 'Abhijit', c: 'var(--bar-special)' }].map(x => (
            <div key={x.l} style={{ display: 'flex', alignItems: 'center', gap: 5 }}><div style={{ width: 8, height: 8, borderRadius: 2, background: x.c }} /><span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{x.l}</span></div>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12 }}>
        {periods.map(p => {
          const m = PERIOD_META[p.name] || { icon: '\u23F0', color: 'var(--text-muted)', status: '', desc: '' };
          const bad = m.status === 'Inauspicious';
          return (
            <div key={p.name} style={{ ...cardS, padding: '16px 18px', borderLeft: `3px solid ${m.color}`, background: bad ? 'var(--red-bg)' : m.status === 'Auspicious' ? 'var(--gold-bg)' : 'var(--card)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <span style={{ fontSize: 16 }}>{m.icon}</span>
                <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{p.name}</span>
                {m.status && <span style={{ marginLeft: 'auto', fontSize: 10, fontWeight: 600, padding: '2px 8px', borderRadius: 10, background: bad ? 'rgba(196,93,74,0.15)' : 'rgba(106,175,122,0.15)', color: m.color }}>{m.status}</span>}
              </div>
              <div style={{ fontSize: 13, fontWeight: 500, color: m.color, marginBottom: 4 }}>{p.time}</div>
              {m.desc && <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.5 }}>{m.desc}</div>}
            </div>
          );
        })}
      </div>

      <div style={cardS}>
        <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 12 }}>Activity Recommendations</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--green)', marginBottom: 8 }}>Good for</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {['Spiritual practice', 'Education', 'Charity'].map(a => <span key={a} style={{ padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 500, background: 'var(--green-bg)', color: 'var(--green)' }}>{a}</span>)}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--red)', marginBottom: 8 }}>Avoid</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {['Major purchases', 'Travel'].map(a => <span key={a} style={{ padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 500, background: 'var(--red-bg)', color: 'var(--red)' }}>{a}</span>)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
