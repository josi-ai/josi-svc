'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, ChevronDown, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { ChartDetail, ChartDetailPerson } from '@/types';
import { TRADITION_STYLES, TRADITIONS_LIST, CHART_FORMATS, getPlanets } from './chart-detail-helpers';

/* --- Dropdown --- */
function Dropdown({ value, options, onChange }: { value: string; options: readonly string[]; onChange?: (val: string) => void }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(!open)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 4,
          padding: '5px 10px', borderRadius: 8, border: '1px solid var(--border)',
          background: 'var(--bg-card)', color: 'var(--text-secondary)',
          fontSize: 12, fontWeight: 500, cursor: 'pointer',
        }}
      >
        {value}
        <ChevronDown style={{ width: 12, height: 12, opacity: 0.5 }} />
      </button>
      {open && (
        <div
          style={{
            position: 'absolute', top: '100%', right: 0, marginTop: 4, zIndex: 50,
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,0.08)', minWidth: 140,
            overflow: 'hidden',
          }}
        >
          {options.map((opt) => (
            <div
              key={opt}
              onClick={() => { onChange?.(opt); setOpen(false); }}
              style={{
                padding: '8px 12px', fontSize: 12, color: opt === value ? 'var(--gold)' : 'var(--text-secondary)',
                cursor: 'pointer', fontWeight: opt === value ? 600 : 400,
                background: opt === value ? 'var(--gold-bg-subtle)' : 'transparent',
              }}
            >
              {opt}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* --- Header --- */
interface ChartDetailHeaderProps {
  chart: ChartDetail;
  person?: ChartDetailPerson | null;
  chartFormat: string;
  onChartFormatChange: (val: string) => void;
  onDeleteClick: () => void;
  isDeleting: boolean;
}

export function ChartDetailHeader({
  chart,
  person,
  chartFormat,
  onChartFormatChange,
  onDeleteClick,
  isDeleting,
}: ChartDetailHeaderProps) {
  const planets = getPlanets(chart);
  const sun = planets['Sun'];
  const moon = planets['Moon'];
  const tradition = TRADITION_STYLES[chart.chart_type] || { label: chart.chart_type, variant: 'outline' as const, color: 'var(--text-secondary)' };

  const chartTitle = [
    sun ? `Sun ${sun.sign}` : null,
    moon ? `Moon ${moon.sign}` : null,
  ]
    .filter(Boolean)
    .join(', ') || `${tradition.label} Chart`;

  return (
    <div style={{ marginBottom: 24 }}>
      {/* Back link */}
      <Link
        href="/charts"
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          fontSize: 13, color: 'var(--text-muted)', textDecoration: 'none',
          marginBottom: 14, transition: 'color 0.15s',
        }}
      >
        <ArrowLeft style={{ width: 15, height: 15 }} />
        Charts
      </Link>

      {/* Title row */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ flex: 1, minWidth: 200 }}>
          <h1
            style={{
              fontFamily: "'DM Serif Display', serif",
              fontSize: 24,
              fontWeight: 400,
              color: 'var(--text-primary)',
              margin: 0,
              lineHeight: 1.2,
            }}
          >
            {chartTitle}
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 6, flexWrap: 'wrap' }}>
            {person && (
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                {person.name}
              </span>
            )}
            {person && chart.calculated_at && (
              <span style={{ fontSize: 11, color: 'var(--text-faint)' }}>&middot;</span>
            )}
            {(person?.date_of_birth || chart.calculated_at) && (
              <span style={{ fontSize: 12, color: 'var(--text-faint)' }}>
                {person?.date_of_birth
                  ? new Date(person.date_of_birth).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
                  : chart.calculated_at
                    ? new Date(chart.calculated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
                    : ''
                }
              </span>
            )}
            <Badge variant={tradition.variant}>{tradition.label}</Badge>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
          <Dropdown value={tradition.label} options={TRADITIONS_LIST} />
          <Dropdown value={chartFormat} options={CHART_FORMATS} onChange={onChartFormatChange} />
          <button
            onClick={onDeleteClick}
            disabled={isDeleting}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 5,
              padding: '7px 12px',
              fontSize: 12,
              fontWeight: 500,
              color: 'var(--text-faint)',
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              cursor: isDeleting ? 'not-allowed' : 'pointer',
              transition: 'color 0.15s, border-color 0.15s',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--red)'; e.currentTarget.style.borderColor = 'var(--red-bg)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-faint)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
          >
            <Trash2 style={{ width: 13, height: 13 }} />
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
