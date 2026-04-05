'use client';

import { useState, useMemo, useCallback } from 'react';
import { useQuery, useQueries, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useDefaultProfile } from '@/hooks/use-default-profile';
import { TimeframeSelector } from '@/components/ui/timeframe-selector';
import { ChevronLeft, ChevronRight } from 'lucide-react';

/* ── Types ─────────────────────────────────────────────────────── */

interface PanchangDetail {
  sunrise: string; sunset: string;
  tithi?: { name?: string }; nakshatra?: { name?: string }; yoga?: { name?: string };
  inauspicious_times: { rahu_kaal: string; gulika_kaal: string; yamaganda: string };
  auspicious_times: { abhijit_muhurta: string; brahma_muhurta: string };
}
interface DayQuality { date: string; quality: string; score?: number; tithi?: string; nakshatra?: string }
interface MonthlyData { month: number; year: number; days: DayQuality[] }
interface MuhurtaWindow { date?: string; start_time?: string; end_time?: string; score?: number; quality?: string; tithi?: string; nakshatra?: string; yoga?: string; reason?: string; explanation?: string; [k: string]: any }
interface MuhurtaResult { muhurtas: MuhurtaWindow[]; search_criteria: { purpose: string; date_range: string }; total_found: number }

/* ── Helpers ───────────────────────────────────────────────────── */

const DS = 360, DE = 1080; // 6AM, 6PM in minutes
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const DAYS_SHORT = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

function pt(s: string): number {
  if (!s) return 0;
  const ap = s.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (ap) { let h = +ap[1]; if (ap[3].toUpperCase() === 'PM' && h !== 12) h += 12; if (ap[3].toUpperCase() === 'AM' && h === 12) h = 0; return h * 60 + +ap[2]; }
  const h24 = s.match(/^(\d{1,2}):(\d{2})/); return h24 ? +h24[1] * 60 + +h24[2] : 0;
}
function ft(m: number) { const h = Math.floor(m / 60), mn = m % 60, p = h >= 12 ? 'PM' : 'AM'; return `${h === 0 ? 12 : h > 12 ? h - 12 : h}:${String(mn).padStart(2, '0')} ${p}`; }
function pr(s: string) { const p = s.split(/\s*[-\u2013]\s*/); if (p.length !== 2) return null; const a = pt(p[0].trim()), b = pt(p[1].trim()); return a && b && a < b ? { start: a, end: b } : null; }
function fd(d: Date) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }
function addD(d: Date, n: number) { const r = new Date(d); r.setDate(r.getDate() + n); return r; }

type SegT = 'auspicious' | 'rahu' | 'gulika' | 'yamaganda' | 'abhijit';
interface Seg { s: number; e: number; t: SegT; l: string }
const SEG_CLR: Record<string, string> = { auspicious: 'var(--bar-good)', rahu: 'var(--bar-avoid)', gulika: 'var(--bar-avoid)', yamaganda: 'var(--bar-avoid)', abhijit: 'var(--bar-special)' };

function buildSegs(d: PanchangDetail): Seg[] {
  const ps: Seg[] = [];
  const add = (str: string, t: SegT, l: string) => { const r = pr(str); if (r && r.start < DE && r.end > DS) ps.push({ s: Math.max(r.start, DS), e: Math.min(r.end, DE), t, l }); };
  add(d.inauspicious_times?.rahu_kaal || '', 'rahu', 'Rahu Kaal');
  add(d.inauspicious_times?.gulika_kaal || '', 'gulika', 'Gulika Kaal');
  add(d.inauspicious_times?.yamaganda || '', 'yamaganda', 'Yamaganda');
  add(d.auspicious_times?.abhijit_muhurta || '', 'abhijit', 'Abhijit Muhurta');
  ps.sort((a, b) => a.s - b.s);
  const segs: Seg[] = []; let c = DS;
  for (const p of ps) { if (c < p.s) segs.push({ s: c, e: p.s, t: 'auspicious', l: 'Favorable' }); segs.push(p); c = p.e; }
  if (c < DE) segs.push({ s: c, e: DE, t: 'auspicious', l: 'Favorable' }); return segs;
}

function dayQuality(d: PanchangDetail) {
  const ti = (d.tithi?.name || '').toLowerCase(), yo = (d.yoga?.name || '').toLowerCase();
  if (['rikta','nanda','bhadra'].some(k => ti.includes(k)) || ['vyatipata','vaidhriti'].some(k => yo.includes(k)))
    return { label: 'Inauspicious', color: 'var(--red)', bg: 'var(--red-bg)' };
  if (['poorna','shukla'].some(k => ti.includes(k)) || ['siddhi','amrita'].some(k => yo.includes(k)))
    return { label: 'Auspicious', color: 'var(--green)', bg: 'var(--green-bg)' };
  return { label: 'Mixed', color: 'var(--gold)', bg: 'var(--gold-bg)' };
}

const cardS: React.CSSProperties = { background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 24 };
const labelS: React.CSSProperties = { display: 'block', fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--text-faint)', marginBottom: 6 };
const inputS: React.CSSProperties = { width: '100%', padding: '10px 14px', fontSize: 14, color: 'var(--text-primary)', background: 'var(--background)', border: '1px solid var(--border)', borderRadius: 8, outline: 'none' };

const PERIOD_META: Record<string, { icon: string; color: string; status: string; desc: string }> = {
  'Brahma Muhurta': { icon: '\uD83C\uDF1F', color: 'var(--gold)', status: 'Auspicious', desc: 'Ideal for meditation, prayer, and spiritual practice.' },
  'Sunrise': { icon: '\u2600\uFE0F', color: 'var(--gold)', status: 'Auspicious', desc: 'Sacred transition marking the start of the day.' },
  'Rahu Kaal': { icon: '\u26A0\uFE0F', color: 'var(--red)', status: 'Inauspicious', desc: 'Avoid starting new ventures or important activities.' },
  'Abhijit Muhurta': { icon: '\u2726', color: 'var(--gold)', status: 'Auspicious', desc: 'The most auspicious muhurta for all activities.' },
  'Gulika Kaal': { icon: '\u26A0\uFE0F', color: 'var(--red)', status: 'Inauspicious', desc: 'Generally unfavorable; avoid initiating important tasks.' },
  'Yamaganda': { icon: '\u26A0\uFE0F', color: 'var(--red)', status: 'Inauspicious', desc: 'Ruled by Yama; avoid travel and risky undertakings.' },
  'Sunset': { icon: '\uD83C\uDF05', color: 'var(--text-muted)', status: 'Transition', desc: 'Sandhya kaal \u2014 time for evening prayers.' },
};

/* ── Shared sub-components ─────────────────────────────────────── */

function Spinner() {
  return (<><svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: 'spin 1s linear infinite' }}><circle cx="12" cy="12" r="10" stroke="var(--text-muted)" strokeWidth="3" strokeLinecap="round" strokeDasharray="31.42 31.42" /></svg><style>{`@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}`}</style></>);
}

function NavArrow({ dir, onClick }: { dir: 'left' | 'right'; onClick: () => void }) {
  const I = dir === 'left' ? ChevronLeft : ChevronRight;
  return (<button onClick={onClick} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8, width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-secondary)' }}><I style={{ width: 16, height: 16 }} /></button>);
}

/* ── Timeline Bar ──────────────────────────────────────────────── */

function TimelineBar({ segments, height = 40 }: { segments: Seg[]; height?: number }) {
  const now = new Date(), nM = now.getHours() * 60 + now.getMinutes(), inR = nM >= DS && nM <= DE, pct = inR ? ((nM - DS) / (DE - DS)) * 100 : 0;
  return (
    <div>
      <div style={{ position: 'relative', height, borderRadius: 4, overflow: 'hidden', display: 'flex', background: 'var(--border-subtle)' }}>
        {segments.map((seg, i) => (
          <div key={i} style={{ flex: seg.e - seg.s, background: SEG_CLR[seg.t] || 'var(--bar-neutral)', minWidth: 1, position: 'relative' }} title={`${seg.l}: ${ft(seg.s)} \u2013 ${ft(seg.e)}`}>
            {(seg.e - seg.s) > 50 && height >= 30 && <span style={{ position: 'absolute', left: 6, top: '50%', transform: 'translateY(-50%)', fontSize: 9, fontWeight: 600, color: 'rgba(255,255,255,0.8)', whiteSpace: 'nowrap', textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}>{seg.l}</span>}
          </div>
        ))}
        {inR && <div style={{ position: 'absolute', top: 0, bottom: 0, left: `${pct}%`, width: 2, background: 'var(--gold-bright)', boxShadow: '0 0 8px rgba(212,160,74,0.6)', zIndex: 2 }}><div style={{ position: 'absolute', top: -4, left: -3, width: 8, height: 8, borderRadius: '50%', background: 'var(--gold-bright)' }} /></div>}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: 'var(--text-faint)', marginTop: 4, padding: '0 2px' }}>
        {['6 AM','8 AM','10 AM','12 PM','2 PM','4 PM','6 PM'].map(l => <span key={l}>{l}</span>)}
      </div>
    </div>
  );
}

/* ── Daily View ────────────────────────────────────────────────── */

function DailyView({ date, lat, lng, tz }: { date: string; lat: number; lng: number; tz: string }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['panchang-daily', date, lat, lng, tz],
    queryFn: async () => { const r = await apiClient.get<any>(`/api/v1/panchang/?date=${encodeURIComponent(date + 'T06:00:00')}&latitude=${lat}&longitude=${lng}&timezone=${encodeURIComponent(tz)}`); return (r.data?.detailed_panchang || r.data) as PanchangDetail; },
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
      {/* Quality + Timeline */}
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

      {/* Period cards */}
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

      {/* Recommendations */}
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

/* ── Weekly View ───────────────────────────────────────────────── */

function WeeklyView({ startDate, lat, lng, tz }: { startDate: Date; lat: number; lng: number; tz: string }) {
  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => addD(startDate, i)), [startDate]);
  const todayStr = fd(new Date());

  const queries = useQueries({
    queries: days.map(d => ({
      queryKey: ['panchang-weekly', fd(d), lat, lng, tz],
      queryFn: async () => { const r = await apiClient.get<any>(`/api/v1/panchang/?date=${encodeURIComponent(fd(d) + 'T06:00:00')}&latitude=${lat}&longitude=${lng}&timezone=${encodeURIComponent(tz)}`); return { date: d, p: (r.data?.detailed_panchang || r.data) as PanchangDetail }; },
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

/* ── Monthly View ──────────────────────────────────────────────── */

function MonthlyView({ year, month, lat, lng, tz, onSelectDay }: { year: number; month: number; lat: number; lng: number; tz: string; onSelectDay: (d: string) => void }) {
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

/* ── Activity Search ───────────────────────────────────────────── */

function ActivitySearch({ lat, lng, tz }: { lat: number; lng: number; tz: string }) {
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
        <button onClick={() => mut.mutate()} disabled={mut.isPending} style={{ marginTop: 20, padding: '12px 32px', fontSize: 15, fontWeight: 600, color: '#060A14', background: 'var(--gold)', border: 'none', borderRadius: 10, cursor: mut.isPending ? 'not-allowed' : 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
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

/* ── Main Page ─────────────────────────────────────────────────── */

export default function MuhurtaPage() {
  const { location, isLoading: pl } = useDefaultProfile();
  const [tf, setTf] = useState('Daily');
  const [selDate, setSelDate] = useState(() => new Date());
  const [weekStart, setWeekStart] = useState(() => { const d = new Date(); d.setDate(d.getDate() - d.getDay()); return d; });
  const [mo, setMo] = useState(0);
  const vm = useMemo(() => { const d = new Date(); d.setMonth(d.getMonth() + mo); return d; }, [mo]);

  const goDay = useCallback((ds: string) => { setSelDate(new Date(ds + 'T12:00:00')); setTf('Daily'); }, []);
  const nav = (dir: number) => { if (tf === 'Daily') setSelDate(p => addD(p, dir)); else if (tf === 'Weekly') setWeekStart(p => addD(p, dir * 7)); else setMo(p => p + dir); };

  const dateLabel = tf === 'Daily' ? selDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
    : tf === 'Weekly' ? `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} \u2013 ${addD(weekStart, 6).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
    : `${MONTHS[vm.getMonth()]} ${vm.getFullYear()}`;

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 16px 48px' }}>
      {/* Hero */}
      <section style={{ padding: '48px 24px 36px', textAlign: 'center', marginBottom: 28, background: 'radial-gradient(ellipse at 50% 0%, rgba(200,145,58,0.08) 0%, transparent 70%)' }}>
        <h1 className="font-display" style={{ fontSize: 32, fontWeight: 400, color: 'var(--text-primary)', margin: 0, lineHeight: 1.2 }}>Muhurta</h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8, marginBottom: 0, maxWidth: 480, marginLeft: 'auto', marginRight: 'auto' }}>
          Vedic electional astrology &mdash; find the most auspicious moments for every important decision
        </p>
      </section>

      <TimeframeSelector value={tf} onChange={setTf} options={['Daily', 'Weekly', 'Monthly']} style={{ marginBottom: 20 }} />

      {/* Date nav */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16, marginBottom: 24 }}>
        <NavArrow dir="left" onClick={() => nav(-1)} />
        <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', minWidth: 200, textAlign: 'center' }}>{dateLabel}</span>
        <NavArrow dir="right" onClick={() => nav(1)} />
        {tf === 'Daily' && fd(selDate) !== fd(new Date()) && (
          <button onClick={() => setSelDate(new Date())} style={{ padding: '5px 12px', fontSize: 11, fontWeight: 600, color: 'var(--gold)', background: 'var(--gold-bg)', border: '1px solid rgba(200,145,58,0.2)', borderRadius: 6, cursor: 'pointer' }}>Today</button>
        )}
      </div>

      {pl ? (
        <div style={{ ...cardS, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 40 }}><Spinner /><span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading profile...</span></div>
      ) : (
        <>
          {tf === 'Daily' && <DailyView date={fd(selDate)} lat={location.latitude} lng={location.longitude} tz={location.timezone} />}
          {tf === 'Weekly' && <WeeklyView startDate={weekStart} lat={location.latitude} lng={location.longitude} tz={location.timezone} />}
          {tf === 'Monthly' && <MonthlyView year={vm.getFullYear()} month={vm.getMonth()} lat={location.latitude} lng={location.longitude} tz={location.timezone} onSelectDay={goDay} />}
          <div style={{ marginTop: 36 }}><ActivitySearch lat={location.latitude} lng={location.longitude} tz={location.timezone} /></div>
        </>
      )}
    </div>
  );
}
