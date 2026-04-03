'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Sun, Moon, Star, RotateCcw, ChevronDown, Sparkles, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';
import { SouthIndianChart, NorthIndianChart, WesternWheelChart } from '@/components/charts/chart-visualizations';

/* ================================================================
   Types
   ================================================================ */

interface PlanetData {
  longitude: number;
  sign: string;
  sign_degree: number;
  house: number;
  nakshatra?: string;
  nakshatra_pada?: number;
  pada?: number;
  is_retrograde: boolean;
  speed?: number;
  dignity?: string;
}

interface HouseData {
  sign: string;
  degree: number;
}

interface PanchangItem {
  number?: number;
  name?: string;
  percent?: number;
  end_time?: string;
  paksha?: string;
  deity?: string;
  pada?: number;
  ruler?: string;
  quality?: string;
}

interface DashaPeriod {
  planet: string;
  start_date: string;
  end_date: string;
  duration_years?: number;
  progress_percentage?: number;
  remaining_days?: number;
}

interface CurrentDasha {
  mahadasha?: DashaPeriod;
  antardasha?: DashaPeriod;
  description?: string;
}

interface ChartData {
  planets: Record<string, PlanetData>;
  houses: Record<string, HouseData> | number[];
  ascendant: { sign: string; degree: number; longitude?: number; nakshatra?: string };
  panchang?: {
    tithi?: PanchangItem;
    nakshatra?: PanchangItem;
    yoga?: PanchangItem;
    karana?: PanchangItem;
    vara?: { day?: string; ruler?: string };
    sunrise?: string;
    sunset?: string;
    ayanamsa?: number;
    [key: string]: unknown;
  };
  dasha?: {
    current_dasha?: CurrentDasha;
    birth_details?: { nakshatra_name?: string; nakshatra_number?: number };
    mahadashas?: DashaPeriod[];
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

interface Chart {
  chart_id: string;
  person_id: string;
  chart_type: string;
  house_system: string;
  ayanamsa: string;
  calculated_at: string;
  chart_data: ChartData;
  planet_positions?: Record<string, PlanetData>;
  house_cusps?: number[];
  aspects?: AspectData[];
}

interface AspectData {
  planet1: string;
  planet2: string;
  aspect: string;
  orb: number;
  angle?: number;
  applying?: boolean;
}

interface Person {
  person_id: string;
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  place_of_birth?: string;
}

/* ================================================================
   Constants
   ================================================================ */

const TABS = ['Overview', 'Planets', 'Houses', 'Aspects'] as const;
type Tab = (typeof TABS)[number];

const PLANET_ORDER = [
  'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu',
];

const TRADITION_STYLES: Record<string, { label: string; variant: 'default' | 'blue' | 'green' | 'outline'; color: string }> = {
  vedic: { label: 'Vedic', variant: 'default', color: 'var(--gold)' },
  western: { label: 'Western', variant: 'blue', color: 'var(--blue)' },
  chinese: { label: 'Chinese', variant: 'green', color: 'var(--green)' },
  hellenistic: { label: 'Hellenistic', variant: 'outline', color: 'var(--text-secondary)' },
  mayan: { label: 'Mayan', variant: 'outline', color: 'var(--text-secondary)' },
  celtic: { label: 'Celtic', variant: 'outline', color: 'var(--text-secondary)' },
};

const TRADITIONS_LIST = ['Vedic', 'Western', 'Chinese'] as const;
const CHART_FORMATS = ['South Indian', 'North Indian', 'Western Wheel'] as const;

/* ================================================================
   Helpers
   ================================================================ */

function formatDegree(deg: number | undefined | null): string {
  if (deg == null || isNaN(deg)) return '\u2014';
  const d = Math.floor(deg);
  const m = Math.round((deg - d) * 60);
  return `${d}\u00B0${m.toString().padStart(2, '0')}\u2032`;
}

function safeStr(val: unknown): string {
  if (val == null) return '\u2014';
  if (typeof val === 'object') {
    // Handle panchang objects that have a .name property
    if ('name' in (val as Record<string, unknown>)) return String((val as Record<string, unknown>).name);
    return '\u2014';
  }
  return String(val);
}

function dignityStyle(dignity?: string): { color: string; fontWeight?: number } {
  if (!dignity) return { color: 'var(--text-faint)' };
  const d = dignity.toLowerCase();
  if (d === 'exalted' || d === 'own_sign' || d === 'own' || d === 'moolatrikona')
    return { color: 'var(--gold)', fontWeight: 600 };
  if (d === 'friendly' || d === 'friend')
    return { color: 'var(--green)', fontWeight: 500 };
  if (d === 'debilitated' || d === 'enemy')
    return { color: 'var(--red)', fontWeight: 600 };
  return { color: 'var(--text-secondary)' };
}

function dignityLabel(dignity?: string): string {
  if (!dignity || dignity === 'neutral') return '\u2014';
  return dignity.charAt(0).toUpperCase() + dignity.slice(1).replace('_', ' ');
}

function getPlanets(chart: Chart): Record<string, PlanetData> {
  return chart.chart_data?.planets || chart.planet_positions || {};
}

/* ================================================================
   Sub-components
   ================================================================ */

function LoadingState() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            width: 48, height: 48, borderRadius: '50%', margin: '0 auto 16px',
            background: 'var(--gold-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <Star style={{ width: 20, height: 20, color: 'var(--gold)', animation: 'pulse 2s infinite' }} />
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading chart data...</p>
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            width: 48, height: 48, borderRadius: '50%', margin: '0 auto 16px',
            background: 'var(--red-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <span style={{ fontSize: 18, color: 'var(--red)', fontWeight: 700 }}>!</span>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Failed to load chart</p>
        <p style={{ fontSize: 11, color: 'var(--text-faint)' }}>{message}</p>
      </div>
    </div>
  );
}

/* --- Dropdown (functional) --- */
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

/* --- Quick Info Panel --- */
function QuickInfoPanel({ chart }: { chart: Chart }) {
  const planets = getPlanets(chart);
  const sun = planets['Sun'];
  const moon = planets['Moon'];
  const asc = chart.chart_data?.ascendant;
  const isVedic = chart.chart_type === 'vedic';
  const panchang = chart.chart_data?.panchang;

  // Determine nakshatra value
  let nakshatraValue = '\u2014';
  if (isVedic && moon?.nakshatra) {
    nakshatraValue = moon.nakshatra;
  } else if (isVedic && panchang?.nakshatra) {
    nakshatraValue = safeStr(panchang.nakshatra?.name || panchang.nakshatra);
  }

  const items: { label: string; value: string }[] = [
    { label: 'Sun Sign', value: sun?.sign || '\u2014' },
    { label: 'Moon Sign', value: moon?.sign || '\u2014' },
    { label: 'Ascendant', value: asc?.sign || '\u2014' },
    { label: 'Nakshatra', value: nakshatraValue },
    { label: 'Ayanamsa', value: chart.ayanamsa ? chart.ayanamsa.charAt(0).toUpperCase() + chart.ayanamsa.slice(1) : '\u2014' },
    { label: 'House System', value: chart.house_system ? chart.house_system.charAt(0).toUpperCase() + chart.house_system.slice(1) : '\u2014' },
    { label: 'Chart Type', value: chart.chart_type ? chart.chart_type.charAt(0).toUpperCase() + chart.chart_type.slice(1) : '\u2014' },
    { label: 'Calculated Date', value: chart.calculated_at ? new Date(chart.calculated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '\u2014' },
  ];

  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '16px 24px',
        }}
      >
        {items.map((item) => (
          <div key={item.label}>
            <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 }}>
              {item.label}
            </p>
            <p style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 600 }}>{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* --- Overview Tab --- */
function OverviewTab({ chart }: { chart: Chart }) {
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

function PanchangCard({ label, item }: { label: string; item?: PanchangItem | string }) {
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

/* --- Planets Tab --- */
function PlanetsTab({ chart }: { chart: Chart }) {
  const planets = getPlanets(chart);
  const isVedic = chart.chart_type === 'vedic';

  const orderedPlanets = PLANET_ORDER.filter((p) => planets[p]);
  const extraPlanets = Object.keys(planets).filter((p) => !PLANET_ORDER.includes(p));
  const allPlanets = [...orderedPlanets, ...extraPlanets];

  const headerStyle: React.CSSProperties = {
    padding: '10px 16px',
    fontSize: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    color: 'var(--text-faint)',
    fontWeight: 600,
    textAlign: 'left',
    borderBottom: '1px solid var(--border)',
  };

  const cellStyle: React.CSSProperties = {
    padding: '10px 16px',
    fontSize: 13,
    color: 'var(--text-secondary)',
    borderBottom: '1px solid var(--border)',
  };

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--bg-card)',
          overflow: 'hidden',
        }}
      >
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>Planet</th>
                <th style={headerStyle}>Sign</th>
                <th style={headerStyle}>Degree</th>
                <th style={headerStyle}>House</th>
                {isVedic && <th style={headerStyle}>Nakshatra</th>}
                {isVedic && <th style={headerStyle}>Pada</th>}
                <th style={headerStyle}>Dignity</th>
                <th style={{ ...headerStyle, textAlign: 'center' }}>Retro</th>
              </tr>
            </thead>
            <tbody>
              {allPlanets.map((name) => {
                const p = planets[name];
                if (!p) return null;
                const isRetro = p.is_retrograde || (p.speed != null && p.speed < 0);
                const dStyle = dignityStyle(p.dignity);
                return (
                  <tr
                    key={name}
                    style={{ transition: 'background 0.15s' }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{name}</td>
                    <td style={cellStyle}>{p.sign || '\u2014'}</td>
                    <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>{formatDegree(p.sign_degree)}</td>
                    <td style={cellStyle}>{p.house || '\u2014'}</td>
                    {isVedic && <td style={cellStyle}>{p.nakshatra || '\u2014'}</td>}
                    {isVedic && <td style={cellStyle}>{p.nakshatra_pada || p.pada || '\u2014'}</td>}
                    <td style={{ ...cellStyle, ...dStyle }}>{dignityLabel(p.dignity)}</td>
                    <td style={{ ...cellStyle, textAlign: 'center' }}>
                      {isRetro ? (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, color: 'var(--red)', fontWeight: 600, fontSize: 11 }}>
                          <RotateCcw style={{ width: 11, height: 11 }} /> &#x211E;
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-faint)' }}>\u2014</span>
                      )}
                    </td>
                  </tr>
                );
              })}
              {allPlanets.length === 0 && (
                <tr>
                  <td colSpan={isVedic ? 8 : 6} style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                    No planet data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* --- Houses Tab --- */
function HousesTab({ chart }: { chart: Chart }) {
  const houses = chart.chart_data?.houses;
  const cusps = chart.house_cusps;

  // Try to build house data from either format
  let houseRows: { num: number; sign: string; degree: string; lord: string }[] = [];

  const SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
  ];
  const LORDS: Record<string, string> = {
    Aries: 'Mars', Taurus: 'Venus', Gemini: 'Mercury', Cancer: 'Moon',
    Leo: 'Sun', Virgo: 'Mercury', Libra: 'Venus', Scorpio: 'Mars',
    Sagittarius: 'Jupiter', Capricorn: 'Saturn', Aquarius: 'Saturn', Pisces: 'Jupiter',
  };

  if (Array.isArray(houses) && houses.length > 0) {
    houseRows = (houses as number[]).map((deg: number, i: number) => {
      const sign = SIGNS[Math.floor(deg / 30) % 12];
      return { num: i + 1, sign, degree: formatDegree(deg % 30), lord: LORDS[sign] || '\u2014' };
    });
  } else if (Array.isArray(cusps) && cusps.length > 0) {
    houseRows = cusps.map((deg, i) => {
      const sign = SIGNS[Math.floor(deg / 30) % 12];
      return { num: i + 1, sign, degree: formatDegree(deg % 30), lord: LORDS[sign] || '\u2014' };
    });
  } else if (houses && typeof houses === 'object' && !Array.isArray(houses)) {
    // Record<string, HouseData> format
    const housesObj = houses as Record<string, HouseData>;
    houseRows = Object.entries(housesObj).map(([key, data]) => ({
      num: parseInt(key) || 0,
      sign: data.sign || '\u2014',
      degree: formatDegree(data.degree),
      lord: LORDS[data.sign] || '\u2014',
    })).sort((a, b) => a.num - b.num);
  }

  if (houseRows.length === 0) {
    return (
      <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
        <ComingSoonCard icon={<Star style={{ width: 20, height: 20, color: 'var(--blue)' }} />} bgColor="var(--blue-bg)" message="Houses data not available for this chart" />
      </div>
    );
  }

  const headerStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.8,
    color: 'var(--text-faint)', fontWeight: 600, textAlign: 'left', borderBottom: '1px solid var(--border)',
  };
  const cellStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 13, color: 'var(--text-secondary)', borderBottom: '1px solid var(--border)',
  };

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      <div style={{ border: '1px solid var(--border)', borderRadius: 12, background: 'var(--bg-card)', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>House</th>
                <th style={headerStyle}>Sign</th>
                <th style={headerStyle}>Degree</th>
                <th style={headerStyle}>Lord</th>
              </tr>
            </thead>
            <tbody>
              {houseRows.map((h) => (
                <tr
                  key={h.num}
                  style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{h.num}</td>
                  <td style={cellStyle}>{h.sign}</td>
                  <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>{h.degree}</td>
                  <td style={cellStyle}>{h.lord}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* --- Aspects Tab --- */
function AspectsTab({ chart }: { chart: Chart }) {
  const aspects: AspectData[] = chart.aspects || (chart.chart_data as unknown as Record<string, unknown>)?.aspects as AspectData[] || [];

  if (aspects.length === 0) {
    return (
      <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
        <ComingSoonCard
          icon={<Sparkles style={{ width: 20, height: 20, color: 'var(--green)' }} />}
          bgColor="var(--green-bg)"
          message="No aspects data available for this chart"
        />
      </div>
    );
  }

  const headerStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.8,
    color: 'var(--text-faint)', fontWeight: 600, textAlign: 'left', borderBottom: '1px solid var(--border)',
  };
  const cellStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 13, color: 'var(--text-secondary)', borderBottom: '1px solid var(--border)',
  };

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      <div style={{ border: '1px solid var(--border)', borderRadius: 12, background: 'var(--bg-card)', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>Planet 1</th>
                <th style={headerStyle}>Aspect</th>
                <th style={headerStyle}>Planet 2</th>
                <th style={headerStyle}>Orb</th>
                <th style={{ ...headerStyle, textAlign: 'center' }}>Applying / Separating</th>
              </tr>
            </thead>
            <tbody>
              {aspects.map((a, i) => (
                <tr
                  key={`${a.planet1}-${a.planet2}-${a.aspect}-${i}`}
                  style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{a.planet1}</td>
                  <td style={cellStyle}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                      <span>{a.aspect}</span>
                      {a.angle != null && (
                        <span style={{ fontSize: 10, color: 'var(--text-faint)', fontFamily: 'monospace' }}>
                          {a.angle}&deg;
                        </span>
                      )}
                    </span>
                  </td>
                  <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{a.planet2}</td>
                  <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>
                    {a.orb != null ? `${a.orb.toFixed(2)}\u00B0` : '\u2014'}
                  </td>
                  <td style={{ ...cellStyle, textAlign: 'center' }}>
                    {a.applying != null ? (
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 500,
                          color: a.applying ? 'var(--green)' : 'var(--text-faint)',
                        }}
                      >
                        {a.applying ? 'Applying' : 'Separating'}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)' }}>{'\u2014'}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ComingSoonCard({ icon, bgColor, message }: { icon: React.ReactNode; bgColor: string; message: string }) {
  return (
    <div
      style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        border: '1px solid var(--border)', borderRadius: 12, background: 'var(--bg-card)',
        padding: '64px 24px', textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 48, height: 48, borderRadius: 12, display: 'flex',
          alignItems: 'center', justifyContent: 'center', background: bgColor, marginBottom: 16,
        }}
      >
        {icon}
      </div>
      <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>{message}</p>
    </div>
  );
}

/* ================================================================
   Main Page
   ================================================================ */

export default function ChartDetailPage() {
  const params = useParams<{ chartId: string }>();
  const chartId = params.chartId;
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>('Overview');
  const [chartFormat, setChartFormat] = useState<string>('South Indian');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.delete(`/api/v1/charts/${chartId}`),
    onSuccess: () => router.push('/charts'),
  });

  // Fetch chart
  const {
    data: chartResponse,
    isLoading: chartLoading,
    isError: chartError,
    error: chartErr,
  } = useQuery({
    queryKey: ['chart', chartId],
    queryFn: () => apiClient.get<Chart>(`/api/v1/charts/${chartId}`),
    enabled: !!chartId,
  });

  const chart = chartResponse?.data;

  // Fetch person for name/date
  const {
    data: personResponse,
  } = useQuery({
    queryKey: ['person', chart?.person_id],
    queryFn: () => apiClient.get<Person>(`/api/v1/persons/${chart!.person_id}`),
    enabled: !!chart?.person_id,
  });

  const person = personResponse?.data;

  if (chartLoading) return <LoadingState />;
  if (chartError) return <ErrorState message={(chartErr as Error).message} />;
  if (!chart) return <ErrorState message="Chart not found" />;

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
    <div>
      {/* ---- Inject keyframe for tab fade-in ---- */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* ===== TOPBAR ===== */}
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
            <Dropdown value={chartFormat} options={CHART_FORMATS} onChange={setChartFormat} />
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={deleteMutation.isPending}
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
                cursor: deleteMutation.isPending ? 'not-allowed' : 'pointer',
                transition: 'color 0.15s, border-color 0.15s',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = '#E5484D'; e.currentTarget.style.borderColor = 'rgba(229,72,77,0.3)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-faint)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
            >
              <Trash2 style={{ width: 13, height: 13 }} />
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </div>

      {/* ===== CHART VISUALIZATION + QUICK INFO ===== */}
      <div
        style={{
          display: 'flex',
          gap: 28,
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          marginBottom: 28,
          padding: 20,
          border: '1px solid var(--border)',
          borderRadius: 14,
          background: 'var(--bg-card)',
        }}
      >
        {chartFormat === 'South Indian' && <SouthIndianChart planets={planets} ascSign={chart.chart_data?.ascendant?.sign} />}
        {chartFormat === 'North Indian' && <NorthIndianChart planets={planets} ascSign={chart.chart_data?.ascendant?.sign} />}
        {chartFormat === 'Western Wheel' && <WesternWheelChart planets={planets} ascSign={chart.chart_data?.ascendant?.sign} />}
        <QuickInfoPanel chart={chart} />
      </div>

      {/* ===== STICKY TAB BAR ===== */}
      <div
        style={{
          display: 'flex',
          gap: 0,
          borderBottom: '1px solid var(--border)',
          marginBottom: 24,
          position: 'sticky',
          top: 0,
          zIndex: 10,
          background: 'var(--bg-page, var(--background))',
          paddingTop: 2,
        }}
      >
        {TABS.map((tab) => {
          const isActive = activeTab === tab;
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '10px 18px',
                fontSize: 13,
                fontWeight: isActive ? 600 : 500,
                color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                background: 'transparent',
                border: 'none',
                borderBottom: isActive ? '3px solid var(--gold)' : '3px solid transparent',
                cursor: 'pointer',
                transition: 'color 0.15s, border-color 0.15s',
                marginBottom: -1,
              }}
            >
              {tab}
            </button>
          );
        })}
      </div>

      {/* ===== TAB CONTENT ===== */}
      {activeTab === 'Overview' && <OverviewTab chart={chart} />}
      {activeTab === 'Planets' && <PlanetsTab chart={chart} />}
      {activeTab === 'Houses' && <HousesTab chart={chart} />}
      {activeTab === 'Aspects' && <AspectsTab chart={chart} />}

      {/* Delete confirmation modal */}
      <ConfirmDialog
        open={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this chart?"
        description="This chart and its interpretations will be removed. You can always recalculate it later."
        confirmLabel="Delete Chart"
        loading={deleteMutation.isPending}
      />
    </div>
  );
}
