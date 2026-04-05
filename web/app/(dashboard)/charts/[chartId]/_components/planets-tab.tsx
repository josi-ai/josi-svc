'use client';

import { RotateCcw } from 'lucide-react';
import type { ChartDetail } from '@/types';
import { PLANET_ORDER, formatDegree, dignityStyle, dignityLabel, getPlanets } from './chart-detail-helpers';

export function PlanetsTab({ chart }: { chart: ChartDetail }) {
  const planets = getPlanets(chart);
  const isVedic = chart.chart_type === 'vedic';

  const orderedPlanets = PLANET_ORDER.filter((p) => planets[p]);
  const extraPlanets = Object.keys(planets).filter((p) => !PLANET_ORDER.includes(p));
  const allPlanets = [...orderedPlanets, ...extraPlanets];

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
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--bg-card)',
          overflow: 'hidden',
        }}
      >
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>Planet</th>
                <th style={headerStyle}>Sign</th>
                <th style={headerStyle}>Degree</th>
                <th style={headerStyle}>House</th>
                {isVedic && <th style={headerStyle}>Nakshatra</th>}
                {isVedic && <th style={headerStyle}>Pada</th>}
                <th style={headerStyle}>Dignity</th>
                <th style={{ ...headerStyle, textAlign: 'center' }}>Retro</th>
              </tr>
            </thead>
            <tbody>
              {allPlanets.map((name) => {
                const p = planets[name];
                if (!p) return null;
                const isRetro = p.is_retrograde || (p.speed != null && p.speed < 0);
                const dStyle = dignityStyle(p.dignity);
                return (
                  <tr
                    key={name}
                    style={{ transition: 'background 0.15s' }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{name}</td>
                    <td style={cellStyle}>{p.sign || '\u2014'}</td>
                    <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>{formatDegree(p.sign_degree)}</td>
                    <td style={cellStyle}>{p.house || '\u2014'}</td>
                    {isVedic && <td style={cellStyle}>{p.nakshatra || '\u2014'}</td>}
                    {isVedic && <td style={cellStyle}>{p.nakshatra_pada || p.pada || '\u2014'}</td>}
                    <td style={{ ...cellStyle, ...dStyle }}>{dignityLabel(p.dignity)}</td>
                    <td style={{ ...cellStyle, textAlign: 'center' }}>
                      {isRetro ? (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, color: 'var(--red)', fontWeight: 600, fontSize: 11 }}>
                          <RotateCcw style={{ width: 11, height: 11 }} /> &#x211E;
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
                  <td colSpan={isVedic ? 8 : 6} style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                    No planet data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
