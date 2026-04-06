'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import type { GunaResult } from './compatibility-types';
import { GUNA_INFO } from './compatibility-types';

export function GunaCard({ gunaKey, guna, person1Name, person2Name }: {
  gunaKey: string;
  guna: GunaResult;
  person1Name: string;
  person2Name: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const info = GUNA_INFO[gunaKey];
  if (!info) return null;
  const pct = guna.max_points > 0 ? (guna.points / guna.max_points) * 100 : 0;
  const barColor = pct >= 75 ? 'var(--green)' : pct >= 50 ? 'var(--gold)' : 'var(--red)';
  const isHigh = pct >= 50;

  return (
    <div
      style={{
        border: `1px solid ${expanded ? barColor : 'var(--border)'}`,
        borderRadius: 12,
        background: 'var(--card)',
        padding: 16,
        cursor: 'pointer',
        transition: 'border-color 0.2s, box-shadow 0.2s',
        boxShadow: expanded ? `0 0 0 1px ${barColor}20` : 'none',
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
          {info.label}
        </h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: barColor, fontFamily: 'monospace' }}>
            {guna.points}/{guna.max_points}
          </span>
          <ChevronDown
            style={{
              width: 14, height: 14, color: 'var(--text-faint)',
              transition: 'transform 0.2s',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            }}
          />
        </div>
      </div>
      <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden', marginBottom: 8 }}>
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            background: barColor,
            borderRadius: 3,
            transition: 'width 0.5s ease-out',
          }}
        />
      </div>
      <p style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>
        {info.description}
      </p>

      {/* Expanded detail */}
      {expanded && (
        <div
          style={{
            marginTop: 14,
            paddingTop: 14,
            borderTop: '1px solid var(--border)',
            animation: 'fadeIn 0.2s ease-out',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div style={{ marginBottom: 12 }}>
            <p style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-faint)', marginBottom: 4 }}>
              What this measures
            </p>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              {info.measures}
            </p>
          </div>

          <div style={{ marginBottom: 12 }}>
            <p style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-faint)', marginBottom: 4 }}>
              {person1Name} & {person2Name}
            </p>
            <div
              style={{
                padding: 10,
                borderRadius: 8,
                background: isHigh ? 'var(--green-bg)' : 'var(--red-bg)',
                fontSize: 12,
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
              }}
            >
              {guna.description || (isHigh
                ? `${person1Name} and ${person2Name} show strong ${info.label.toLowerCase()} compatibility, scoring ${guna.points} out of ${guna.max_points} points.`
                : `${person1Name} and ${person2Name} have lower ${info.label.toLowerCase()} compatibility at ${guna.points} out of ${guna.max_points} points. Consider the remedial suggestions below.`
              )}
            </div>
          </div>

          <div>
            <p style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-faint)', marginBottom: 4 }}>
              {isHigh ? 'High score means' : 'Low score means'}
            </p>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              {isHigh ? info.highScore : info.lowScore}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
