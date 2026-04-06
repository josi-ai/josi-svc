'use client';

import { RotateCcw } from 'lucide-react';
import type { PlanetPosition } from './transit-types';
import { PLANET_ORDER, formatDegree } from './transit-helpers';

export function PlanetaryPositionsTable({ positions }: { positions: Record<string, PlanetPosition> }) {
  const ordered = PLANET_ORDER.filter((p) => positions[p]);
  const extra = Object.keys(positions).filter((p) => !PLANET_ORDER.includes(p));
  const allPlanets = [...ordered, ...extra];

  const headerStyle: React.CSSProperties = {
    padding: '10px 16px',
    fontSize: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    color: 'var(--text-faint)',
    fontWeight: 600,
    textAlign: 'left',
    borderBottom: '1px solid var(--border)',
  };

  const cellStyle: React.CSSProperties = {
    padding: '10px 16px',
    fontSize: 13,
    color: 'var(--text-secondary)',
    borderBottom: '1px solid var(--border)',
  };

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
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={headerStyle}>Planet</th>
              <th style={headerStyle}>Sign</th>
              <th style={headerStyle}>Degree</th>
              <th style={{ ...headerStyle, textAlign: 'center' }}>Retrograde</th>
            </tr>
          </thead>
          <tbody>
            {allPlanets.map((name) => {
              const p = positions[name];
              if (!p) return null;
              const isRetro = p.retrograde;
              return (
                <tr
                  key={name}
                  style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td
                    style={{
                      ...cellStyle,
                      fontWeight: 600,
                      color: isRetro ? 'var(--red)' : 'var(--text-primary)',
                    }}
                  >
                    {name}
                  </td>
                  <td style={cellStyle}>{p.sign || '\u2014'}</td>
                  <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>
                    {formatDegree(p.degree)}
                  </td>
                  <td style={{ ...cellStyle, textAlign: 'center' }}>
                    {isRetro ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, color: 'var(--red)', fontWeight: 600, fontSize: 11 }}>
                        <RotateCcw style={{ width: 11, height: 11 }} /> Yes
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)' }}>{'\u2014'}</span>
                    )}
                  </td>
                </tr>
              );
            })}
            {allPlanets.length === 0 && (
              <tr>
                <td colSpan={4} style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                  No planetary position data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
