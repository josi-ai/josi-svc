'use client';

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

/* ── Types ─────────────────────────────────────────────────────── */

export interface PanchangDetail {
  sunrise: string; sunset: string;
  tithi?: { name?: string }; nakshatra?: { name?: string }; yoga?: { name?: string };
  inauspicious_times: { rahu_kaal: string; gulika_kaal: string; yamaganda: string };
  auspicious_times: { abhijit_muhurta: string; brahma_muhurta: string };
}
export interface DayQuality { date: string; quality: string; score?: number; tithi?: string; nakshatra?: string }
export interface MonthlyData { month: number; year: number; days: DayQuality[] }
export interface MuhurtaWindow { date?: string; start_time?: string; end_time?: string; score?: number; quality?: string; tithi?: string; nakshatra?: string; yoga?: string; reason?: string; explanation?: string; [k: string]: unknown }
export interface MuhurtaResult { muhurtas: MuhurtaWindow[]; search_criteria: { purpose: string; date_range: string }; total_found: number }

/* ── Constants ────────────────────────────────────────────────── */

export const DS = 360;
export const DE = 1080; // 6AM, 6PM in minutes
export const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
export const DAYS_SHORT = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

export type SegT = 'auspicious' | 'rahu' | 'gulika' | 'yamaganda' | 'abhijit';
export interface Seg { s: number; e: number; t: SegT; l: string }
export const SEG_CLR: Record<string, string> = { auspicious: 'var(--bar-good)', rahu: 'var(--bar-avoid)', gulika: 'var(--bar-avoid)', yamaganda: 'var(--bar-avoid)', abhijit: 'var(--bar-special)' };

export const PERIOD_META: Record<string, { icon: string; color: string; status: string; desc: string }> = {
  'Brahma Muhurta': { icon: '\uD83C\uDF1F', color: 'var(--gold)', status: 'Auspicious', desc: 'Ideal for meditation, prayer, and spiritual practice.' },
  'Sunrise': { icon: '\u2600\uFE0F', color: 'var(--gold)', status: 'Auspicious', desc: 'Sacred transition marking the start of the day.' },
  'Rahu Kaal': { icon: '\u26A0\uFE0F', color: 'var(--red)', status: 'Inauspicious', desc: 'Avoid starting new ventures or important activities.' },
  'Abhijit Muhurta': { icon: '\u2726', color: 'var(--gold)', status: 'Auspicious', desc: 'The most auspicious muhurta for all activities.' },
  'Gulika Kaal': { icon: '\u26A0\uFE0F', color: 'var(--red)', status: 'Inauspicious', desc: 'Generally unfavorable; avoid initiating important tasks.' },
  'Yamaganda': { icon: '\u26A0\uFE0F', color: 'var(--red)', status: 'Inauspicious', desc: 'Ruled by Yama; avoid travel and risky undertakings.' },
  'Sunset': { icon: '\uD83C\uDF05', color: 'var(--text-muted)', status: 'Transition', desc: 'Sandhya kaal \u2014 time for evening prayers.' },
};

export const cardS: React.CSSProperties = { background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 24 };
export const labelS: React.CSSProperties = { display: 'block', fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--text-faint)', marginBottom: 6 };
export const inputS: React.CSSProperties = { width: '100%', padding: '10px 14px', fontSize: 14, color: 'var(--text-primary)', background: 'var(--background)', border: '1px solid var(--border)', borderRadius: 8, outline: 'none' };

/* ── Helpers ──────────────────────────────────────────────────── */

export function pt(s: string): number {
  if (!s) return 0;
  const ap = s.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (ap) { let h = +ap[1]; if (ap[3].toUpperCase() === 'PM' && h !== 12) h += 12; if (ap[3].toUpperCase() === 'AM' && h === 12) h = 0; return h * 60 + +ap[2]; }
  const h24 = s.match(/^(\d{1,2}):(\d{2})/); return h24 ? +h24[1] * 60 + +h24[2] : 0;
}
export function ft(m: number) { const h = Math.floor(m / 60), mn = m % 60, p = h >= 12 ? 'PM' : 'AM'; return `${h === 0 ? 12 : h > 12 ? h - 12 : h}:${String(mn).padStart(2, '0')} ${p}`; }
export function pr(s: string) { const p = s.split(/\s*[-\u2013]\s*/); if (p.length !== 2) return null; const a = pt(p[0].trim()), b = pt(p[1].trim()); return a && b && a < b ? { start: a, end: b } : null; }
export function fd(d: Date) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }
export function addD(d: Date, n: number) { const r = new Date(d); r.setDate(r.getDate() + n); return r; }

export function buildSegs(d: PanchangDetail): Seg[] {
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

export function dayQuality(d: PanchangDetail) {
  const ti = (d.tithi?.name || '').toLowerCase(), yo = (d.yoga?.name || '').toLowerCase();
  if (['rikta','nanda','bhadra'].some(k => ti.includes(k)) || ['vyatipata','vaidhriti'].some(k => yo.includes(k)))
    return { label: 'Inauspicious', color: 'var(--red)', bg: 'var(--red-bg)' };
  if (['poorna','shukla'].some(k => ti.includes(k)) || ['siddhi','amrita'].some(k => yo.includes(k)))
    return { label: 'Auspicious', color: 'var(--green)', bg: 'var(--green-bg)' };
  return { label: 'Mixed', color: 'var(--gold)', bg: 'var(--gold-bg)' };
}

/* ── Shared sub-components ────────────────────────────────────── */

export function Spinner() {
  return (<><svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: 'spin 1s linear infinite' }}><circle cx="12" cy="12" r="10" stroke="var(--text-muted)" strokeWidth="3" strokeLinecap="round" strokeDasharray="31.42 31.42" /></svg><style>{`@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}`}</style></>);
}

export function NavArrow({ dir, onClick }: { dir: 'left' | 'right'; onClick: () => void }) {
  const I = dir === 'left' ? ChevronLeft : ChevronRight;
  return (<button onClick={onClick} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8, width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-secondary)' }}><I style={{ width: 16, height: 16 }} /></button>);
}

export function TimelineBar({ segments, height = 40 }: { segments: Seg[]; height?: number }) {
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
