'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';

export function PeriodNavigator({
  label,
  onPrev,
  onNext,
}: {
  label: string;
  onPrev: () => void;
  onNext: () => void;
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'center' }}>
      <button
        onClick={onPrev}
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '6px 10px',
          cursor: 'pointer',
          color: 'var(--text-primary)',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <ChevronLeft size={16} />
      </button>
      <span
        style={{
          fontSize: 14,
          fontWeight: 600,
          color: 'var(--text-primary)',
          minWidth: 140,
          textAlign: 'center',
        }}
      >
        {label}
      </span>
      <button
        onClick={onNext}
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '6px 10px',
          cursor: 'pointer',
          color: 'var(--text-primary)',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <ChevronRight size={16} />
      </button>
    </div>
  );
}
