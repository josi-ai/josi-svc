'use client';

import React from 'react';

export function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h4
      style={{
        fontSize: 10,
        textTransform: 'uppercase',
        letterSpacing: 1.2,
        color: 'var(--text-faint)',
        marginBottom: 10,
        paddingLeft: 2,
        fontWeight: 600,
      }}
    >
      {children}
    </h4>
  );
}

export function SkeletonGauge() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
      <div
        style={{
          width: 180, height: 180, borderRadius: '50%',
          background: 'var(--border)', opacity: 0.4,
          animation: 'pulse 2s infinite',
        }}
      />
      <div style={{ width: 120, height: 16, borderRadius: 8, background: 'var(--border)', opacity: 0.4 }} />
    </div>
  );
}

export function SkeletonCards() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          style={{
            height: 100, borderRadius: 12,
            background: 'var(--border)', opacity: 0.3,
            animation: 'pulse 2s infinite',
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
    </div>
  );
}
