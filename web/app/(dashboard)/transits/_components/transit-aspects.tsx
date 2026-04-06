'use client';

import { ArrowRight, Globe } from 'lucide-react';
import type { MajorTransit } from './transit-types';
import { ASPECT_COLORS, ASPECT_NATURE, formatDegree, intensityColor, intensityLabel } from './transit-helpers';

export function TransitAspectsSection({ transits }: { transits: MajorTransit[] }) {
  if (transits.length === 0) {
    return (
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--card)',
          padding: 32,
          textAlign: 'center',
          marginBottom: 28,
        }}
      >
        <Globe style={{ width: 24, height: 24, color: 'var(--text-faint)', margin: '0 auto 8px' }} />
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          No major transit aspects within orb right now
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        overflow: 'hidden',
        marginBottom: 28,
      }}
    >
      {transits.map((t, i) => {
        const aspectColor = ASPECT_COLORS[t.aspect] || 'var(--text-muted)';
        const nature = ASPECT_NATURE[t.aspect] || 'Neutral';
        const orbIntensity = intensityLabel(t.orb);

        return (
          <div
            key={i}
            style={{
              padding: '14px 18px',
              borderBottom: i < transits.length - 1 ? '1px solid var(--border)' : 'none',
              transition: 'background 0.15s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
          >
            {/* Aspect row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
                {t.planet}
              </span>
              <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>
                {t.current_sign} {formatDegree(t.current_degree)}
              </span>
              <ArrowRight style={{ width: 12, height: 12, color: aspectColor }} />
              <span
                style={{
                  fontSize: 11, fontWeight: 600,
                  color: aspectColor,
                  padding: '2px 8px',
                  borderRadius: 4,
                  background: nature === 'Harmonious' ? 'var(--green-bg)' : nature === 'Challenging' ? 'var(--red-bg)' : 'var(--gold-bg)',
                }}
              >
                {t.aspect}
              </span>
              <ArrowRight style={{ width: 12, height: 12, color: aspectColor }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
                Natal {t.planet}
              </span>
              <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>
                {t.natal_sign} {formatDegree(t.natal_degree)}
              </span>
            </div>

            {/* Details row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Orb: <span style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{t.orb.toFixed(2)}{'\u00B0'}</span>
              </span>
              <span
                style={{
                  fontSize: 10, fontWeight: 600,
                  color: intensityColor(orbIntensity),
                  padding: '1px 6px',
                  borderRadius: 4,
                  border: `1px solid ${orbIntensity === 'Strong' ? 'var(--gold)' : 'var(--border)'}`,
                }}
              >
                {orbIntensity}
              </span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', flex: 1 }}>
                {t.effects}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
