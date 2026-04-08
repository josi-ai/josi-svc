'use client';

import React from 'react';
import {
  type ChartProps,
  SIGNS_ORDERED,
  SIGN_GLYPHS,
  PLANET_GLYPHS,
  SIGN_ELEMENT_COLORS,
} from './chart-constants';

/* ================================================================
   Western Wheel Chart (SVG)

   A circular wheel chart with concentric rings:
   - Outer ring (sign band): shows zodiac sign glyphs with element-colored backgrounds
   - Middle ring (planet zone): planets placed at their longitude degree
   - Inner circle: center label "Natal"

   Signs start at 0 degrees at the top and progress clockwise, 30 degrees each.
   Planets are placed at their absolute longitude on the wheel.
================================================================ */

export function WesternWheelChart({ planets, ascSign, centerLabel = 'Natal' }: ChartProps) {
  const S = 350;
  const cx = S / 2;
  const cy = S / 2;
  const outerR = S / 2 - 8;     // 167 -- outermost circle
  const signR = outerR - 22;     // 145 -- inner edge of sign band
  const houseR = signR - 4;      // 141 -- outer edge of planet zone
  const innerR = houseR - 50;    // 91  -- inner edge of planet zone
  const centerR = innerR - 10;   // 81  -- center circle

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
            <path
              d={arcPath(startDeg, endDeg, outerR, signR)}
              fill={`${color}${isAscSign ? '1A' : '10'}`}
              stroke="var(--border)"
              strokeWidth="0.3"
            />
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

      {/* Ascendant marker */}
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
        {centerLabel}
      </text>
    </svg>
  );
}
