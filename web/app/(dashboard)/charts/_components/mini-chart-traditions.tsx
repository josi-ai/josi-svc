'use client';

import { Star, Globe } from 'lucide-react';
import { TRADITION_STYLES } from './chart-types';

/* ---------- Western (circle) ---------- */

export function WesternMiniChart() {
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {/* Outer ring */}
      <div
        style={{
          width: 110,
          height: 110,
          borderRadius: '50%',
          border: '2px solid var(--border-strong)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
        }}
      >
        {/* Inner ring */}
        <div
          style={{
            width: 70,
            height: 70,
            borderRadius: '50%',
            border: '1.5px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* Cross lines */}
          <div
            style={{
              width: 30,
              height: 1,
              background: 'var(--border)',
              position: 'absolute',
            }}
          />
          <div
            style={{
              width: 1,
              height: 30,
              background: 'var(--border)',
              position: 'absolute',
            }}
          />
        </div>
        {/* 12 spoke marks around the outer ring */}
        {Array.from({ length: 12 }).map((_, idx) => (
          <div
            key={idx}
            style={{
              position: 'absolute',
              width: 1,
              height: 10,
              background: 'var(--border)',
              transformOrigin: '50% 55px',
              transform: `rotate(${idx * 30}deg)`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

/* ---------- Chinese (four-pillars) ---------- */

export function ChineseMiniChart() {
  const pillars = [
    { label: 'Year', stem: '\u7532' },
    { label: 'Month', stem: '\u4E59' },
    { label: 'Day', stem: '\u4E19' },
    { label: 'Hour', stem: '\u4E01' },
  ];
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        gap: 4,
        alignItems: 'center',
        justifyContent: 'center',
        padding: '8px 6px',
      }}
    >
      {pillars.map((p) => (
        <div
          key={p.label}
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
          }}
        >
          <div
            style={{
              width: '100%',
              height: 70,
              borderRadius: 3,
              border: '1.5px solid var(--border-strong)',
              background: 'var(--card)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 2,
            }}
          >
            <span style={{ fontSize: 14, color: 'var(--text-secondary)', fontWeight: 600, lineHeight: 1 }}>
              {p.stem}
            </span>
            <span style={{ fontSize: 5.5, color: 'var(--text-faint)', fontWeight: 500 }}>
              {p.label.slice(0, 2)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ---------- Hellenistic (circle with diagonal cross) ---------- */

export function HellenisticMiniChart() {
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {/* Outer ring */}
      <div
        style={{
          width: 110,
          height: 110,
          borderRadius: '50%',
          border: '2px solid var(--border-strong)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
        }}
      >
        {/* Inner ring */}
        <div
          style={{
            width: 70,
            height: 70,
            borderRadius: '50%',
            border: '1.5px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* Diagonal cross lines */}
          <div
            style={{
              width: 30,
              height: 1,
              background: 'var(--border)',
              position: 'absolute',
              transform: 'rotate(45deg)',
            }}
          />
          <div
            style={{
              width: 30,
              height: 1,
              background: 'var(--border)',
              position: 'absolute',
              transform: 'rotate(-45deg)',
            }}
          />
        </div>
        {/* 12 spoke marks around the outer ring */}
        {Array.from({ length: 12 }).map((_, idx) => (
          <div
            key={idx}
            style={{
              position: 'absolute',
              width: 1,
              height: 10,
              background: 'var(--border)',
              transformOrigin: '50% 55px',
              transform: `rotate(${idx * 30}deg)`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

/* ---------- Generic (Mayan, Celtic, etc.) ---------- */

export function GenericMiniChart({ tradition }: { tradition: string }) {
  const tradStyle = TRADITION_STYLES[tradition.toLowerCase()];
  const color = tradStyle?.color || 'var(--text-muted)';
  const t = tradition.toLowerCase();
  const Icon = t === 'mayan' || t === 'celtic' ? Globe : Star;
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1.5px solid var(--border)',
        borderRadius: 6,
      }}
    >
      <Icon style={{ width: 28, height: 28, color, opacity: 0.5 }} />
    </div>
  );
}
