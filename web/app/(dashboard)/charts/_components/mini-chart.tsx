'use client';

import type { ChartItem } from './chart-types';
import { SIGN_CELLS } from './chart-types';
import { buildSignPlanetMap } from './chart-helpers';
import {
  WesternMiniChart,
  ChineseMiniChart,
  HellenisticMiniChart,
  GenericMiniChart,
} from './mini-chart-traditions';

/* ---------- Vedic (South Indian 4x4 grid) ---------- */

function VedicMiniChart({ chart }: { chart: ChartItem }) {
  const signPlanets = buildSignPlanetMap(chart);

  return (
    <div
      style={{
        width: 120,
        height: 120,
        border: '1.5px solid var(--border-strong)',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gridTemplateRows: 'repeat(4, 1fr)',
        flexShrink: 0,
        borderRadius: 4,
        overflow: 'hidden',
        background: 'var(--bg-card, var(--card))',
      }}
    >
      {SIGN_CELLS.map((sign, i) => {
        // Center 2x2 cells (indices 5,6,9,10)
        if (i === 5) {
          return (
            <div
              key={i}
              style={{
                gridColumn: '2 / 4',
                gridRow: '2 / 4',
                border: '1px solid var(--border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 8,
                fontWeight: 600,
                color: 'var(--text-muted)',
                background: 'var(--card)',
              }}
            >
              Rasi
            </div>
          );
        }
        if (i === 6 || i === 9 || i === 10) return null;

        const planets = signPlanets[sign] || [];
        const hasAsc = planets.includes('As');
        const displayPlanets = planets.filter((p) => p !== 'As');

        return (
          <div
            key={i}
            style={{
              border: '0.5px solid var(--border)',
              padding: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <span
              style={{
                fontSize: 6,
                color: hasAsc ? 'var(--gold)' : 'var(--text-faint)',
                fontWeight: hasAsc ? 700 : 400,
                lineHeight: 1,
              }}
            >
              {sign}
            </span>
            {displayPlanets.length > 0 && (
              <span
                style={{
                  fontSize: 5.5,
                  color: 'var(--text-secondary)',
                  lineHeight: 1,
                  marginTop: 1,
                  textAlign: 'center',
                  wordBreak: 'break-all',
                }}
              >
                {displayPlanets.join(' ')}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ---------- Main MiniChart Dispatcher ---------- */

export function MiniChart({ chart }: { chart: ChartItem }) {
  const type = chart.chart_type.toLowerCase();
  if (type === 'vedic') return <VedicMiniChart chart={chart} />;
  if (type === 'western') return <WesternMiniChart />;
  if (type === 'chinese') return <ChineseMiniChart />;
  if (type === 'hellenistic') return <HellenisticMiniChart />;
  return <GenericMiniChart tradition={chart.chart_type} />;
}
