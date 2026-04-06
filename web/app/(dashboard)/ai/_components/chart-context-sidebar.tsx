'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { PanelRightClose, PanelRightOpen, Sun, Moon, Star, ArrowUpRight, Clock } from 'lucide-react';
import type { Chart, DashaResponse, Transit } from './ai-types';

export function ChartContextSidebar({
  personId,
  chartId,
  collapsed,
  onToggle,
}: {
  personId: string;
  chartId: string | undefined;
  collapsed: boolean;
  onToggle: () => void;
}) {
  const { data: chartRes } = useQuery({
    queryKey: ['chart-detail', chartId],
    queryFn: () => apiClient.get<Chart>(`/api/v1/charts/${chartId}`),
    enabled: !!chartId && !collapsed,
    staleTime: 60 * 60 * 1000,
  });

  const { data: dashaRes } = useQuery({
    queryKey: ['dasha-sidebar', personId],
    queryFn: () => apiClient.get<DashaResponse>(`/api/v1/dasha/vimshottari/${personId}`),
    enabled: !!personId && !collapsed,
    staleTime: 60 * 60 * 1000,
  });

  const { data: transitsRes } = useQuery({
    queryKey: ['transits-sidebar', personId],
    queryFn: () => apiClient.get<Transit[]>(`/api/v1/transits/current/${personId}`),
    enabled: !!personId && !collapsed,
    staleTime: 10 * 60 * 1000,
  });

  const chart = chartRes?.data;
  const planets = chart?.chart_data?.planets || {};
  const ascendant = chart?.chart_data?.ascendant;
  const sunSign = planets['Sun']?.sign || planets['sun']?.sign;
  const moonSign = planets['Moon']?.sign || planets['moon']?.sign;
  const ascSign = ascendant?.sign;
  const currentDasha = dashaRes?.data?.current_dasha || chart?.chart_data?.dasha?.current_dasha;
  const rawTransits = transitsRes?.data;
  const transits = (Array.isArray(rawTransits) ? rawTransits : (rawTransits as any)?.major_transits || []).slice(0, 3);

  const hasData = sunSign || moonSign || ascSign || currentDasha || transits.length > 0;

  if (collapsed) {
    return (
      <button
        onClick={onToggle}
        title="Show chart context"
        style={{
          position: 'absolute', right: 0, top: 72, zIndex: 10,
          width: 36, height: 36, borderRadius: '8px 0 0 8px',
          background: 'var(--surface)', border: '1px solid var(--border)', borderRight: 'none',
          color: 'var(--text-muted)', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <PanelRightOpen size={16} />
      </button>
    );
  }

  const sectionLabel: React.CSSProperties = {
    fontSize: 10, fontWeight: 600, textTransform: 'uppercase',
    letterSpacing: '1.2px', color: 'var(--text-faint)', marginBottom: 8,
  };

  const dataRow: React.CSSProperties = {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '6px 0', fontSize: 13,
  };

  return (
    <div style={{
      width: 260, flexShrink: 0, borderLeft: '1px solid var(--border)',
      background: 'var(--surface)', display: 'flex', flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Sidebar header */}
      <div style={{
        padding: '14px 16px', borderBottom: '1px solid var(--border)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
          Chart Context
        </span>
        <button
          onClick={onToggle}
          title="Hide chart context"
          style={{
            width: 28, height: 28, borderRadius: 6,
            background: 'transparent', border: '1px solid var(--border)',
            color: 'var(--text-muted)', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <PanelRightClose size={14} />
        </button>
      </div>

      {/* Sidebar content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {!personId ? (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Select a profile to see chart context.
          </p>
        ) : !hasData && !chartId ? (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            No chart data available. Calculate a chart first.
          </p>
        ) : (
          <>
            {/* Key Placements */}
            {(sunSign || moonSign || ascSign) && (
              <div style={{ marginBottom: 20 }}>
                <div style={sectionLabel}>Key Placements</div>
                {sunSign && (
                  <div style={dataRow}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
                      <Sun size={13} style={{ color: 'var(--gold)' }} /> Sun
                    </span>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{sunSign}</span>
                  </div>
                )}
                {moonSign && (
                  <div style={dataRow}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
                      <Moon size={13} style={{ color: 'var(--indigo-light)' }} /> Moon
                    </span>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{moonSign}</span>
                  </div>
                )}
                {ascSign && (
                  <div style={dataRow}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
                      <Star size={13} style={{ color: 'var(--pink)' }} /> Ascendant
                    </span>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{ascSign}</span>
                  </div>
                )}
              </div>
            )}

            {/* Current Dasha */}
            {currentDasha && (
              <div style={{ marginBottom: 20 }}>
                <div style={sectionLabel}>Current Dasha</div>
                {currentDasha.mahadasha && (
                  <div style={{
                    padding: '10px 12px', borderRadius: 8,
                    background: 'rgba(245,166,35,0.06)', border: '1px solid rgba(245,166,35,0.15)',
                    marginBottom: 8,
                  }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 2 }}>Mahadasha</div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--gold)' }}>
                      {currentDasha.mahadasha.planet}
                    </div>
                    {currentDasha.mahadasha.end_date && (
                      <div style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 2 }}>
                        <Clock size={10} style={{ marginRight: 3, verticalAlign: -1 }} />
                        Until {new Date(currentDasha.mahadasha.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </div>
                    )}
                  </div>
                )}
                {currentDasha.antardasha && (
                  <div style={{
                    padding: '10px 12px', borderRadius: 8,
                    background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.15)',
                  }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 2 }}>Antardasha</div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--indigo)' }}>
                      {currentDasha.antardasha.planet}
                    </div>
                    {currentDasha.antardasha.end_date && (
                      <div style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 2 }}>
                        <Clock size={10} style={{ marginRight: 3, verticalAlign: -1 }} />
                        Until {new Date(currentDasha.antardasha.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Active Transits */}
            {transits.length > 0 && (
              <div>
                <div style={sectionLabel}>Active Transits</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {transits.map((t: any, i: number) => (
                    <div key={i} style={{
                      padding: '8px 10px', borderRadius: 8,
                      background: 'var(--background)', border: '1px solid var(--border)',
                    }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2, display: 'flex', alignItems: 'center', gap: 4 }}>
                        <ArrowUpRight size={11} style={{ color: 'var(--gold)' }} />
                        {t.transiting_planet} {t.aspect_type} {t.natal_planet}
                      </div>
                      {t.description && (
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                          {t.description.length > 80 ? t.description.slice(0, 80) + '...' : t.description}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
