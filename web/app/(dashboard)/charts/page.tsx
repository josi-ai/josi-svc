'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import {
  Plus,
  Star,
  LayoutGrid,
  List,
  ArrowUpDown,
  ChevronDown,
  ChevronUp,
  Eye,
} from 'lucide-react';
import Link from 'next/link';

/* ---------- Types ---------- */

interface Person {
  person_id: string;
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  place_of_birth?: string;
}

interface PlanetData {
  sign: string;
  nakshatra?: string;
  nakshatra_pada?: number;
  house?: number;
  sign_degree?: number;
  [key: string]: unknown;
}

interface ChartDataInner {
  planets?: Record<string, PlanetData>;
  ascendant?: { sign: string; degree: number };
}

interface ChartItem {
  chart_id: string;
  person_id: string;
  chart_type: string;
  house_system: string;
  ayanamsa: string;
  calculated_at: string;
  chart_data?: ChartDataInner;
  planet_positions?: Record<string, PlanetData>;
}

/* ---------- Constants ---------- */

const TRADITION_FILTERS = [
  'All',
  'Vedic',
  'Western',
  'Chinese',
  'Hellenistic',
  'Mayan',
  'Celtic',
] as const;
type TraditionFilter = (typeof TRADITION_FILTERS)[number];

type ViewMode = 'grid' | 'list';

type SortColumn = 'name' | 'sun_moon' | 'ascendant' | 'tradition' | 'date';
type SortDir = 'asc' | 'desc';

const TRADITION_STYLES: Record<
  string,
  { label: string; variant: 'default' | 'blue' | 'green' | 'outline'; color: string }
> = {
  vedic: { label: 'Vedic', variant: 'default', color: 'var(--gold)' },
  western: { label: 'Western', variant: 'blue', color: '#4A7FB5' },
  chinese: { label: 'Chinese', variant: 'green', color: '#528E62' },
  hellenistic: { label: 'Hellenistic', variant: 'outline', color: '#7B5AAF' },
  mayan: { label: 'Mayan', variant: 'outline', color: '#C46A50' },
  celtic: { label: 'Celtic', variant: 'outline', color: '#3A9DB5' },
};

/* Signs abbreviation map for the South Indian chart grid */
const SIGN_CELLS: string[] = [
  'Pis', 'Ari', 'Tau', 'Gem',
  'Aqu', '',     '',    'Can',
  'Cap', '',     '',    'Leo',
  'Sag', 'Sco', 'Lib', 'Vir',
];

/* ---------- Helpers ---------- */

function getPlanets(chart: ChartItem): Record<string, PlanetData> {
  return chart.chart_data?.planets || chart.planet_positions || {};
}

function getSunSign(chart: ChartItem): string {
  return getPlanets(chart)['Sun']?.sign || '';
}

function getMoonSign(chart: ChartItem): string {
  return getPlanets(chart)['Moon']?.sign || '';
}

function getChartName(chart: ChartItem): string {
  const sun = getSunSign(chart);
  const moon = getMoonSign(chart);
  const parts: string[] = [];
  if (sun) parts.push(`Sun ${sun}`);
  if (moon) parts.push(`Moon ${moon}`);
  return parts.length > 0 ? parts.join(', ') : 'Chart calculated';
}

function getAscendant(chart: ChartItem): { sign: string; nakshatra?: string } {
  const asc = chart.chart_data?.ascendant;
  return { sign: asc?.sign || '', nakshatra: undefined };
}

function getAscendantNakshatra(chart: ChartItem): string | undefined {
  // Try to find ascendant nakshatra from planet data (some APIs include it)
  const planets = getPlanets(chart);
  const asc = planets['Ascendant'] || planets['Lagna'];
  return asc?.nakshatra;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function getTradition(chart: ChartItem) {
  return (
    TRADITION_STYLES[chart.chart_type.toLowerCase()] || {
      label: chart.chart_type.charAt(0).toUpperCase() + chart.chart_type.slice(1),
      variant: 'outline' as const,
      color: 'var(--text-muted)',
    }
  );
}

/**
 * Build a simple planet-to-sign lookup for the mini chart.
 * Returns a map of sign abbreviation -> planet abbreviations in that sign.
 */
function buildSignPlanetMap(chart: ChartItem): Record<string, string[]> {
  const SIGN_ABBR: Record<string, string> = {
    Aries: 'Ari', Taurus: 'Tau', Gemini: 'Gem', Cancer: 'Can',
    Leo: 'Leo', Virgo: 'Vir', Libra: 'Lib', Scorpio: 'Sco',
    Sagittarius: 'Sag', Capricorn: 'Cap', Aquarius: 'Aqu', Pisces: 'Pis',
  };
  const PLANET_ABBR: Record<string, string> = {
    Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me',
    Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke',
  };
  const planets = getPlanets(chart);
  const map: Record<string, string[]> = {};

  Object.entries(planets).forEach(([name, data]) => {
    if (!data.sign) return;
    const signKey = SIGN_ABBR[data.sign] || data.sign.slice(0, 3);
    const planetKey = PLANET_ABBR[name] || name.slice(0, 2);
    if (!map[signKey]) map[signKey] = [];
    map[signKey].push(planetKey);
  });

  // Mark ascendant
  const asc = chart.chart_data?.ascendant;
  if (asc?.sign) {
    const signKey = SIGN_ABBR[asc.sign] || asc.sign.slice(0, 3);
    if (!map[signKey]) map[signKey] = [];
    if (!map[signKey].includes('As')) map[signKey].push('As');
  }

  return map;
}

/* ---------- Mini Chart Visualizations ---------- */

/** South Indian 4x4 grid for Vedic charts */
function VedicMiniChart({ chart }: { chart: ChartItem }) {
  const signPlanets = buildSignPlanetMap(chart);

  return (
    <div
      style={{
        width: 120,
        height: 120,
        border: '1.5px solid var(--border-strong)',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gridTemplateRows: 'repeat(4, 1fr)',
        flexShrink: 0,
        borderRadius: 4,
        overflow: 'hidden',
        background: 'var(--bg-card, var(--card))',
      }}
    >
      {SIGN_CELLS.map((sign, i) => {
        // Center 2x2 cells (indices 5,6,9,10)
        if (i === 5) {
          return (
            <div
              key={i}
              style={{
                gridColumn: '2 / 4',
                gridRow: '2 / 4',
                border: '1px solid var(--border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 8,
                fontWeight: 600,
                color: 'var(--text-muted)',
                background: 'var(--card)',
              }}
            >
              Rasi
            </div>
          );
        }
        if (i === 6 || i === 9 || i === 10) return null;

        const planets = signPlanets[sign] || [];
        const hasAsc = planets.includes('As');
        const displayPlanets = planets.filter((p) => p !== 'As');

        return (
          <div
            key={i}
            style={{
              border: '0.5px solid var(--border)',
              padding: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <span
              style={{
                fontSize: 6,
                color: hasAsc ? 'var(--gold)' : 'var(--text-faint)',
                fontWeight: hasAsc ? 700 : 400,
                lineHeight: 1,
              }}
            >
              {sign}
            </span>
            {displayPlanets.length > 0 && (
              <span
                style={{
                  fontSize: 5.5,
                  color: 'var(--text-secondary)',
                  lineHeight: 1,
                  marginTop: 1,
                  textAlign: 'center',
                  wordBreak: 'break-all',
                }}
              >
                {displayPlanets.join(' ')}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

/** Western circle chart placeholder */
function WesternMiniChart() {
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {/* Outer ring */}
      <div
        style={{
          width: 110,
          height: 110,
          borderRadius: '50%',
          border: '2px solid var(--border-strong)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
        }}
      >
        {/* Inner ring */}
        <div
          style={{
            width: 70,
            height: 70,
            borderRadius: '50%',
            border: '1.5px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* Cross lines */}
          <div
            style={{
              width: 30,
              height: 1,
              background: 'var(--border)',
              position: 'absolute',
            }}
          />
          <div
            style={{
              width: 1,
              height: 30,
              background: 'var(--border)',
              position: 'absolute',
            }}
          />
        </div>
        {/* 12 spoke marks around the outer ring */}
        {Array.from({ length: 12 }).map((_, idx) => (
          <div
            key={idx}
            style={{
              position: 'absolute',
              width: 1,
              height: 10,
              background: 'var(--border)',
              transformOrigin: '50% 55px',
              transform: `rotate(${idx * 30}deg)`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

/** Chinese four-pillars mini visualization */
function ChineseMiniChart() {
  const pillars = ['Year', 'Month', 'Day', 'Hour'];
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        gap: 4,
        alignItems: 'flex-end',
        justifyContent: 'center',
        padding: '12px 4px',
      }}
    >
      {pillars.map((p, i) => (
        <div
          key={p}
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
          }}
        >
          <div
            style={{
              width: '100%',
              height: 40 + i * 10,
              borderRadius: 3,
              border: '1.5px solid var(--border-strong)',
              background: 'var(--card)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span style={{ fontSize: 6, color: 'var(--text-faint)', fontWeight: 600 }}>
              {p.slice(0, 2)}
            </span>
          </div>
          <span style={{ fontSize: 5.5, color: 'var(--text-faint)' }}>{p}</span>
        </div>
      ))}
    </div>
  );
}

/** Generic mini chart for other traditions */
function GenericMiniChart({ tradition }: { tradition: string }) {
  const style = TRADITION_STYLES[tradition.toLowerCase()];
  const color = style?.color || 'var(--text-muted)';
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1.5px solid var(--border)',
        borderRadius: 6,
      }}
    >
      <Star style={{ width: 28, height: 28, color, opacity: 0.5 }} />
    </div>
  );
}

function MiniChart({ chart }: { chart: ChartItem }) {
  const type = chart.chart_type.toLowerCase();
  if (type === 'vedic') return <VedicMiniChart chart={chart} />;
  if (type === 'western') return <WesternMiniChart />;
  if (type === 'chinese') return <ChineseMiniChart />;
  return <GenericMiniChart tradition={chart.chart_type} />;
}

/* ---------- Loading / Empty States ---------- */

function LoadingGrid() {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
        gap: 16,
      }}
    >
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          style={{
            background: 'var(--card)',
            border: '1px solid var(--border)',
            borderRadius: 14,
            padding: 20,
          }}
        >
          <div style={{ display: 'flex', gap: 16 }}>
            {/* Mini chart skeleton */}
            <div
              style={{
                width: 120,
                height: 120,
                borderRadius: 4,
                background: 'var(--border)',
                opacity: 0.4,
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div
                style={{
                  height: 12,
                  width: 60,
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.4,
                }}
              />
              <div
                style={{
                  height: 16,
                  width: '80%',
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.4,
                }}
              />
              <div
                style={{
                  height: 10,
                  width: '50%',
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.3,
                }}
              />
              <div style={{ flex: 1 }} />
              <div
                style={{
                  height: 10,
                  width: '40%',
                  borderRadius: 6,
                  background: 'var(--border)',
                  opacity: 0.25,
                }}
              />
            </div>
          </div>
        </div>
      ))}
      <style>{`@keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.2; } }`}</style>
    </div>
  );
}

function LoadingList() {
  return (
    <div
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 14,
        overflow: 'hidden',
      }}
    >
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          style={{
            padding: '14px 20px',
            borderBottom: i < 5 ? '1px solid var(--border)' : 'none',
            display: 'flex',
            gap: 16,
            alignItems: 'center',
          }}
        >
          <div
            style={{
              height: 12,
              width: 120,
              borderRadius: 6,
              background: 'var(--border)',
              opacity: 0.4,
            }}
          />
          <div
            style={{
              height: 12,
              width: 100,
              borderRadius: 6,
              background: 'var(--border)',
              opacity: 0.3,
            }}
          />
          <div style={{ flex: 1 }} />
          <div
            style={{
              height: 12,
              width: 80,
              borderRadius: 6,
              background: 'var(--border)',
              opacity: 0.25,
            }}
          />
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 14,
        border: '1px solid var(--border)',
        background: 'var(--card)',
        padding: '64px 24px',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 20,
          background: 'var(--gold-bg)',
        }}
      >
        <Star style={{ width: 24, height: 24, color: 'var(--gold)' }} />
      </div>
      <p
        className="font-display"
        style={{
          fontSize: 18,
          color: 'var(--text-primary)',
          marginBottom: 8,
        }}
      >
        No charts yet
      </p>
      <p
        style={{
          fontSize: 13,
          color: 'var(--text-muted)',
          marginBottom: 24,
          maxWidth: 300,
          lineHeight: 1.5,
        }}
      >
        Create your first birth chart to explore planetary positions across six astrological traditions.
      </p>
      <Link href="/chart-calculator">
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
          }}
        >
          <Plus style={{ width: 16, height: 16 }} />
          Calculate Your First Chart
        </button>
      </Link>
    </div>
  );
}

function NoFilterResults({ filter }: { filter: string }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 14,
        border: '1px solid var(--border)',
        background: 'var(--card)',
        padding: '64px 24px',
        textAlign: 'center',
      }}
    >
      <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
        No {filter.toLowerCase()} charts found. Try a different tradition.
      </p>
    </div>
  );
}

/* ---------- Grid View Card ---------- */

function ChartGridCard({
  chart,
  personName,
}: {
  chart: ChartItem;
  personName?: string;
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

/* ---------- List View ---------- */

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

function ChartListView({
  charts,
  personMap,
}: {
  charts: ChartItem[];
  personMap: Record<string, string>;
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

/* ---------- Main Page ---------- */

export default function ChartsPage() {
  const [filter, setFilter] = useState<TraditionFilter>('All');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  // apiClient internally waits for auth before making requests
  const { data: personsResponse, isLoading: personsLoading } = useQuery({
    queryKey: ['persons'],
    queryFn: () => apiClient.get<Person[]>('/api/v1/persons/'),
  });

  const persons = personsResponse?.data || [];
  const personMap = useMemo(() => {
    const map: Record<string, string> = {};
    persons.forEach((p) => {
      map[p.person_id] = p.name;
    });
    return map;
  }, [persons]);

  // Fetch charts for each person (enabled once persons are loaded)
  const personIds = persons.map((p) => p.person_id);

  const { data: chartsResponse, isLoading: chartsLoading } = useQuery({
    queryKey: ['all-charts', personIds],
    queryFn: async () => {
      if (personIds.length === 0) return [];
      const results = await Promise.all(
        personIds.map((pid) =>
          apiClient
            .get<ChartItem[]>(`/api/v1/persons/${pid}/charts`)
            .then((res) => res.data || [])
            .catch(() => [] as ChartItem[])
        )
      );
      return results.flat();
    },
    enabled: personIds.length > 0 && !personsLoading,
  });

  const allCharts = chartsResponse || [];
  const isLoading = personsLoading || (personIds.length > 0 && chartsLoading);

  // Filter charts by tradition
  const filteredCharts = useMemo(() => {
    if (filter === 'All') return allCharts;
    return allCharts.filter(
      (c) => c.chart_type.toLowerCase() === filter.toLowerCase()
    );
  }, [allCharts, filter]);

  return (
    <div>
      {/* Hover styles */}
      <style>{`
        .chart-grid-card:hover {
          border-color: var(--gold) !important;
          box-shadow: 0 0 0 1px var(--gold), 0 8px 24px rgba(200,145,58,0.12) !important;
          transform: translateY(-2px);
        }
        .chart-grid-card:hover .chart-card-name {
          color: var(--gold-bright) !important;
        }
        .chart-list-row:hover {
          background: var(--card-hover) !important;
        }
        .filter-pill {
          transition: all 0.15s ease;
        }
        .filter-pill:hover:not(.filter-pill-active) {
          border-color: var(--gold) !important;
          color: var(--text-primary) !important;
        }
        .view-toggle-btn {
          transition: all 0.15s ease;
        }
      `}</style>

      {/* Header */}
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
        <Link href="/chart-calculator">
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

      {/* Filter bar + View toggle */}
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
                onClick={() => setFilter(t)}
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
            onClick={() => setViewMode('grid')}
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
            onClick={() => setViewMode('list')}
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

      {/* Content */}
      {isLoading ? (
        viewMode === 'grid' ? (
          <LoadingGrid />
        ) : (
          <LoadingList />
        )
      ) : filteredCharts.length === 0 && allCharts.length === 0 ? (
        <EmptyState />
      ) : filteredCharts.length === 0 ? (
        <NoFilterResults filter={filter} />
      ) : viewMode === 'grid' ? (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: 16,
          }}
        >
          {filteredCharts.map((chart) => (
            <ChartGridCard
              key={chart.chart_id}
              chart={chart}
              personName={personMap[chart.person_id]}
            />
          ))}
        </div>
      ) : (
        <ChartListView charts={filteredCharts} personMap={personMap} />
      )}
    </div>
  );
}
