'use client';

import { useState, useMemo, useCallback } from 'react';
import { useDefaultProfile } from '@/hooks/use-default-profile';
import { TimeframeSelector } from '@/components/ui/timeframe-selector';
import { fd, addD, MONTHS, cardS, NavArrow, Spinner } from './_components/muhurta-shared';
import { DailyView } from './_components/daily-view';
import { WeeklyView } from './_components/weekly-view';
import { MonthlyView } from './_components/monthly-view';
import { ActivitySearch } from './_components/activity-search';

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
