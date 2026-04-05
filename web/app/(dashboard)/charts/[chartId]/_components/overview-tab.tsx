'use client';

import { Sun, Moon, Star } from 'lucide-react';
import type { ChartDetail, ChartDetailPanchangItem } from '@/types';
import { formatDegree, getPlanets } from './chart-detail-helpers';

/* --- Sub-components --- */

function SectionHeading({ children }: { children: React.ReactNode }) {
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

function PlacementCard({
  label, icon, sign, degree, nakshatra,
}: {
  label: string;
  icon: React.ReactNode;
  sign: string;
  degree: number;
  nakshatra?: string;
}) {
  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--bg-card)',
        padding: 16,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <div
          style={{
            width: 32, height: 32, borderRadius: 10, display: 'flex',
            alignItems: 'center', justifyContent: 'center', background: 'var(--gold-bg)',
          }}
        >
          {icon}
        </div>
        <div>
          <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8 }}>{label}</p>
          <p style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{sign}</p>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
          <span style={{ color: 'var(--text-faint)' }}>Degree</span>
          <span style={{ color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: 10 }}>{formatDegree(degree)}</span>
        </div>
        {nakshatra && (
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
            <span style={{ color: 'var(--text-faint)' }}>Nakshatra</span>
            <span style={{ color: 'var(--text-secondary)' }}>{nakshatra}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function PanchangCard({ label, item }: { label: string; item?: ChartDetailPanchangItem | string }) {
  if (!item) return null;

  // Handle case where panchang field is a plain string (legacy) or an object
  let name = '\u2014';
  let extra: string | null = null;

  if (typeof item === 'string') {
    name = item;
  } else if (typeof item === 'object' && item !== null) {
    name = item.name || '\u2014';
    if (item.paksha) extra = item.paksha;
    else if (item.quality) extra = item.quality;
    else if (item.ruler) extra = item.ruler;
  }

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 10,
        background: 'var(--bg-card)',
        padding: 14,
      }}
    >
      <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 }}>
        {label}
      </p>
      <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{name}</p>
      {extra && <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{extra}</p>}
    </div>
  );
}

/* --- Main Component --- */

export function OverviewTab({ chart }: { chart: ChartDetail }) {
  const planets = getPlanets(chart);
  const ascendant = chart.chart_data?.ascendant;
  const sun = planets['Sun'];
  const moon = planets['Moon'];
  const isVedic = chart.chart_type === 'vedic';
  const panchang = chart.chart_data?.panchang;
  const dashaData = chart.chart_data?.dasha;
  const currentDasha = dashaData?.current_dasha;

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      {/* Key Placements */}
      <SectionHeading>Key Placements</SectionHeading>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 28 }}>
        {sun && (
          <PlacementCard
            label="Sun"
            icon={<Sun style={{ width: 15, height: 15, color: 'var(--gold)' }} />}
            sign={sun.sign}
            degree={sun.sign_degree}
            nakshatra={isVedic ? sun.nakshatra : undefined}
          />
        )}
        {moon && (
          <PlacementCard
            label="Moon"
            icon={<Moon style={{ width: 15, height: 15, color: 'var(--gold)' }} />}
            sign={moon.sign}
            degree={moon.sign_degree}
            nakshatra={isVedic ? moon.nakshatra : undefined}
          />
        )}
        {ascendant && (
          <PlacementCard
            label="Ascendant"
            icon={<Star style={{ width: 15, height: 15, color: 'var(--gold)' }} />}
            sign={ascendant.sign}
            degree={ascendant.degree}
            nakshatra={isVedic ? ascendant.nakshatra : undefined}
          />
        )}
        {planets['Rahu'] && (
          <PlacementCard
            label="Rahu"
            icon={<Star style={{ width: 15, height: 15, color: 'var(--gold)' }} />}
            sign={planets['Rahu'].sign}
            degree={planets['Rahu'].sign_degree}
            nakshatra={isVedic ? planets['Rahu'].nakshatra : undefined}
          />
        )}
      </div>

      {/* Panchang (Vedic only) */}
      {isVedic && panchang && (
        <>
          <SectionHeading>Panchang</SectionHeading>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 28 }}>
            <PanchangCard label="Tithi" item={panchang.tithi} />
            <PanchangCard label="Nakshatra" item={panchang.nakshatra} />
            <PanchangCard label="Yoga" item={panchang.yoga} />
            <PanchangCard label="Karana" item={panchang.karana} />
          </div>
        </>
      )}

      {/* Dasha (Vedic only) */}
      {isVedic && currentDasha && (
        <>
          <SectionHeading>Current Dasha</SectionHeading>
          <div
            style={{
              border: '1px solid var(--border)',
              borderRadius: 12,
              background: 'var(--bg-card)',
              padding: 20,
              marginBottom: 28,
            }}
          >
            <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap', marginBottom: currentDasha.mahadasha?.progress_percentage != null ? 16 : 0 }}>
              {currentDasha.mahadasha && (
                <div>
                  <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 }}>
                    Maha Dasha
                  </p>
                  <p style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
                    {currentDasha.mahadasha.planet}
                  </p>
                  {currentDasha.mahadasha.remaining_days != null && (
                    <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 2 }}>
                      {Math.round(currentDasha.mahadasha.remaining_days / 365.25 * 10) / 10} years remaining
                    </p>
                  )}
                </div>
              )}
              {currentDasha.antardasha && (
                <div>
                  <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 }}>
                    Antar Dasha
                  </p>
                  <p style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
                    {currentDasha.antardasha.planet}
                  </p>
                  {currentDasha.antardasha.remaining_days != null && (
                    <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 2 }}>
                      {currentDasha.antardasha.remaining_days} days remaining
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Progress bar for Maha Dasha */}
            {currentDasha.mahadasha?.progress_percentage != null && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-faint)', marginBottom: 4 }}>
                  <span>Progress</span>
                  <span>{Math.round(currentDasha.mahadasha.progress_percentage)}%</span>
                </div>
                <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${Math.min(100, currentDasha.mahadasha.progress_percentage)}%`,
                      background: 'var(--gold)',
                      borderRadius: 3,
                      transition: 'width 0.5s ease-out',
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
