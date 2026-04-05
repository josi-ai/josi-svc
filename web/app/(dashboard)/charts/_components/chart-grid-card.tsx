'use client';

import Link from 'next/link';
import { Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { ChartItem } from './chart-types';
import { getTradition, getChartName, getAscendant, getAscendantNakshatra, formatDate } from './chart-helpers';
import { MiniChart } from './mini-chart';

export function ChartGridCard({
  chart,
  personName,
  onDelete,
}: {
  chart: ChartItem;
  personName?: string;
  onDelete?: (chartId: string) => void;
}) {
  const tradition = getTradition(chart);
  const chartName = getChartName(chart);
  const ascendant = getAscendant(chart);
  const ascNakshatra = getAscendantNakshatra(chart);

  return (
    <Link href={`/charts/${chart.chart_id}`} style={{ textDecoration: 'none' }}>
      <div
        className="chart-grid-card"
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: 14,
          padding: 20,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Delete button */}
        {onDelete && (
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onDelete(chart.chart_id);
            }}
            style={{
              position: 'absolute',
              top: 10,
              right: 10,
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              padding: 4,
              borderRadius: 6,
              color: 'var(--text-faint)',
              transition: 'color 0.15s, background 0.15s',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--red)'; e.currentTarget.style.background = 'var(--red-bg)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-faint)'; e.currentTarget.style.background = 'transparent'; }}
            title="Delete chart"
          >
            <Trash2 style={{ width: 14, height: 14 }} />
          </button>
        )}

        <div style={{ display: 'flex', gap: 16 }}>
          {/* Mini chart visualization */}
          <MiniChart chart={chart} />

          {/* Card info */}
          <div
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              minWidth: 0,
            }}
          >
            {/* Tradition badge */}
            <div style={{ marginBottom: 8 }}>
              <Badge variant={tradition.variant}>{tradition.label}</Badge>
            </div>

            {/* Chart name (Sun sign, Moon sign) */}
            <p
              className="font-display chart-card-name"
              style={{
                fontSize: 15,
                color: 'var(--text-primary)',
                marginBottom: 2,
                lineHeight: 1.3,
                transition: 'color 0.2s',
              }}
            >
              {chartName}
            </p>

            {/* Person name */}
            {personName && (
              <p
                style={{
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  marginBottom: 6,
                }}
              >
                {personName}
              </p>
            )}

            {/* Key placements */}
            {ascendant.sign && (
              <p
                style={{
                  fontSize: 11,
                  color: 'var(--text-muted)',
                  marginBottom: 4,
                }}
              >
                Asc {ascendant.sign}
                {ascNakshatra ? ` \u00B7 ${ascNakshatra}` : ''}
              </p>
            )}

            {/* Spacer */}
            <div style={{ flex: 1 }} />

            {/* Date */}
            <p style={{ fontSize: 11, color: 'var(--text-faint)' }}>
              {chart.calculated_at
                ? `Calculated ${formatDate(chart.calculated_at)}`
                : ''}
            </p>
          </div>
        </div>
      </div>
    </Link>
  );
}
