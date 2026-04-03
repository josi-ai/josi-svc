'use client';

import React from 'react';

/* ================================================================
   Types
   ================================================================ */

interface PlanetData {
  longitude: number;
  sign: string;
  sign_degree: number;
  house: number;
  nakshatra?: string;
  nakshatra_pada?: number;
  pada?: number;
  is_retrograde: boolean;
  speed?: number;
  dignity?: string;
}

interface ChartProps {
  planets: Record<string, PlanetData>;
  ascSign?: string; // Ascendant sign name (e.g., "Aries")
}

/* ================================================================
   Constants
   ================================================================ */

const PLANET_ABBREV: Record<string, string> = {
  Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me',
  Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke',
};

const SIGN_ABBREV: Record<string, string> = {
  Aries: 'Ar', Taurus: 'Ta', Gemini: 'Ge', Cancer: 'Ca',
  Leo: 'Le', Virgo: 'Vi', Libra: 'Li', Scorpio: 'Sc',
  Sagittarius: 'Sg', Capricorn: 'Cp', Aquarius: 'Aq', Pisces: 'Pi',
};

const SIGNS_ORDERED = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
];

/* South Indian chart: signs in fixed cell positions (row, col) */
const SI_CELL_POSITIONS: { sign: string; row: number; col: number }[] = [
  { sign: 'Pisces', row: 0, col: 0 },
  { sign: 'Aries', row: 0, col: 1 },
  { sign: 'Taurus', row: 0, col: 2 },
  { sign: 'Gemini', row: 0, col: 3 },
  { sign: 'Cancer', row: 1, col: 3 },
  { sign: 'Leo', row: 2, col: 3 },
  { sign: 'Virgo', row: 3, col: 3 },
  { sign: 'Libra', row: 3, col: 2 },
  { sign: 'Scorpio', row: 3, col: 1 },
  { sign: 'Sagittarius', row: 3, col: 0 },
  { sign: 'Capricorn', row: 2, col: 0 },
  { sign: 'Aquarius', row: 1, col: 0 },
];

/* Sign Unicode glyphs for Western wheel */
const SIGN_GLYPHS: Record<string, string> = {
  Aries: '\u2648', Taurus: '\u2649', Gemini: '\u264A', Cancer: '\u264B',
  Leo: '\u264C', Virgo: '\u264D', Libra: '\u264E', Scorpio: '\u264F',
  Sagittarius: '\u2650', Capricorn: '\u2651', Aquarius: '\u2652', Pisces: '\u2653',
};

/* Planet Unicode glyphs for Western wheel */
const PLANET_GLYPHS: Record<string, string> = {
  Sun: '\u2609', Moon: '\u263D', Mars: '\u2642', Mercury: '\u263F',
  Jupiter: '\u2643', Venus: '\u2640', Saturn: '\u2644', Rahu: '\u260A', Ketu: '\u260B',
};

/* Element colors for Western wheel sign segments */
const SIGN_ELEMENT_COLORS: Record<string, string> = {
  Aries: '#E5484D', Taurus: '#46A758', Gemini: '#F5A623', Cancer: '#6E7BD0',
  Leo: '#E5484D', Virgo: '#46A758', Libra: '#F5A623', Scorpio: '#6E7BD0',
  Sagittarius: '#E5484D', Capricorn: '#46A758', Aquarius: '#F5A623', Pisces: '#6E7BD0',
};

/* ================================================================
   Shared Helper
   ================================================================ */

function getPlanetsBySign(planets: Record<string, PlanetData>): Record<string, string[]> {
  const map: Record<string, string[]> = {};
  for (const [name, data] of Object.entries(planets)) {
    const sign = data.sign;
    if (!sign) continue;
    if (!map[sign]) map[sign] = [];
    map[sign].push(PLANET_ABBREV[name] || name.substring(0, 2));
  }
  return map;
}

/* ================================================================
   1. South Indian Chart
   ================================================================

   A 4x4 CSS grid with signs in fixed positions. Center 2x2 shows "Rasi".
   Each cell shows the sign abbreviation and any planets in that sign.

   Cell layout:
     Row 0: Pisces   Aries    Taurus   Gemini
     Row 1: Aquarius [center] [center] Cancer
     Row 2: Capricorn[center] [center] Leo
     Row 3: Sagitt.  Scorpio  Libra    Virgo
*/

export function SouthIndianChart({ planets, ascSign }: ChartProps) {
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
      Rasi
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

/* ================================================================
   2. North Indian Chart (SVG)
   ================================================================

   Standard North Indian diamond chart. The geometry consists of:
   - An outer square
   - An inner diamond whose vertices touch the midpoints of the outer square sides
   - Lines from each outer corner to the center of the square

   This creates exactly 12 triangular regions:
   - 8 outer triangles (between diamond edges and outer square edges, split by
     the corner-to-center diagonals)
   - 4 inner diamond quadrants (the diamond interior, split by the diagonals
     which pass through the center)

   Key points (S=350, M=175):
     Outer corners: TL(0,0) TR(S,0) BR(S,S) BL(0,S)
     Diamond vertices (midpoints): TC(M,0) RC(S,M) BC(M,S) LC(0,M)
     Center: CC(M,M)

   House layout (clockwise from top):
     H1:  TC, TR, CC  (outer top-right)       -- Ascendant
     H2:  TR, RC, CC  (outer right-top)
     H3:  RC, BR, CC  (outer right-bottom)
     H4:  BR, BC, CC  (outer bottom-right)
     H5:  BC, BL, CC  (outer bottom-left)
     H6:  BL, LC, CC  (outer left-bottom)
     H7:  LC, TL, CC  (outer left-top)
     H8:  TL, TC, CC  (outer top-left)
     H9:  TC, RC, CC  (inner top-right diamond quadrant)
     H10: RC, BC, CC  (inner bottom-right diamond quadrant)
     H11: BC, LC, CC  (inner bottom-left diamond quadrant)
     H12: LC, TC, CC  (inner top-left diamond quadrant)

   The inner quadrants (H9-H12) occupy the same triangle vertex sets as certain
   outer triangles, but they are distinct regions separated by diamond edges.
   For example, H1 (TC,TR,CC) is bounded by the outer top edge and the diagonal
   TR->CC, and lies OUTSIDE the diamond. H9 (TC,RC,CC) is bounded by the diamond
   edge TC->RC and lies INSIDE the diamond.

   Sign mapping: H1 gets the ascendant sign, H2 the next sign, etc.
*/

export function NorthIndianChart({ planets, ascSign }: ChartProps) {
  const planetsBySign = getPlanetsBySign(planets);
  const ascIdx = SIGNS_ORDERED.indexOf(ascSign || 'Aries');
  const houseSign = (h: number) => SIGNS_ORDERED[(ascIdx + h) % 12];

  const S = 350;
  const M = S / 2; // 175

  // Named points
  const TL = [0, 0] as const;
  const TR = [S, 0] as const;
  const BR = [S, S] as const;
  const BL = [0, S] as const;
  const TC = [M, 0] as const;
  const RC = [S, M] as const;
  const BC = [M, S] as const;
  const LC = [0, M] as const;
  const CC = [M, M] as const;

  const pt = (p: readonly [number, number] | readonly number[]) => `${p[0]},${p[1]}`;

  // 12 house regions: vertices + centroid for label placement
  // Centroids are calculated as the average of the 3 triangle vertices, then adjusted
  // inward slightly for better visual centering within the narrow triangular regions.
  const houses: { vertices: string; cx: number; cy: number }[] = [
    // Outer triangles (H1-H8, between outer square and diamond)
    /* H1  */ { vertices: `${pt(TC)} ${pt(TR)} ${pt(CC)}`, cx: (M + S + M) / 3, cy: (0 + 0 + M) / 3 },
    /* H2  */ { vertices: `${pt(TR)} ${pt(RC)} ${pt(CC)}`, cx: (S + S + M) / 3, cy: (0 + M + M) / 3 },
    /* H3  */ { vertices: `${pt(RC)} ${pt(BR)} ${pt(CC)}`, cx: (S + S + M) / 3, cy: (M + S + M) / 3 },
    /* H4  */ { vertices: `${pt(BR)} ${pt(BC)} ${pt(CC)}`, cx: (S + M + M) / 3, cy: (S + S + M) / 3 },
    /* H5  */ { vertices: `${pt(BC)} ${pt(BL)} ${pt(CC)}`, cx: (M + 0 + M) / 3, cy: (S + S + M) / 3 },
    /* H6  */ { vertices: `${pt(BL)} ${pt(LC)} ${pt(CC)}`, cx: (0 + 0 + M) / 3, cy: (S + M + M) / 3 },
    /* H7  */ { vertices: `${pt(LC)} ${pt(TL)} ${pt(CC)}`, cx: (0 + 0 + M) / 3, cy: (M + 0 + M) / 3 },
    /* H8  */ { vertices: `${pt(TL)} ${pt(TC)} ${pt(CC)}`, cx: (0 + M + M) / 3, cy: (0 + 0 + M) / 3 },
    // Inner diamond quadrants (H9-H12)
    /* H9  */ { vertices: `${pt(TC)} ${pt(RC)} ${pt(CC)}`, cx: (M + S + M) / 3, cy: (0 + M + M) / 3 },
    /* H10 */ { vertices: `${pt(RC)} ${pt(BC)} ${pt(CC)}`, cx: (S + M + M) / 3, cy: (M + S + M) / 3 },
    /* H11 */ { vertices: `${pt(BC)} ${pt(LC)} ${pt(CC)}`, cx: (M + 0 + M) / 3, cy: (S + M + M) / 3 },
    /* H12 */ { vertices: `${pt(LC)} ${pt(TC)} ${pt(CC)}`, cx: (0 + M + M) / 3, cy: (M + 0 + M) / 3 },
  ];

  return (
    <svg width={S} height={S} viewBox={`0 0 ${S} ${S}`} style={{ flexShrink: 0 }}>
      {/* Outer square border */}
      <rect x="0" y="0" width={S} height={S} fill="none" stroke="var(--border-strong)" strokeWidth="1.5" />

      {/* Inner diamond */}
      <polygon
        points={`${pt(TC)} ${pt(RC)} ${pt(BC)} ${pt(LC)}`}
        fill="none"
        stroke="var(--border)"
        strokeWidth="0.5"
      />

      {/* Corner-to-center diagonals */}
      <line x1={TL[0]} y1={TL[1]} x2={CC[0]} y2={CC[1]} stroke="var(--border)" strokeWidth="0.5" />
      <line x1={TR[0]} y1={TR[1]} x2={CC[0]} y2={CC[1]} stroke="var(--border)" strokeWidth="0.5" />
      <line x1={BR[0]} y1={BR[1]} x2={CC[0]} y2={CC[1]} stroke="var(--border)" strokeWidth="0.5" />
      <line x1={BL[0]} y1={BL[1]} x2={CC[0]} y2={CC[1]} stroke="var(--border)" strokeWidth="0.5" />

      {/* House contents: sign abbreviation + planets */}
      {houses.map((h, i) => {
        const sign = houseSign(i);
        const abbr = SIGN_ABBREV[sign] || '';
        const pls = planetsBySign[sign] || [];
        const isAsc = i === 0;

        return (
          <g key={i}>
            {/* Subtle fill for Ascendant house */}
            {isAsc && (
              <polygon
                points={h.vertices}
                fill="var(--gold)"
                opacity="0.05"
              />
            )}
            {/* Sign abbreviation */}
            <text
              x={h.cx}
              y={h.cy - 6}
              textAnchor="middle"
              fontSize="9"
              fill={isAsc ? 'var(--gold)' : 'var(--text-faint)'}
              fontWeight={isAsc ? 700 : 500}
            >
              {abbr}
              {isAsc && (
                <tspan fontSize="7" dx="1" opacity="0.7">Asc</tspan>
              )}
            </text>
            {/* Planets in this house */}
            {pls.length > 0 && (
              <text
                x={h.cx}
                y={h.cy + 7}
                textAnchor="middle"
                fontSize="8.5"
                fill="var(--gold)"
                fontWeight="600"
              >
                {pls.join(' ')}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

/* ================================================================
   3. Western Wheel Chart (SVG)
   ================================================================

   A circular wheel chart with concentric rings:
   - Outer ring (sign band): shows zodiac sign glyphs with element-colored backgrounds
   - Middle ring (planet zone): planets placed at their longitude degree
   - Inner circle: center label "Natal"

   Signs start at 0 degrees at the top and progress clockwise, 30 degrees each.
   Planets are placed at their absolute longitude on the wheel.
*/

export function WesternWheelChart({ planets, ascSign }: ChartProps) {
  const S = 350;
  const cx = S / 2;
  const cy = S / 2;
  const outerR = S / 2 - 8;     // 167 — outermost circle
  const signR = outerR - 22;     // 145 — inner edge of sign band
  const houseR = signR - 4;      // 141 — outer edge of planet zone
  const innerR = houseR - 50;    // 91  — inner edge of planet zone
  const centerR = innerR - 10;   // 81  — center circle

  // Point on circle: 0 degrees at top, clockwise
  const pointOnCircle = (angleDeg: number, r: number): [number, number] => {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  };

  // Arc path for an annular sector between two radii
  const arcPath = (startDeg: number, endDeg: number, r1: number, r2: number): string => {
    const s1 = pointOnCircle(startDeg, r1);
    const e1 = pointOnCircle(endDeg, r1);
    const s2 = pointOnCircle(endDeg, r2);
    const e2 = pointOnCircle(startDeg, r2);
    const largeArc = Math.abs(endDeg - startDeg) > 180 ? 1 : 0;
    return [
      `M ${s1[0]},${s1[1]}`,
      `A ${r1},${r1} 0 ${largeArc} 1 ${e1[0]},${e1[1]}`,
      `L ${s2[0]},${s2[1]}`,
      `A ${r2},${r2} 0 ${largeArc} 0 ${e2[0]},${e2[1]}`,
      'Z',
    ].join(' ');
  };

  // Find the ascendant sign's starting degree for optional Asc marker
  const ascIdx = SIGNS_ORDERED.indexOf(ascSign || '');
  const ascDeg = ascIdx >= 0 ? ascIdx * 30 : -1;

  return (
    <svg width={S} height={S} viewBox={`0 0 ${S} ${S}`} style={{ flexShrink: 0 }}>
      {/* Ring circles */}
      <circle cx={cx} cy={cy} r={outerR} fill="none" stroke="var(--border-strong)" strokeWidth="1.5" />
      <circle cx={cx} cy={cy} r={signR} fill="none" stroke="var(--border)" strokeWidth="0.5" />
      <circle cx={cx} cy={cy} r={houseR} fill="none" stroke="var(--border)" strokeWidth="0.5" />
      <circle cx={cx} cy={cy} r={innerR} fill="none" stroke="var(--border)" strokeWidth="0.5" />

      {/* Sign segments (outer ring) */}
      {SIGNS_ORDERED.map((sign, i) => {
        const startDeg = i * 30;
        const endDeg = (i + 1) * 30;
        const midDeg = startDeg + 15;
        const labelPt = pointOnCircle(midDeg, (outerR + signR) / 2);
        const color = SIGN_ELEMENT_COLORS[sign] || 'var(--text-faint)';
        const isAscSign = sign === ascSign;

        return (
          <g key={sign}>
            {/* Sign arc background (subtle element color) */}
            <path
              d={arcPath(startDeg, endDeg, outerR, signR)}
              fill={`${color}${isAscSign ? '1A' : '10'}`}
              stroke="var(--border)"
              strokeWidth="0.3"
            />
            {/* Sign glyph */}
            <text
              x={labelPt[0]}
              y={labelPt[1] + 4}
              textAnchor="middle"
              fontSize="12"
              fill={color}
              style={{ opacity: isAscSign ? 1 : 0.7 }}
              fontWeight={isAscSign ? 700 : 400}
            >
              {SIGN_GLYPHS[sign]}
            </text>
            {/* Spoke line at segment boundary */}
            {(() => {
              const inner = pointOnCircle(startDeg, innerR);
              const outer = pointOnCircle(startDeg, outerR);
              return (
                <line
                  x1={outer[0]} y1={outer[1]}
                  x2={inner[0]} y2={inner[1]}
                  stroke="var(--border)"
                  strokeWidth="0.3"
                />
              );
            })()}
          </g>
        );
      })}

      {/* Ascendant marker (small arrow/line on the outer ring) */}
      {ascDeg >= 0 && (() => {
        const markerPt = pointOnCircle(ascDeg, outerR + 2);
        const markerInner = pointOnCircle(ascDeg, outerR - 6);
        return (
          <line
            x1={markerPt[0]} y1={markerPt[1]}
            x2={markerInner[0]} y2={markerInner[1]}
            stroke="var(--gold)"
            strokeWidth="2"
            opacity="0.8"
          />
        );
      })()}

      {/* Planet positions in the middle ring */}
      {Object.entries(planets).map(([name, data]) => {
        if (data.longitude == null) return null;
        const deg = data.longitude % 360;
        const planetPt = pointOnCircle(deg, (houseR + innerR) / 2);
        const glyph = PLANET_GLYPHS[name] || name.substring(0, 2);
        const isRetro = data.is_retrograde || (data.speed != null && data.speed < 0);

        return (
          <g key={name}>
            {/* Planet glyph */}
            <text
              x={planetPt[0]}
              y={planetPt[1] + 4}
              textAnchor="middle"
              fontSize="13"
              fill="var(--gold)"
              fontWeight="600"
            >
              {glyph}
            </text>
            {/* Retrograde indicator */}
            {isRetro && (
              <text
                x={planetPt[0] + 8}
                y={planetPt[1] - 2}
                textAnchor="middle"
                fontSize="7"
                fill="var(--red, #E5484D)"
              >
                R
              </text>
            )}
            {/* Degree tick on outer ring */}
            {(() => {
              const tick1 = pointOnCircle(deg, outerR);
              const tick2 = pointOnCircle(deg, outerR - 4);
              return (
                <line
                  x1={tick1[0]} y1={tick1[1]}
                  x2={tick2[0]} y2={tick2[1]}
                  stroke="var(--gold)"
                  strokeWidth="1"
                  opacity="0.5"
                />
              );
            })()}
          </g>
        );
      })}

      {/* Center circle with label */}
      <circle cx={cx} cy={cy} r={centerR} fill="var(--card)" stroke="var(--border)" strokeWidth="0.5" />
      <text
        x={cx}
        y={cy + 4}
        textAnchor="middle"
        fontSize="11"
        fill="var(--text-muted)"
        fontFamily="'DM Serif Display', serif"
      >
        Natal
      </text>
    </svg>
  );
}
