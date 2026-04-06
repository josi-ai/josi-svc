'use client';

import type { PanchangData } from './panchang-types';
import { overallDayQuality } from './panchang-helpers';

export function QualitySummaryCard({ data }: { data: PanchangData }) {
  const quality = overallDayQuality(data.tithi, data.nakshatra, data.yoga);

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 14,
        background: 'var(--bg-card)',
        padding: 20,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: '50%',
          margin: '0 auto 12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: quality.color + '18',
        }}
      >
        <div style={{ width: 20, height: 20, borderRadius: '50%', background: quality.color }} />
      </div>
      <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 18, color: quality.color, marginBottom: 8 }}>
        {quality.label}
      </h3>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: 300, margin: '0 auto' }}>
        Based on {data.tithi?.name || 'Tithi'} ({data.tithi?.paksha || ''}), {data.nakshatra?.name || 'Nakshatra'}, and {data.yoga?.name || 'Yoga'} ({data.yoga?.quality || 'mixed'}).
      </p>
    </div>
  );
}
