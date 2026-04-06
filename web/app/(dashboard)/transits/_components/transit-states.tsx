'use client';

import { Globe, Star } from 'lucide-react';

export function LoadingSkeleton() {
  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      {/* Summary skeleton */}
      <div
        style={{
          height: 120, borderRadius: 12,
          background: 'var(--border)', opacity: 0.3,
          marginBottom: 24, animation: 'pulse 2s infinite',
        }}
      />
      {/* Table skeleton */}
      <div
        style={{
          height: 320, borderRadius: 12,
          background: 'var(--border)', opacity: 0.25,
          marginBottom: 28, animation: 'pulse 2s infinite',
          animationDelay: '0.2s',
        }}
      />
      {/* Aspects skeleton */}
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            height: 72, borderRadius: 12,
            background: 'var(--border)', opacity: 0.2,
            marginBottom: 10, animation: 'pulse 2s infinite',
            animationDelay: `${0.3 + i * 0.1}s`,
          }}
        />
      ))}
    </div>
  );
}

export function EmptyState() {
  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        padding: 48,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 48, height: 48, borderRadius: '50%', margin: '0 auto 14px',
          background: 'var(--gold-bg)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <Globe style={{ width: 22, height: 22, color: 'var(--gold)' }} />
      </div>
      <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 4 }}>
        Select a profile to get started
      </p>
      <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
        See how current planetary positions affect your natal chart
      </p>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div
      style={{
        border: '1px solid var(--red)',
        borderRadius: 12,
        background: 'var(--red-bg)',
        padding: 16,
        marginBottom: 24,
        display: 'flex', alignItems: 'center', gap: 10,
      }}
    >
      <Star style={{ width: 16, height: 16, color: 'var(--red)', flexShrink: 0 }} />
      <p style={{ fontSize: 13, color: 'var(--red)' }}>
        {message || 'Failed to load transit data'}
      </p>
    </div>
  );
}
