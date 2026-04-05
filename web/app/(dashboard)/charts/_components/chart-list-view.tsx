'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { ArrowUpDown, ChevronDown, ChevronUp, Eye, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { ChartItem, SortColumn, SortDir } from './chart-types';
import { getTradition, getSunSign, getMoonSign, getChartName, getAscendant, formatDate } from './chart-helpers';

/* ---------- Sortable Table Header ---------- */

function SortableHeader({
  label,
  column,
  currentSort,
  currentDir,
  onSort,
}: {
  label: string;
  column: SortColumn;
  currentSort: SortColumn;
  currentDir: SortDir;
  onSort: (col: SortColumn) => void;
}) {
  const isActive = currentSort === column;
  return (
    <th
      onClick={() => onSort(column)}
      style={{
        padding: '12px 20px',
        textAlign: 'left',
        fontSize: 11,
        fontWeight: 600,
        textTransform: 'uppercase' as const,
        letterSpacing: '0.5px',
        color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
        cursor: 'pointer',
        userSelect: 'none',
        whiteSpace: 'nowrap',
        transition: 'color 0.15s',
      }}
    >
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
        {label}
        {isActive ? (
          currentDir === 'asc' ? (
            <ChevronUp style={{ width: 12, height: 12 }} />
          ) : (
            <ChevronDown style={{ width: 12, height: 12 }} />
          )
        ) : (
          <ArrowUpDown
            style={{ width: 10, height: 10, opacity: 0.4 }}
          />
        )}
      </span>
    </th>
  );
}

/* ---------- ChartListView ---------- */

export function ChartListView({
  charts,
  personMap,
  onDelete,
}: {
  charts: ChartItem[];
  personMap: Record<string, string>;
  onDelete?: (chartId: string) => void;
}) {
  const [sortCol, setSortCol] = useState<SortColumn>('date');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  const handleSort = (col: SortColumn) => {
    if (sortCol === col) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortCol(col);
      setSortDir('asc');
    }
  };

  const sortedCharts = useMemo(() => {
    const sorted = [...charts];
    sorted.sort((a, b) => {
      let cmp = 0;
      switch (sortCol) {
        case 'name':
          cmp = (personMap[a.person_id] || '').localeCompare(
            personMap[b.person_id] || ''
          );
          break;
        case 'sun_moon':
          cmp = getChartName(a).localeCompare(getChartName(b));
          break;
        case 'ascendant':
          cmp = (getAscendant(a).sign || '').localeCompare(
            getAscendant(b).sign || ''
          );
          break;
        case 'tradition':
          cmp = a.chart_type.localeCompare(b.chart_type);
          break;
        case 'date':
          cmp =
            new Date(a.calculated_at || 0).getTime() -
            new Date(b.calculated_at || 0).getTime();
          break;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return sorted;
  }, [charts, sortCol, sortDir, personMap]);

  return (
    <div
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 14,
        overflow: 'hidden',
      }}
    >
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr
              style={{
                borderBottom: '1px solid var(--border)',
              }}
            >
              <SortableHeader
                label="Name"
                column="name"
                currentSort={sortCol}
                currentDir={sortDir}
                onSort={handleSort}
              />
              <SortableHeader
                label="Sun / Moon"
                column="sun_moon"
                currentSort={sortCol}
                currentDir={sortDir}
                onSort={handleSort}
              />
              <SortableHeader
                label="Ascendant"
                column="ascendant"
                currentSort={sortCol}
                currentDir={sortDir}
                onSort={handleSort}
              />
              <SortableHeader
                label="Tradition"
                column="tradition"
                currentSort={sortCol}
                currentDir={sortDir}
                onSort={handleSort}
              />
              <SortableHeader
                label="Date"
                column="date"
                currentSort={sortCol}
                currentDir={sortDir}
                onSort={handleSort}
              />
              <th
                style={{
                  padding: '12px 20px',
                  textAlign: 'center',
                  fontSize: 11,
                  fontWeight: 600,
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.5px',
                  color: 'var(--text-muted)',
                }}
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedCharts.map((chart, idx) => {
              const tradition = getTradition(chart);
              const sun = getSunSign(chart);
              const moon = getMoonSign(chart);
              const asc = getAscendant(chart);
              const isLast = idx === sortedCharts.length - 1;

              return (
                <tr
                  key={chart.chart_id}
                  className="chart-list-row"
                  style={{
                    borderBottom: isLast ? 'none' : '1px solid var(--border)',
                    transition: 'background 0.15s',
                    cursor: 'pointer',
                  }}
                  onClick={() => {
                    window.location.href = `/charts/${chart.chart_id}`;
                  }}
                >
                  <td
                    style={{
                      padding: '14px 20px',
                      fontWeight: 500,
                      color: 'var(--text-primary)',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {personMap[chart.person_id] || 'Unknown'}
                  </td>
                  <td style={{ padding: '14px 20px', color: 'var(--text-secondary)' }}>
                    {sun && moon
                      ? `${sun} / ${moon}`
                      : sun || moon || '-'}
                  </td>
                  <td style={{ padding: '14px 20px', color: 'var(--text-secondary)' }}>
                    {asc.sign || '-'}
                  </td>
                  <td style={{ padding: '14px 20px' }}>
                    <Badge variant={tradition.variant}>{tradition.label}</Badge>
                  </td>
                  <td
                    style={{
                      padding: '14px 20px',
                      color: 'var(--text-muted)',
                      whiteSpace: 'nowrap',
                      fontSize: 12,
                    }}
                  >
                    {chart.calculated_at ? formatDate(chart.calculated_at) : '-'}
                  </td>
                  <td style={{ padding: '14px 20px', textAlign: 'center' }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12 }}>
                      <Link
                        href={`/charts/${chart.chart_id}`}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 4,
                          fontSize: 12,
                          fontWeight: 500,
                          color: 'var(--gold)',
                          textDecoration: 'none',
                        }}
                      >
                        <Eye style={{ width: 13, height: 13 }} />
                        View
                      </Link>
                      {onDelete && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDelete(chart.chart_id);
                          }}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                            fontSize: 12,
                            fontWeight: 500,
                            color: 'var(--text-faint)',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: 0,
                            transition: 'color 0.15s',
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--red)'; }}
                          onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-faint)'; }}
                        >
                          <Trash2 style={{ width: 13, height: 13 }} />
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
