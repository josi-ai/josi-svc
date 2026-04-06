'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  type MuhurtaResult,
  cardS, labelS, inputS,
  fd, addD, Spinner,
} from './muhurta-shared';

export function ActivitySearch({ lat, lng, tz }: { lat: number; lng: number; tz: string }) {
  const [activity, setActivity] = useState('marriage');
  const [sd, setSd] = useState(() => fd(new Date()));
  const [ed, setEd] = useState(() => fd(addD(new Date(), 7)));
  const { data: actData } = useQuery({ queryKey: ['muhurta-activities'], queryFn: () => apiClient.get<{ activities: { name: string; description: string }[] }>('/api/v1/muhurta/activities') });
  const acts = actData?.data?.activities || [];
  const mut = useMutation({ mutationFn: () => apiClient.post<MuhurtaResult>('/api/v1/muhurta/find-muhurta', { purpose: activity, start_date: `${sd}T00:00:00`, end_date: `${ed}T23:59:59`, latitude: lat, longitude: lng, timezone: tz, max_results: 20 }) });
  const res = mut.data?.data;
  const selS: React.CSSProperties = { ...inputS, appearance: 'none' as const, backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235B6A8A' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', paddingRight: 36 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={cardS}>
        <h3 className="font-display" style={{ fontSize: 18, fontWeight: 400, color: 'var(--text-primary)', marginTop: 0, marginBottom: 20 }}>Find Auspicious Times</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          <div><label style={labelS}>Activity</label><select value={activity} onChange={e => setActivity(e.target.value)} style={selS}>
            {acts.length > 0 ? acts.map(a => <option key={a.name} value={a.name}>{a.name.charAt(0).toUpperCase() + a.name.slice(1)}</option>) : ['Marriage','Business','Travel','Education','Medical','Property'].map(a => <option key={a} value={a.toLowerCase()}>{a}</option>)}
          </select></div>
          <div><label style={labelS}>Start Date</label><input type="date" value={sd} onChange={e => setSd(e.target.value)} style={inputS} /></div>
          <div><label style={labelS}>End Date</label><input type="date" value={ed} onChange={e => setEd(e.target.value)} style={inputS} /></div>
        </div>
        <button onClick={() => mut.mutate()} disabled={mut.isPending} style={{ marginTop: 20, padding: '12px 32px', fontSize: 15, fontWeight: 600, color: 'var(--primary-foreground)', background: 'var(--gold)', border: 'none', borderRadius: 10, cursor: mut.isPending ? 'not-allowed' : 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          {mut.isPending ? <><Spinner /> Searching...</> : 'Find Auspicious Times'}
        </button>
        {mut.isError && <div style={{ marginTop: 16, padding: '10px 14px', borderRadius: 8, fontSize: 13, color: 'var(--red)', background: 'var(--red-bg)' }}>{(mut.error as Error)?.message || 'Search failed'}</div>}
      </div>

      {res && (
        <div style={cardS}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{res.total_found} result{res.total_found !== 1 ? 's' : ''}</h3>
            <span style={{ fontSize: 12, color: 'var(--text-faint)' }}>{res.search_criteria.purpose} &middot; {res.search_criteria.date_range}</span>
          </div>
          {res.muhurtas.length === 0 ? <p style={{ fontSize: 13, color: 'var(--text-muted)', textAlign: 'center', padding: '20px 0' }}>No times found. Try a wider date range.</p> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {res.muhurtas.map((m, i) => (
                <div key={i} style={{ padding: '16px 20px', borderRadius: 10, background: 'var(--background)', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>{m.date || `Window ${i + 1}`}</div>
                      {(m.start_time || m.end_time) && <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>{m.start_time}{m.end_time ? ` - ${m.end_time}` : ''}</div>}
                    </div>
                    {typeof m.score === 'number' && <div style={{ minWidth: 120, display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ flex: 1, height: 6, borderRadius: 3, background: 'var(--border)' }}><div style={{ width: `${Math.min(m.score, 100)}%`, height: '100%', borderRadius: 3, background: m.score >= 80 ? 'var(--green)' : m.score >= 60 ? 'var(--gold)' : 'var(--red)' }} /></div>
                      <span style={{ fontSize: 12, fontWeight: 600, color: m.score >= 80 ? 'var(--green)' : m.score >= 60 ? 'var(--gold)' : 'var(--red)', minWidth: 28 }}>{m.score}</span>
                    </div>}
                  </div>
                  {(m.tithi || m.nakshatra || m.yoga) && <div style={{ display: 'flex', gap: 16, marginTop: 8, flexWrap: 'wrap' }}>
                    {m.tithi && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Tithi: <span style={{ color: 'var(--text-secondary)' }}>{m.tithi}</span></span>}
                    {m.nakshatra && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Nakshatra: <span style={{ color: 'var(--text-secondary)' }}>{m.nakshatra}</span></span>}
                  </div>}
                  {(m.reason || m.explanation) && <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8, marginBottom: 0, lineHeight: 1.5 }}>{m.reason || m.explanation}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
