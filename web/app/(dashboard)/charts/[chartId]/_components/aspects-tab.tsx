'use client';

import { Sparkles } from 'lucide-react';
import type { ChartDetail, ChartDetailAspectData } from '@/types';
import { ComingSoonCard } from './coming-soon-card';

export function AspectsTab({ chart }: { chart: ChartDetail }) {
  const aspects: ChartDetailAspectData[] = chart.aspects || (chart.chart_data as unknown as Record<string, unknown>)?.aspects as ChartDetailAspectData[] || [];

  if (aspects.length === 0) {
    return (
      <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
        <ComingSoonCard
          icon={<Sparkles style={{ width: 20, height: 20, color: 'var(--green)' }} />}
          bgColor="var(--green-bg)"
          message="No aspects data available for this chart"
        />
      </div>
    );
  }

  const headerStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.8,
    color: 'var(--text-faint)', fontWeight: 600, textAlign: 'left', borderBottom: '1px solid var(--border)',
  };
  const cellStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 13, color: 'var(--text-secondary)', borderBottom: '1px solid var(--border)',
  };

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      <div style={{ border: '1px solid var(--border)', borderRadius: 12, background: 'var(--bg-card)', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>Planet 1</th>
                <th style={headerStyle}>Aspect</th>
                <th style={headerStyle}>Planet 2</th>
                <th style={headerStyle}>Orb</th>
                <th style={{ ...headerStyle, textAlign: 'center' }}>Applying / Separating</th>
              </tr>
            </thead>
            <tbody>
              {aspects.map((a, i) => (
                <tr
                  key={`${a.planet1}-${a.planet2}-${a.aspect}-${i}`}
                  style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{a.planet1}</td>
                  <td style={cellStyle}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                      <span>{a.aspect}</span>
                      {a.angle != null && (
                        <span style={{ fontSize: 10, color: 'var(--text-faint)', fontFamily: 'monospace' }}>
                          {a.angle}&deg;
                        </span>
                      )}
                    </span>
                  </td>
                  <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{a.planet2}</td>
                  <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>
                    {a.orb != null ? `${a.orb.toFixed(2)}\u00B0` : '\u2014'}
                  </td>
                  <td style={{ ...cellStyle, textAlign: 'center' }}>
                    {a.applying != null ? (
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 500,
                          color: a.applying ? 'var(--green)' : 'var(--text-faint)',
                        }}
                      >
                        {a.applying ? 'Applying' : 'Separating'}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)' }}>{'\u2014'}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
