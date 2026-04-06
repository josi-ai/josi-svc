'use client';

import type { PanchangData } from './panchang-types';

export function SunMoonCard({ data }: { data: PanchangData }) {
  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 20 }}>
      <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, color: 'var(--text-primary)', marginBottom: 16 }}>
        Sun & Moon
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div style={{ textAlign: 'center', padding: 16, borderRadius: 10, background: 'var(--background)' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>{'\u2600\uFE0F'}</div>
          <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 }}>Sunrise</p>
          <p style={{ fontSize: 18, fontWeight: 700, color: 'var(--gold)', fontFamily: 'monospace' }}>{data.sunrise || '\u2014'}</p>
        </div>
        <div style={{ textAlign: 'center', padding: 16, borderRadius: 10, background: 'var(--background)' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>{'\uD83C\uDF05'}</div>
          <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 }}>Sunset</p>
          <p style={{ fontSize: 18, fontWeight: 700, color: 'var(--bar-avoid)', fontFamily: 'monospace' }}>{data.sunset || '\u2014'}</p>
        </div>
      </div>
      {data.ayanamsa != null && (
        <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 12, textAlign: 'center' }}>
          Ayanamsa (Lahiri): {data.ayanamsa.toFixed(4)}
        </p>
      )}
    </div>
  );
}
