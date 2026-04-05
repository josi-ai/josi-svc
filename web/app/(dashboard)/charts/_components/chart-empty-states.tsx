'use client';

import Link from 'next/link';
import { Plus, Star } from 'lucide-react';

/* ---------- Loading Skeletons ---------- */

export function LoadingGrid() {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
        gap: 16,
      }}
    >
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          style={{
            background: 'var(--card)',
            border: '1px solid var(--border)',
            borderRadius: 14,
            padding: 20,
          }}
        >
          <div style={{ display: 'flex', gap: 16 }}>
            {/* Mini chart skeleton */}
            <div
              style={{
                width: 120,
                height: 120,
                borderRadius: 4,
                background: 'var(--border)',
                opacity: 0.4,
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div
                style={{
                  height: 12,
                  width: 60,
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.4,
                }}
              />
              <div
                style={{
                  height: 16,
                  width: '80%',
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.4,
                }}
              />
              <div
                style={{
                  height: 10,
                  width: '50%',
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.3,
                }}
              />
              <div style={{ flex: 1 }} />
              <div
                style={{
                  height: 10,
                  width: '40%',
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.25,
                }}
              />
            </div>
          </div>
        </div>
      ))}
      <style>{`@keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.2; } }`}</style>
    </div>
  );
}

export function LoadingList() {
  return (
    <div
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 14,
        overflow: 'hidden',
      }}
    >
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          style={{
            padding: '14px 20px',
            borderBottom: i < 5 ? '1px solid var(--border)' : 'none',
            display: 'flex',
            gap: 16,
            alignItems: 'center',
          }}
        >
          <div
            style={{
              height: 12,
              width: 120,
              borderRadius: 6,
              background: 'var(--border)',
              opacity: 0.4,
            }}
          />
          <div
            style={{
              height: 12,
              width: 100,
              borderRadius: 6,
              background: 'var(--border)',
              opacity: 0.3,
            }}
          />
          <div style={{ flex: 1 }} />
          <div
            style={{
              height: 12,
              width: 80,
              borderRadius: 6,
              background: 'var(--border)',
              opacity: 0.25,
            }}
          />
        </div>
      ))}
    </div>
  );
}

/* ---------- Empty / No Results ---------- */

export function EmptyState() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 14,
        border: '1px solid var(--border)',
        background: 'var(--card)',
        padding: '64px 24px',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 20,
          background: 'var(--gold-bg)',
        }}
      >
        <Star style={{ width: 24, height: 24, color: 'var(--gold)' }} />
      </div>
      <p
        className="font-display"
        style={{
          fontSize: 18,
          color: 'var(--text-primary)',
          marginBottom: 8,
        }}
      >
        No charts yet
      </p>
      <p
        style={{
          fontSize: 13,
          color: 'var(--text-muted)',
          marginBottom: 24,
          maxWidth: 300,
          lineHeight: 1.5,
        }}
      >
        Create your first birth chart to explore planetary positions across six astrological traditions.
      </p>
      <Link href="/charts/new">
        <button
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '10px 20px',
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 600,
            background: 'var(--gold)',
            color: 'var(--btn-add-text)',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          <Plus style={{ width: 16, height: 16 }} />
          Calculate Your First Chart
        </button>
      </Link>
    </div>
  );
}

export function NoFilterResults({ filter }: { filter: string }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 14,
        border: '1px solid var(--border)',
        background: 'var(--card)',
        padding: '64px 24px',
        textAlign: 'center',
      }}
    >
      <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
        No {filter.toLowerCase()} charts found. Try a different tradition.
      </p>
    </div>
  );
}
