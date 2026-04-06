'use client';

import type { DashaPeriod, CurrentDasha } from './dasha-types';
import { pColor, parseDate, fmtDate, HEADING, CARD, LABEL } from './dasha-helpers';

/* ---------- Shared ---------- */

export function SkeletonBar({ width, height = 40 }: { width: string; height?: number }) {
  return <div style={{ width, height, borderRadius: 8, background: 'var(--border)', animation: 'pulse 1.5s ease-in-out infinite' }} />;
}

export function PeriodBlock({ label, period }: { label: string; period: DashaPeriod }) {
  const remaining = period.remaining_days;
  const remLabel = remaining != null
    ? (remaining > 365 ? `${Math.round(remaining / 365.25 * 10) / 10} years remaining` : `${remaining} days remaining`)
    : null;

  return (
    <div style={{ flex: 1, minWidth: 160 }}>
      <p style={LABEL}>{label}</p>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{ width: 12, height: 12, borderRadius: 3, background: pColor(period.planet) }} />
        <span style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>{period.planet}</span>
      </div>
      <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>{fmtDate(period.start_date)} \u2013 {fmtDate(period.end_date)}</p>
      {remLabel && <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 4 }}>{remLabel}</p>}
    </div>
  );
}

/* ---------- Mahadasha Timeline ---------- */

export function MahadashaTimeline({ periods, currentPlanet, onPlanetClick }: { periods: DashaPeriod[]; currentPlanet?: string; onPlanetClick?: (period: DashaPeriod) => void }) {
  const firstStart = parseDate(periods[0]?.start_date);
  if (!firstStart || periods.length === 0) return null;

  const endMs = firstStart.getTime() + 120 * 365.25 * 86400000;
  const totalMs = endMs - firstStart.getTime();
  const visible = periods.filter((p) => { const s = parseDate(p.start_date); return s && s.getTime() < endMs; });

  const ticks: { year: number; pct: number }[] = [];
  for (let y = Math.ceil(firstStart.getFullYear() / 10) * 10; y <= firstStart.getFullYear() + 120; y += 10) {
    const pct = ((new Date(y, 0, 1).getTime() - firstStart.getTime()) / totalMs) * 100;
    if (pct >= 0 && pct <= 100) ticks.push({ year: y, pct });
  }
  const nowPct = ((Date.now() - firstStart.getTime()) / totalMs) * 100;

  return (
    <div style={CARD}>
      <h3 style={HEADING}>Mahadasha Timeline</h3>
      <div style={{ position: 'relative', height: 44, borderRadius: 8, overflow: 'hidden', background: 'var(--background)', marginBottom: 8 }}>
        {visible.map((p, i) => {
          const s = parseDate(p.start_date)!.getTime();
          const e = Math.min(parseDate(p.end_date)!.getTime(), endMs);
          const left = ((s - firstStart.getTime()) / totalMs) * 100;
          const w = ((e - s) / totalMs) * 100;
          const cur = p.planet === currentPlanet;
          return (
            <div key={`${p.planet}-${i}`} title={`${p.planet}: ${fmtDate(p.start_date)} \u2013 ${fmtDate(p.end_date)}`}
              onClick={() => onPlanetClick?.(p)}
              style={{
              position: 'absolute', left: `${left}%`, width: `${w}%`, top: 0, bottom: 0,
              background: pColor(p.planet), opacity: cur ? 1 : 0.6,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderLeft: i > 0 ? '1px solid var(--background)' : 'none',
              cursor: 'pointer',
              ...(cur ? { outline: '2px solid var(--gold)', outlineOffset: -2, zIndex: 2 } : {}),
            }}>
              {w > 5 && <span style={{ fontSize: w > 8 ? 11 : 9, color: '#fff', fontWeight: 600, textShadow: '0 1px 2px rgba(0,0,0,0.5)', whiteSpace: 'nowrap', overflow: 'hidden' }}>{p.planet}</span>}
            </div>
          );
        })}
        {nowPct > 0 && nowPct < 100 && <div style={{ position: 'absolute', left: `${nowPct}%`, top: -4, bottom: -4, width: 2, background: 'var(--gold)', zIndex: 5 }} />}
      </div>
      <div style={{ position: 'relative', height: 18 }}>
        {ticks.map((t) => <span key={t.year} style={{ position: 'absolute', left: `${t.pct}%`, transform: 'translateX(-50%)', fontSize: 9, color: 'var(--text-faint)' }}>{t.year}</span>)}
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 12 }}>
        {visible.map((p, i) => (
          <div key={`l-${i}`} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <div style={{ width: 10, height: 10, borderRadius: 3, background: pColor(p.planet), opacity: p.planet === currentPlanet ? 1 : 0.6 }} />
            <span style={{ fontSize: 11, color: p.planet === currentPlanet ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: p.planet === currentPlanet ? 600 : 400 }}>
              {p.planet} ({Math.round(p.duration_years)}y)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- Current Period Card ---------- */

export function CurrentPeriodCard({ current, birthNakshatra }: { current: CurrentDasha; birthNakshatra?: string }) {
  const maha = current.mahadasha;
  return (
    <div style={CARD}>
      <h3 style={{ ...HEADING, marginBottom: 4 }}>Current Period</h3>
      {birthNakshatra && <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 16 }}>Birth Nakshatra: {birthNakshatra}</p>}
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginBottom: 20 }}>
        {maha && <PeriodBlock label="Mahadasha" period={maha} />}
        {current.antardasha && <PeriodBlock label="Antardasha" period={current.antardasha} />}
      </div>
      {maha?.progress_percentage != null && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-faint)', marginBottom: 4 }}>
            <span>Mahadasha Progress</span><span>{Math.round(maha.progress_percentage)}%</span>
          </div>
          <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${Math.min(100, maha.progress_percentage)}%`, background: pColor(maha.planet), borderRadius: 3, transition: 'width 0.5s ease-out' }} />
          </div>
        </div>
      )}
      {current.description && <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 16, lineHeight: 1.6, fontStyle: 'italic' }}>{current.description}</p>}
    </div>
  );
}

/* ---------- Antardasha Timeline ---------- */

export function AntardashaTimeline({ periods, currentAntar, onPlanetClick }: { periods: DashaPeriod[]; currentAntar?: string; onPlanetClick?: (period: DashaPeriod) => void }) {
  if (!periods.length) return null;
  const fStart = parseDate(periods[0].start_date);
  const fEnd = parseDate(periods[periods.length - 1].end_date);
  if (!fStart || !fEnd) return null;
  const totalMs = fEnd.getTime() - fStart.getTime();
  if (totalMs <= 0) return null;

  return (
    <div style={CARD}>
      <h3 style={HEADING}>Antardasha Sub-periods</h3>
      <div style={{ position: 'relative', height: 32, borderRadius: 6, overflow: 'hidden', background: 'var(--background)', marginBottom: 12 }}>
        {periods.map((p, i) => {
          const s = parseDate(p.start_date)!.getTime();
          const e = parseDate(p.end_date)!.getTime();
          const left = ((s - fStart.getTime()) / totalMs) * 100;
          const w = ((e - s) / totalMs) * 100;
          const cur = p.planet === currentAntar;
          return (
            <div key={`ad-${i}`} title={`${p.planet}: ${fmtDate(p.start_date)} \u2013 ${fmtDate(p.end_date)}`} style={{
              position: 'absolute', left: `${left}%`, width: `${w}%`, top: 0, bottom: 0,
              background: pColor(p.planet), opacity: cur ? 1 : 0.5,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderLeft: i > 0 ? '1px solid var(--background)' : 'none',
              ...(cur ? { outline: '2px solid var(--gold)', outlineOffset: -2, zIndex: 2 } : {}),
            }}>
              {w > 7 && <span style={{ fontSize: 10, color: '#fff', fontWeight: 600, textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}>{p.planet}</span>}
            </div>
          );
        })}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
        {periods.map((p, i) => {
          const cur = p.planet === currentAntar;
          return (
            <div key={`al-${i}`}
              onClick={() => onPlanetClick?.(p)}
              style={{ padding: '10px 12px', borderRadius: 8, border: cur ? '1px solid var(--gold)' : '1px solid var(--border)', background: cur ? 'var(--gold-bg)' : 'transparent', cursor: 'pointer', transition: 'border-color 0.15s ease' }}
              onMouseEnter={(e) => { if (!cur) e.currentTarget.style.borderColor = pColor(p.planet); }}
              onMouseLeave={(e) => { if (!cur) e.currentTarget.style.borderColor = 'var(--border)'; }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                <div style={{ width: 8, height: 8, borderRadius: 2, background: pColor(p.planet) }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: cur ? 'var(--text-primary)' : 'var(--text-secondary)' }}>{p.planet}</span>
                {cur && <span style={{ fontSize: 9, color: 'var(--gold)', fontWeight: 700 }}>CURRENT</span>}
              </div>
              <p style={{ fontSize: 10, color: 'var(--text-faint)' }}>{fmtDate(p.start_date)} \u2013 {fmtDate(p.end_date)}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ---------- Upcoming Transitions ---------- */

export function UpcomingTransitions({ changes, antardashas }: {
  changes?: { date: string; new_dasha: string }[];
  antardashas?: DashaPeriod[];
}) {
  const now = Date.now();
  const items: { date: string; planet: string; level: string }[] = [];

  if (antardashas) {
    for (const ad of antardashas) {
      const s = parseDate(ad.start_date);
      if (s && s.getTime() > now) items.push({ date: ad.start_date, planet: ad.planet, level: 'Antardasha' });
    }
  }
  if (changes) {
    for (const c of changes) items.push({ date: c.date, planet: c.new_dasha, level: 'Mahadasha' });
  }

  items.sort((a, b) => (parseDate(a.date)?.getTime() || 0) - (parseDate(b.date)?.getTime() || 0));
  const top5 = items.slice(0, 5);
  if (!top5.length) return null;

  return (
    <div style={CARD}>
      <h3 style={HEADING}>Upcoming Transitions</h3>
      {top5.map((t, i) => {
        const daysUntil = parseDate(t.date) ? Math.ceil((parseDate(t.date)!.getTime() - now) / 86400000) : 0;
        return (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: i < top5.length - 1 ? '1px solid var(--border)' : 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 10, height: 10, borderRadius: 3, background: pColor(t.planet) }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{t.planet}</span>
              <span style={{ fontSize: 10, color: t.level === 'Mahadasha' ? 'var(--gold)' : 'var(--text-muted)', fontWeight: 500 }}>{t.level}</span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{fmtDate(t.date)}</p>
              <p style={{ fontSize: 10, color: 'var(--text-faint)' }}>in {daysUntil} days</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
