'use client';

import { useState, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { TimeframeSelector } from '@/components/ui/timeframe-selector';
import { OverallScoreCard } from '@/components/predictions/score-card';
import { CategoryCard, SkeletonCategoryCard, type Category } from '@/components/predictions/category-card';
import { PeriodNavigator } from '@/components/predictions/period-navigator';
import { Sparkles, AlertTriangle, Lightbulb } from 'lucide-react';

/* ==========================================================================
   Types
   ========================================================================== */

interface PredictionData {
  timeframe: string;
  period: { start: string; end: string };
  overall_score: number;
  overall_summary: string;
  categories: Category[];
  sign_changes?: { planet: string; from_sign: string; to_sign: string; date: string }[];
  auspicious_times?: string[];
  caution_periods?: string[];
}

/* ==========================================================================
   Constants
   ========================================================================== */

const TIMEFRAMES = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Half-yearly', 'Yearly'] as const;
type Timeframe = (typeof TIMEFRAMES)[number];

/* ==========================================================================
   Date helpers
   ========================================================================== */

function getMonday(d: Date): Date {
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const m = new Date(d);
  m.setDate(diff);
  m.setHours(0, 0, 0, 0);
  return m;
}

function fmtDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function getQuarter(d: Date): number {
  return Math.floor(d.getMonth() / 3) + 1;
}

function getHalf(d: Date): number {
  return d.getMonth() < 6 ? 1 : 2;
}

function buildEndpoint(personId: string, tf: Timeframe, offset: number): string {
  const now = new Date();
  const base = '/api/v1/predictions';
  switch (tf) {
    case 'Daily': {
      const d = new Date(now);
      d.setDate(d.getDate() + offset);
      return `${base}/daily/${personId}?date=${fmtDate(d)}`;
    }
    case 'Weekly': {
      const monday = getMonday(now);
      monday.setDate(monday.getDate() + offset * 7);
      return `${base}/weekly/${personId}?week_start=${fmtDate(monday)}`;
    }
    case 'Monthly': {
      const d = new Date(now.getFullYear(), now.getMonth() + offset, 1);
      return `${base}/monthly/${personId}?month=${d.getMonth() + 1}&year=${d.getFullYear()}`;
    }
    case 'Quarterly': {
      let q = getQuarter(now) + offset;
      let y = now.getFullYear();
      while (q < 1) { q += 4; y--; }
      while (q > 4) { q -= 4; y++; }
      return `${base}/quarterly/${personId}?quarter=${q}&year=${y}`;
    }
    case 'Half-yearly': {
      let h = getHalf(now) + offset;
      let y = now.getFullYear();
      while (h < 1) { h += 2; y--; }
      while (h > 2) { h -= 2; y++; }
      return `${base}/half-yearly/${personId}?half=${h}&year=${y}`;
    }
    case 'Yearly': {
      return `${base}/yearly/${personId}?year=${now.getFullYear() + offset}`;
    }
  }
}

function periodLabel(tf: Timeframe, offset: number): string {
  const now = new Date();
  switch (tf) {
    case 'Daily': {
      const d = new Date(now);
      d.setDate(d.getDate() + offset);
      if (offset === 0) return 'Today';
      if (offset === -1) return 'Yesterday';
      if (offset === 1) return 'Tomorrow';
      return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    }
    case 'Weekly': {
      const monday = getMonday(now);
      monday.setDate(monday.getDate() + offset * 7);
      const sunday = new Date(monday);
      sunday.setDate(sunday.getDate() + 6);
      if (offset === 0) return 'This Week';
      return `${monday.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${sunday.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
    }
    case 'Monthly': {
      const d = new Date(now.getFullYear(), now.getMonth() + offset, 1);
      if (offset === 0) return 'This Month';
      return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    }
    case 'Quarterly': {
      let q = getQuarter(now) + offset;
      let y = now.getFullYear();
      while (q < 1) { q += 4; y--; }
      while (q > 4) { q -= 4; y++; }
      return `Q${q} ${y}`;
    }
    case 'Half-yearly': {
      let h = getHalf(now) + offset;
      let y = now.getFullYear();
      while (h < 1) { h += 2; y--; }
      while (h > 2) { h -= 2; y++; }
      return `${h === 1 ? 'Jan - Jun' : 'Jul - Dec'} ${y}`;
    }
    case 'Yearly':
      return `${now.getFullYear() + offset}`;
  }
}

/* ==========================================================================
   Page
   ========================================================================== */

export default function PredictionsPage() {
  const [personId, setPersonId] = useState('');
  const [timeframe, setTimeframe] = useState<Timeframe>('Daily');
  const [offset, setOffset] = useState(0);

  const handleTimeframeChange = useCallback((tf: string) => {
    setTimeframe(tf as Timeframe);
    setOffset(0);
  }, []);

  const endpoint = personId ? buildEndpoint(personId, timeframe, offset) : null;

  const { data: predictionResponse, isLoading, isError, error } = useQuery({
    queryKey: ['predictions', personId, timeframe, offset],
    queryFn: () => apiClient.get<PredictionData>(endpoint!),
    enabled: !!endpoint,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const prediction = predictionResponse?.data ?? null;
  const navLabel = useMemo(() => periodLabel(timeframe, offset), [timeframe, offset]);

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 16px' }}>
      <style>{`@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.4 } }`}</style>

      {/* Header */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 16 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
          Predictions
        </h1>
        <div style={{ width: 220 }}>
          <ProfileSelector value={personId} onChange={setPersonId} />
        </div>
      </div>

      <TimeframeSelector value={timeframe} onChange={handleTimeframeChange} options={[...TIMEFRAMES]} style={{ marginBottom: 16 }} />

      <div style={{ marginBottom: 20 }}>
        <PeriodNavigator label={navLabel} onPrev={() => setOffset((o) => o - 1)} onNext={() => setOffset((o) => o + 1)} />
      </div>

      {/* Empty state */}
      {!personId && (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <Lightbulb size={48} style={{ color: 'var(--border)', marginBottom: 16 }} />
          <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
            Select a profile to see predictions
          </h2>
          <p style={{ fontSize: 14 }}>Choose a profile above to view personalized predictions based on their chart.</p>
        </div>
      )}

      {/* Loading */}
      {personId && isLoading && (
        <>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 16, padding: 28, display: 'flex', gap: 28, alignItems: 'center', marginBottom: 20 }}>
            <div style={{ width: 128, height: 128, borderRadius: '50%', background: 'var(--border)', animation: 'pulse 1.5s ease infinite', flexShrink: 0 }} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ width: '40%', height: 18, borderRadius: 4, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
              <div style={{ width: '80%', height: 14, borderRadius: 4, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 16 }}>
            {Array.from({ length: 10 }).map((_, i) => <SkeletonCategoryCard key={i} />)}
          </div>
        </>
      )}

      {/* Error */}
      {personId && isError && (
        <div style={{ textAlign: 'center', padding: '40px 20px', color: '#ef4444' }}>
          <AlertTriangle size={40} style={{ marginBottom: 12 }} />
          <p style={{ fontSize: 14 }}>{(error as Error)?.message || 'Failed to load predictions.'}</p>
        </div>
      )}

      {/* Results */}
      {prediction && !isLoading && (
        <>
          <div style={{ marginBottom: 20 }}>
            <OverallScoreCard score={prediction.overall_score} summary={prediction.overall_summary} />
          </div>

          {/* Auspicious times */}
          {prediction.auspicious_times && prediction.auspicious_times.length > 0 && (
            <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12, padding: '14px 18px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              <Sparkles size={16} style={{ color: 'var(--gold)' }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>Auspicious Times:</span>
              {prediction.auspicious_times.map((t, i) => (
                <span key={i} style={{ fontSize: 12, background: 'rgba(212,175,55,0.1)', color: 'var(--gold)', padding: '3px 10px', borderRadius: 20, fontWeight: 500 }}>
                  {t}
                </span>
              ))}
            </div>
          )}

          {/* Category grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 16 }}>
            {prediction.categories.map((cat) => <CategoryCard key={cat.slug} cat={cat} />)}
          </div>

          {/* Sign changes */}
          {prediction.sign_changes && prediction.sign_changes.length > 0 && (
            <div style={{ marginTop: 20, background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12, padding: 18 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 12 }}>
                Planetary Sign Changes
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {prediction.sign_changes.map((sc, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--text-secondary)' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)', minWidth: 70 }}>{sc.planet}</span>
                    <span>{sc.from_sign}</span>
                    <span style={{ color: 'var(--text-muted)' }}>&rarr;</span>
                    <span>{sc.to_sign}</span>
                    <span style={{ color: 'var(--text-muted)', marginLeft: 'auto', fontSize: 12 }}>{sc.date}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Caution periods */}
          {prediction.caution_periods && prediction.caution_periods.length > 0 && (
            <div style={{ marginTop: 16, background: 'rgba(217,119,6,0.06)', border: '1px solid rgba(217,119,6,0.2)', borderRadius: 12, padding: 18 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, color: '#d97706', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertTriangle size={16} />
                Caution Periods
              </h3>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {prediction.caution_periods.map((c, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>{c}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}
