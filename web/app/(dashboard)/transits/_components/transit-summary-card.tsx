'use client';

import { Activity, Star } from 'lucide-react';
import type { MajorTransit } from './transit-types';

export function TransitSummaryCard({ transits }: { transits: MajorTransit[] }) {
  const strongTransits = transits.filter((t) => t.orb < 2);
  const highlight = strongTransits[0] || transits[0];

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        padding: 20,
        marginBottom: 24,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div
          style={{
            width: 32, height: 32, borderRadius: 10,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'var(--gold-bg)',
          }}
        >
          <Activity style={{ width: 15, height: 15, color: 'var(--gold)' }} />
        </div>
        <div>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
            Transit Summary
          </h3>
          <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {transits.length} active aspect{transits.length !== 1 ? 's' : ''}
            {strongTransits.length > 0 && ` \u00B7 ${strongTransits.length} strong`}
          </p>
        </div>
      </div>
      {highlight && (
        <div
          style={{
            padding: 12,
            borderRadius: 8,
            background: 'var(--gold-bg)',
            display: 'flex', alignItems: 'flex-start', gap: 8,
          }}
        >
          <Star style={{ width: 14, height: 14, color: 'var(--gold)', marginTop: 1, flexShrink: 0 }} />
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
              {highlight.planet} {highlight.aspect.toLowerCase()} natal {highlight.planet}
            </p>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {highlight.effects}
            </p>
          </div>
        </div>
      )}
      {transits.length === 0 && (
        <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
          No major transit aspects are active right now. Slow-moving planets are between exact aspects.
        </p>
      )}
    </div>
  );
}
