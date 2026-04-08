'use client';

import React from 'react';
import {
  type ChartProps,
  SIGN_ABBREV,
  SI_CELL_POSITIONS,
  getPlanetsBySign,
} from './chart-constants';

/* ================================================================
   South Indian Chart

   A 4x4 CSS grid with signs in fixed positions. Center 2x2 shows "Rasi".
   Each cell shows the sign abbreviation and any planets in that sign.

   Cell layout:
     Row 0: Pisces   Aries    Taurus   Gemini
     Row 1: Aquarius [center] [center] Cancer
     Row 2: Capricorn[center] [center] Leo
     Row 3: Sagitt.  Scorpio  Libra    Virgo
   ================================================================ */

export function SouthIndianChart({ planets, ascSign, centerLabel = 'Rasi' }: ChartProps) {
  const planetsBySign = getPlanetsBySign(planets);

  const cells: React.ReactNode[] = [];

  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 4; col++) {
      // Skip center 2x2
      if ((row === 1 || row === 2) && (col === 1 || col === 2)) continue;

      const cellInfo = SI_CELL_POSITIONS.find((c) => c.row === row && c.col === col);
      const signFull = cellInfo?.sign || '';
      const signAbbr = SIGN_ABBREV[signFull] || '';
      const cellPlanets = planetsBySign[signFull] || [];
      const isAsc = signFull === ascSign;

      cells.push(
        <div
          key={`${row}-${col}`}
          style={{
            gridRow: row + 1,
            gridColumn: col + 1,
            border: '0.5px solid var(--border)',
            padding: 4,
            fontSize: 10,
            lineHeight: '1.3',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            overflow: 'hidden',
            background: isAsc ? 'var(--gold-bg-subtle, rgba(255,215,0,0.04))' : 'transparent',
          }}
        >
          <span
            style={{
              color: isAsc ? 'var(--gold)' : 'var(--text-faint)',
              fontWeight: isAsc ? 700 : 500,
              letterSpacing: 0.3,
            }}
          >
            {signAbbr}
            {isAsc && (
              <span style={{ fontSize: 7, marginLeft: 2, opacity: 0.7 }}>Asc</span>
            )}
          </span>
          {cellPlanets.length > 0 && (
            <span style={{ color: 'var(--gold)', fontWeight: 600, fontSize: 9, wordBreak: 'break-word' }}>
              {cellPlanets.join(' ')}
            </span>
          )}
        </div>,
      );
    }
  }

  // Center label cell
  cells.push(
    <div
      key="center"
      style={{
        gridColumn: '2 / 4',
        gridRow: '2 / 4',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid var(--border-strong)',
        fontFamily: "'DM Serif Display', serif",
        fontSize: 16,
        color: 'var(--text-muted)',
        letterSpacing: 1,
      }}
    >
      {centerLabel}
    </div>,
  );

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gridTemplateRows: 'repeat(4, 1fr)',
        width: 350,
        height: 350,
        border: '1.5px solid var(--border-strong)',
        borderRadius: 4,
        overflow: 'hidden',
        flexShrink: 0,
      }}
    >
      {cells}
    </div>
  );
}
