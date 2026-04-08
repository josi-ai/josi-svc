'use client';

import { Grid3X3 } from 'lucide-react';
import type { ChartDetail } from '@/types';
import { PLANET_ORDER, getPlanets } from './chart-detail-helpers';
import { ComingSoonCard } from './coming-soon-card';

/* ================================================================
   Constants
   ================================================================ */

const VARGA_COLUMNS = [
  { key: 'D1', label: 'D1 (Rasi)' },
  { key: 'D2', label: 'D2 (Hora)' },
  { key: 'D3', label: 'D3 (Drekkana)' },
  { key: 'D4', label: 'D4' },
  { key: 'D7', label: 'D7' },
  { key: 'D9', label: 'D9 (Navamsa)' },
  { key: 'D10', label: 'D10 (Dasamsa)' },
  { key: 'D12', label: 'D12' },
  { key: 'D16', label: 'D16' },
  { key: 'D20', label: 'D20' },
  { key: 'D24', label: 'D24' },
  { key: 'D27', label: 'D27' },
  { key: 'D30', label: 'D30' },
  { key: 'D40', label: 'D40' },
  { key: 'D45', label: 'D45' },
  { key: 'D60', label: 'D60' },
] as const;

/** D1 and D9 are the most important divisions and get highlighted columns. */
const HIGHLIGHT_KEYS = new Set(['D1', 'D9']);

/* ================================================================
   Styles (match planets-tab)
   ================================================================ */

const headerStyle: React.CSSProperties = {
  padding: '10px 14px',
  fontSize: 10,
  textTransform: 'uppercase',
  letterSpacing: 0.8,
  color: 'var(--text-faint)',
  fontWeight: 600,
  textAlign: 'left',
  borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap',
};

const cellStyle: React.CSSProperties = {
  padding: '10px 14px',
  fontSize: 13,
  color: 'var(--text-secondary)',
  borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap',
};

const highlightHeaderStyle: React.CSSProperties = {
  ...headerStyle,
  color: 'var(--gold)',
  fontWeight: 700,
};

const highlightCellStyle: React.CSSProperties = {
  ...cellStyle,
  background: 'color-mix(in srgb, var(--gold) 6%, transparent)',
  fontWeight: 500,
};

/* ================================================================
   Helpers
   ================================================================ */

/**
 * Extract the sign a planet occupies in a given varga.
 *
 * The backend can return vargas in two layouts:
 *   A) { D9: { planet: { sign, degree, longitude } } }        (position-per-planet)
 *   B) { D9: { SignName: ["Planet", ...] } }                   (planets-per-sign)
 *
 * This helper normalises both to a simple sign string.
 */
function getVargaSign(
  vargas: Record<string, unknown>,
  division: string,
  planetName: string,
): string | null {
  const div = vargas[division];
  if (!div || typeof div !== 'object') return null;

  const divObj = div as Record<string, unknown>;

  // Layout A — planet key maps to an object with a `sign` field
  if (divObj[planetName] && typeof divObj[planetName] === 'object') {
    const planetEntry = divObj[planetName] as Record<string, unknown>;
    if (typeof planetEntry.sign === 'string') return planetEntry.sign;
  }

  // Layout B — sign key maps to an array of planet names
  for (const [sign, value] of Object.entries(divObj)) {
    if (Array.isArray(value) && value.includes(planetName)) return sign;
  }

  return null;
}

/* ================================================================
   Component
   ================================================================ */

export function DivisionalChartsTab({ chart }: { chart: ChartDetail }) {
  const chartData = chart.chart_data as Record<string, unknown> | undefined;
  const vargas = chartData?.vargas as Record<string, unknown> | undefined;

  if (!vargas || Object.keys(vargas).length === 0) {
    return (
      <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
        <ComingSoonCard
          icon={<Grid3X3 style={{ width: 20, height: 20, color: 'var(--blue)' }} />}
          bgColor="var(--blue-bg)"
          message="Divisional chart data not available for this chart"
        />
      </div>
    );
  }

  // Derive visible columns from what the data actually contains
  const visibleColumns = VARGA_COLUMNS.filter((c) => vargas[c.key]);

  // Build planet list in canonical order, plus any extras
  const planets = getPlanets(chart);
  const orderedPlanets = PLANET_ORDER.filter((p) => planets[p]);
  const extraPlanets = Object.keys(planets).filter((p) => !PLANET_ORDER.includes(p));
  const allPlanets = [...orderedPlanets, ...extraPlanets];

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
                {visibleColumns.map((col) => (
                  <th
                    key={col.key}
                    style={HIGHLIGHT_KEYS.has(col.key) ? highlightHeaderStyle : headerStyle}
                  >
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {allPlanets.map((name) => (
                <tr
                  key={name}
                  style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')
                  }
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>
                    {name}
                  </td>
                  {visibleColumns.map((col) => {
                    const sign = getVargaSign(vargas, col.key, name);
                    const isHighlight = HIGHLIGHT_KEYS.has(col.key);
                    return (
                      <td key={col.key} style={isHighlight ? highlightCellStyle : cellStyle}>
                        {sign || '\u2014'}
                      </td>
                    );
                  })}
                </tr>
              ))}
              {allPlanets.length === 0 && (
                <tr>
                  <td
                    colSpan={visibleColumns.length + 1}
                    style={{
                      padding: '48px 16px',
                      textAlign: 'center',
                      color: 'var(--text-muted)',
                      fontSize: 13,
                    }}
                  >
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
