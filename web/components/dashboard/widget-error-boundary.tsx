'use client';

import React from 'react';
import { AlertTriangle } from 'lucide-react';

/* Error boundary so one broken widget can't crash the entire dashboard */
export class WidgetErrorBoundary extends React.Component<
  { children: React.ReactNode; onRemove: () => void },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; onRemove: () => void }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          height: '100%', display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', gap: 8,
          background: 'var(--card)', borderRadius: 16,
          border: '1px solid var(--border)', padding: 16,
        }}>
          <AlertTriangle style={{ width: 20, height: 20, color: 'var(--text-faint)' }} />
          <span style={{ fontSize: 11, color: 'var(--text-faint)' }}>Widget failed to load</span>
          <button
            onClick={this.props.onRemove}
            style={{
              fontSize: 10, color: 'var(--gold)', background: 'none',
              border: 'none', cursor: 'pointer', textDecoration: 'underline',
            }}
          >
            Remove
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export function WidgetSkeleton() {
  return (
    <div style={{ height: '100%', background: 'var(--card)', borderRadius: 16, border: '1px solid var(--border)', padding: 20 }}>
      <div className="animate-pulse space-y-3">
        <div className="h-3 w-24 rounded" style={{ background: 'var(--border)' }} />
        <div className="h-4 w-40 rounded" style={{ background: 'var(--border-subtle)' }} />
        <div className="h-3 w-full rounded" style={{ background: 'var(--border-subtle)' }} />
      </div>
    </div>
  );
}
