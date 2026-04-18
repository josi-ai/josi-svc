'use client';

import { Sun, Moon, Star } from 'lucide-react';
import { SouthIndianChart, NorthIndianChart, WesternWheelChart } from '@/components/charts/chart-visualizations';
import type { ChartDetail, ChartDetailPanchangItem, ChartDetailPlanetData, VargaChart } from '@/types';
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

/* --- Navamsa helpers --- */

/**
 * Build planet positions for the Navamsa (D9) chart.
 * Priority: planet.navamsa_sign > vargas.D9 sign-to-planet mapping > fallback to rasi sign.
 */
function buildNavamsaPlanets(
  planets: Record<string, ChartDetailPlanetData>,
  vargaD9?: VargaChart,
): Record<string, ChartDetailPlanetData> | null {
  // First try: per-planet navamsa_sign from backend
  const hasNavamsaSigns = Object.values(planets).some((p) => p.navamsa_sign);

  if (hasNavamsaSigns) {
    const result: Record<string, ChartDetailPlanetData> = {};
    for (const [name, data] of Object.entries(planets)) {
      result[name] = {
        ...data,
        sign: data.navamsa_sign || data.sign,
      };
    }
    return result;
  }

  // Second try: vargas.D9 is a sign-to-planets mapping { "Aries": ["Sun", "Mars"], ... }
  if (vargaD9) {
    const planetToSign: Record<string, string> = {};
    for (const [sign, planetNames] of Object.entries(vargaD9)) {
      if (!Array.isArray(planetNames)) continue;
      for (const pName of planetNames) {
        planetToSign[pName] = sign;
      }
    }

    if (Object.keys(planetToSign).length > 0) {
      const result: Record<string, ChartDetailPlanetData> = {};
      for (const [name, data] of Object.entries(planets)) {
        result[name] = {
          ...data,
          sign: planetToSign[name] || data.sign,
        };
      }
      return result;
    }
  }

  return null;
}

/**
 * Determine the Navamsa ascendant sign from vargas.D9 or the main ascendant's navamsa.
 */
function getNavamsaAscSign(
  chart: ChartDetail,
  vargaD9?: VargaChart,
): string | undefined {
  // Check if Ascendant is in the D9 varga mapping
  if (vargaD9) {
    for (const [sign, names] of Object.entries(vargaD9)) {
      if (Array.isArray(names) && names.includes('Ascendant')) {
        return sign;
      }
    }
  }
  // Fall back to the main ascendant sign
  return chart.chart_data?.ascendant?.sign;
}

/* --- Chart Visualization Section --- */

function ChartVisualizationSection({
  chart,
  chartFormat,
  planets,
  navamsaPlanets,
  navamsaAscSign,
}: {
  chart: ChartDetail;
  chartFormat: string;
  planets: Record<string, ChartDetailPlanetData>;
  navamsaPlanets: Record<string, ChartDetailPlanetData> | null;
  navamsaAscSign?: string;
}) {
  const ascSign = chart.chart_data?.ascendant?.sign;

  const renderChart = (
    p: Record<string, ChartDetailPlanetData>,
    asc?: string,
    label?: string,
  ) => {
    if (chartFormat === 'South Indian') return <SouthIndianChart planets={p} ascSign={asc} centerLabel={label} />;
    if (chartFormat === 'North Indian') return <NorthIndianChart planets={p} ascSign={asc} centerLabel={label} />;
    if (chartFormat === 'Western Wheel') return <WesternWheelChart planets={p} ascSign={asc} centerLabel={label} />;
    return <SouthIndianChart planets={p} ascSign={asc} centerLabel={label} />;
  };

  return (
    <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginBottom: 28 }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
        <p style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.8 }}>
          Rasi (D1)
        </p>
        {renderChart(planets, ascSign, 'Rasi')}
      </div>
      {navamsaPlanets && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.8 }}>
            Navamsa (D9)
          </p>
          {renderChart(navamsaPlanets, navamsaAscSign, 'D9')}
        </div>
      )}
    </div>
  );
}

/* --- Birth Panchang Section --- */

function BirthPanchangSection({ chart }: { chart: ChartDetail }) {
  const panchang = chart.chart_data?.panchang;
  if (!panchang) return null;

  const vara = panchang.vara;

  // Build detailed items for a 2-column grid
  const items: { label: string; value: string; sub?: string }[] = [];

  // Tithi
  if (panchang.tithi) {
    const t = panchang.tithi;
    const tithiName = typeof t === 'string' ? t : t.name || '\u2014';
    const paksha = typeof t === 'object' && t.paksha ? t.paksha : undefined;
    items.push({ label: 'Tithi', value: tithiName, sub: paksha });
  }

  // Nakshatra
  if (panchang.nakshatra) {
    const n = panchang.nakshatra;
    const nName = typeof n === 'string' ? n : n.name || '\u2014';
    const parts: string[] = [];
    if (typeof n === 'object') {
      if (n.pada) parts.push(`Pada ${n.pada}`);
      if (n.ruler) parts.push(`Ruler: ${n.ruler}`);
    }
    items.push({ label: 'Nakshatra', value: nName, sub: parts.join(' | ') || undefined });
  }

  // Yoga
  if (panchang.yoga) {
    const y = panchang.yoga;
    const yName = typeof y === 'string' ? y : y.name || '\u2014';
    items.push({ label: 'Yoga', value: yName });
  }

  // Karana
  if (panchang.karana) {
    const k = panchang.karana;
    const kName = typeof k === 'string' ? k : k.name || '\u2014';
    items.push({ label: 'Karana', value: kName });
  }

  // Vara (weekday)
  if (vara) {
    const varaDay = vara.day || '\u2014';
    const varaRuler = vara.ruler ? `Ruler: ${vara.ruler}` : undefined;
    items.push({ label: 'Vara', value: varaDay, sub: varaRuler });
  }

  if (items.length === 0) return null;

  return (
    <>
      <SectionHeading>Birth Panchang</SectionHeading>
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--bg-card)',
          padding: 20,
          marginBottom: 28,
        }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px 32px' }}>
          {items.map((item) => (
            <div key={item.label}>
              <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 }}>
                {item.label}
              </p>
              <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{item.value}</p>
              {item.sub && (
                <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{item.sub}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

/* --- Dasha Balance at Birth --- */

function DashaBalanceSection({ chart }: { chart: ChartDetail }) {
  const dashaData = chart.chart_data?.dasha;
  if (!dashaData) return null;

  // Try birth_balance first, then birth_details
  const birthBalance = dashaData.birth_balance;
  const birthDetails = dashaData.birth_details;

  const balancePlanet = birthBalance?.planet || birthDetails?.birth_dasha_lord;
  const balanceYears = birthBalance?.years;
  const balanceMonths = birthBalance?.months;
  const balanceDays = birthBalance?.days;

  const hasBalance = balancePlanet && (balanceYears != null || balanceMonths != null || balanceDays != null);

  if (!hasBalance) return null;

  const parts: string[] = [];
  if (balanceYears != null && balanceYears > 0) parts.push(`${balanceYears} year${balanceYears !== 1 ? 's' : ''}`);
  if (balanceMonths != null && balanceMonths > 0) parts.push(`${balanceMonths} month${balanceMonths !== 1 ? 's' : ''}`);
  if (balanceDays != null && balanceDays > 0) parts.push(`${balanceDays} day${balanceDays !== 1 ? 's' : ''}`);
  const balanceStr = parts.join(' ') || '0 days';

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 10,
        background: 'var(--bg-card)',
        padding: 14,
        marginBottom: 16,
      }}
    >
      <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 }}>
        Dasha Balance at Birth
      </p>
      <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
        {balancePlanet} Dasha — {balanceStr} remaining
      </p>
    </div>
  );
}

/* --- Technical Details Section --- */

function TechnicalDetailsSection({ chart }: { chart: ChartDetail }) {
  const chartData = chart.chart_data;

  // Ayanamsa value: check chart_data.ayanamsa (numeric) or panchang.ayanamsa
  const ayanamsaValue: number | undefined =
    (typeof chartData?.ayanamsa === 'number' ? chartData.ayanamsa : undefined) ??
    chartData?.panchang?.ayanamsa;

  const ayanamsaName = chartData?.ayanamsa_name || chart.ayanamsa;

  if (!ayanamsaName && ayanamsaValue == null) return null;

  // Format ayanamsa value as degrees/minutes/seconds
  let ayanamsaFormatted = '';
  if (ayanamsaValue != null) {
    const deg = Math.floor(ayanamsaValue);
    const minFloat = (ayanamsaValue - deg) * 60;
    const min = Math.floor(minFloat);
    const sec = Math.round((minFloat - min) * 60);
    ayanamsaFormatted = `${deg}\u00B0${min.toString().padStart(2, '0')}\u2032${sec.toString().padStart(2, '0')}\u2033`;
  }

  const displayName = ayanamsaName
    ? ayanamsaName.charAt(0).toUpperCase() + ayanamsaName.slice(1)
    : '';

  const label = displayName && ayanamsaFormatted
    ? `${displayName} (${ayanamsaFormatted})`
    : displayName || ayanamsaFormatted;

  return (
    <>
      <SectionHeading>Technical Details</SectionHeading>
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--bg-card)',
          padding: 20,
          marginBottom: 28,
        }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px 32px' }}>
          <div>
            <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 }}>
              Ayanamsa
            </p>
            <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
              {label || '\u2014'}
            </p>
          </div>
          {chart.house_system && (
            <div>
              <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 }}>
                House System
              </p>
              <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
                {chart.house_system.charAt(0).toUpperCase() + chart.house_system.slice(1)}
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

/* --- Main Component --- */

export function OverviewTab({ chart, chartFormat = 'South Indian' }: { chart: ChartDetail; chartFormat?: string }) {
  const planets = getPlanets(chart);
  const ascendant = chart.chart_data?.ascendant;
  const sun = planets['Sun'];
  const moon = planets['Moon'];
  const isVedic = chart.chart_type === 'vedic';
  const panchang = chart.chart_data?.panchang;
  const dashaData = chart.chart_data?.dasha;
  const currentDasha = dashaData?.current_dasha;

  // Build navamsa planet positions
  const vargaD9 = chart.chart_data?.vargas?.D9 as VargaChart | undefined;
  const navamsaPlanets = isVedic ? buildNavamsaPlanets(planets, vargaD9) : null;
  const navamsaAscSign = isVedic ? getNavamsaAscSign(chart, vargaD9) : undefined;

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      {/* Chart Visualizations: Rasi + Navamsa side by side (Vedic only) */}
      {isVedic && navamsaPlanets && (
        <>
          <SectionHeading>Chart Visualization</SectionHeading>
          <ChartVisualizationSection
            chart={chart}
            chartFormat={chartFormat}
            planets={planets}
            navamsaPlanets={navamsaPlanets}
            navamsaAscSign={navamsaAscSign}
          />
        </>
      )}

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

      {/* Birth Panchang (Vedic only) — enhanced version */}
      {isVedic && <BirthPanchangSection chart={chart} />}

      {/* Legacy compact Panchang if BirthPanchangSection renders nothing */}
      {isVedic && panchang && !panchang.vara && (
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

      {/* Dasha Balance at Birth (Vedic only) */}
      {isVedic && <DashaBalanceSection chart={chart} />}

      {/* Current Dasha (Vedic only) */}
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

      {/* Technical Details (Vedic only) */}
      {isVedic && <TechnicalDetailsSection chart={chart} />}
    </div>
  );
}
