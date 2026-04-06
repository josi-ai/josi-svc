'use client';

import React from 'react';
import {
  type ChartProps,
  SIGN_ABBREV,
  SIGNS_ORDERED,
  getPlanetsBySign,
} from './chart-constants';

/* ================================================================
   North Indian Chart (SVG)

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

   Sign mapping: H1 gets the ascendant sign, H2 the next sign, etc.
================================================================ */

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
  const houses: { vertices: string; cx: number; cy: number }[] = [
    /* H1  */ { vertices: `${pt(TC)} ${pt(TR)} ${pt(CC)}`, cx: (M + S + M) / 3, cy: (0 + 0 + M) / 3 },
    /* H2  */ { vertices: `${pt(TR)} ${pt(RC)} ${pt(CC)}`, cx: (S + S + M) / 3, cy: (0 + M + M) / 3 },
    /* H3  */ { vertices: `${pt(RC)} ${pt(BR)} ${pt(CC)}`, cx: (S + S + M) / 3, cy: (M + S + M) / 3 },
    /* H4  */ { vertices: `${pt(BR)} ${pt(BC)} ${pt(CC)}`, cx: (S + M + M) / 3, cy: (S + S + M) / 3 },
    /* H5  */ { vertices: `${pt(BC)} ${pt(BL)} ${pt(CC)}`, cx: (M + 0 + M) / 3, cy: (S + S + M) / 3 },
    /* H6  */ { vertices: `${pt(BL)} ${pt(LC)} ${pt(CC)}`, cx: (0 + 0 + M) / 3, cy: (S + M + M) / 3 },
    /* H7  */ { vertices: `${pt(LC)} ${pt(TL)} ${pt(CC)}`, cx: (0 + 0 + M) / 3, cy: (M + 0 + M) / 3 },
    /* H8  */ { vertices: `${pt(TL)} ${pt(TC)} ${pt(CC)}`, cx: (0 + M + M) / 3, cy: (0 + 0 + M) / 3 },
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
            {isAsc && (
              <polygon
                points={h.vertices}
                fill="var(--gold)"
                opacity="0.05"
              />
            )}
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
