'use client';

import Link from 'next/link';
import { Plus, LayoutGrid, List, Users, X } from 'lucide-react';
import type { TraditionFilter, ViewMode } from './chart-types';
import { TRADITION_FILTERS } from './chart-types';

/* ---------- Page Header ---------- */

export function ChartsHeader() {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 24,
      }}
    >
      <div>
        <h3
          className="font-display"
          style={{
            fontSize: '1.75rem',
            color: 'var(--text-primary)',
            marginBottom: 4,
          }}
        >
          My Charts
        </h3>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          View and manage your birth charts across traditions
        </p>
      </div>
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
            transition: 'opacity 0.15s',
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLElement).style.opacity = '0.9';
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLElement).style.opacity = '1';
          }}
        >
          <Plus style={{ width: 16, height: 16 }} />
          Calculate New Chart
        </button>
      </Link>
    </div>
  );
}

/* ---------- Person Filter Banners ---------- */

export function PersonFilterBanner({
  activePersonName,
  personIdParam,
  onShowAll,
  onClearFilter,
}: {
  activePersonName: string;
  personIdParam: string | null;
  onShowAll: () => void;
  onClearFilter: () => void;
}) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 16px',
        borderRadius: 10,
        background: 'var(--gold-bg)',
        border: '1px solid var(--gold)',
        marginBottom: 16,
      }}
    >
      <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>
        Showing charts for <strong>{activePersonName}</strong>
      </span>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <button
          onClick={onShowAll}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: '5px 12px',
            borderRadius: 6,
            fontSize: 12,
            fontWeight: 500,
            background: 'var(--card)',
            color: 'var(--text-secondary)',
            border: '1px solid var(--border)',
            cursor: 'pointer',
            transition: 'all 0.15s',
          }}
        >
          <Users style={{ width: 12, height: 12 }} />
          See All Profiles' Charts
        </button>
        {personIdParam && (
          <button
            onClick={onClearFilter}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
              padding: '5px 10px',
              borderRadius: 6,
              fontSize: 12,
              fontWeight: 500,
              background: 'transparent',
              color: 'var(--text-muted)',
              border: '1px solid var(--border)',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            <X style={{ width: 12, height: 12 }} />
            Clear filter
          </button>
        )}
      </div>
    </div>
  );
}

export function AllProfilesBanner({
  onShowMyProfile,
}: {
  onShowMyProfile: () => void;
}) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 16px',
        borderRadius: 10,
        background: 'var(--card)',
        border: '1px solid var(--border)',
        marginBottom: 16,
      }}
    >
      <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
        Showing charts for all profiles
      </span>
      <button
        onClick={onShowMyProfile}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 4,
          padding: '5px 12px',
          borderRadius: 6,
          fontSize: 12,
          fontWeight: 500,
          background: 'var(--gold-bg)',
          color: 'var(--gold)',
          border: '1px solid var(--gold)',
          cursor: 'pointer',
          transition: 'all 0.15s',
        }}
      >
        Show only my profile
      </button>
    </div>
  );
}

/* ---------- Tradition Filter Pills + View Toggle ---------- */

export function FilterBar({
  filter,
  onFilterChange,
  viewMode,
  onViewModeChange,
}: {
  filter: TraditionFilter;
  onFilterChange: (f: TraditionFilter) => void;
  viewMode: ViewMode;
  onViewModeChange: (m: ViewMode) => void;
}) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 24,
        gap: 16,
        flexWrap: 'wrap',
      }}
    >
      {/* Tradition filter pills */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {TRADITION_FILTERS.map((t) => {
          const isActive = filter === t;
          return (
            <button
              key={t}
              onClick={() => onFilterChange(t)}
              className={`filter-pill ${isActive ? 'filter-pill-active' : ''}`}
              style={{
                padding: '6px 14px',
                borderRadius: 999,
                fontSize: 12,
                fontWeight: 500,
                border: isActive ? '1px solid transparent' : '1px solid var(--border)',
                background: isActive ? 'var(--gold)' : 'var(--card)',
                color: isActive ? 'var(--btn-add-text)' : 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {t}
            </button>
          );
        })}
      </div>

      {/* View toggle (Grid / List) */}
      <div
        style={{
          display: 'flex',
          border: '1px solid var(--border)',
          borderRadius: 8,
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <button
          className="view-toggle-btn"
          onClick={() => onViewModeChange('grid')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '7px 14px',
            fontSize: 12,
            fontWeight: 500,
            border: 'none',
            cursor: 'pointer',
            background:
              viewMode === 'grid' ? 'var(--gold-bg)' : 'var(--card)',
            color:
              viewMode === 'grid'
                ? 'var(--gold-bright)'
                : 'var(--text-muted)',
          }}
        >
          <LayoutGrid style={{ width: 14, height: 14 }} />
          Grid
        </button>
        <button
          className="view-toggle-btn"
          onClick={() => onViewModeChange('list')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '7px 14px',
            fontSize: 12,
            fontWeight: 500,
            border: 'none',
            borderLeft: '1px solid var(--border)',
            cursor: 'pointer',
            background:
              viewMode === 'list' ? 'var(--gold-bg)' : 'var(--card)',
            color:
              viewMode === 'list'
                ? 'var(--gold-bright)'
                : 'var(--text-muted)',
          }}
        >
          <List style={{ width: 14, height: 14 }} />
          List
        </button>
      </div>
    </div>
  );
}
