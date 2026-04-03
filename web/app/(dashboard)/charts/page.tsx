'use client';

import { useState, useMemo, Suspense } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import {
  Plus,
  Star,
  Globe,
  LayoutGrid,
  List,
  ArrowUpDown,
  ChevronDown,
  ChevronUp,
  Eye,
  Trash2,
  X,
  Users,
} from 'lucide-react';
import Link from 'next/link';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

/* ---------- Types ---------- */

interface Person {
  person_id: string;
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  place_of_birth?: string;
  is_default?: boolean;
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

/** Chinese four-pillars mini visualization with heavenly stem characters */
function ChineseMiniChart() {
  const pillars = [
    { label: 'Year', stem: '\u7532' },
    { label: 'Month', stem: '\u4E59' },
    { label: 'Day', stem: '\u4E19' },
    { label: 'Hour', stem: '\u4E01' },
  ];
  return (
    <div
      style={{
        width: 120,
        height: 120,
        flexShrink: 0,
        display: 'flex',
        gap: 4,
        alignItems: 'center',
        justifyContent: 'center',
        padding: '8px 6px',
      }}
    >
      {pillars.map((p) => (
        <div
          key={p.label}
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
              height: 70,
              borderRadius: 3,
              border: '1.5px solid var(--border-strong)',
              background: 'var(--card)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 2,
            }}
          >
            <span style={{ fontSize: 14, color: 'var(--text-secondary)', fontWeight: 600, lineHeight: 1 }}>
              {p.stem}
            </span>
            <span style={{ fontSize: 5.5, color: 'var(--text-faint)', fontWeight: 500 }}>
              {p.label.slice(0, 2)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

/** Hellenistic circle chart with triangular inner pattern */
function HellenisticMiniChart() {
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
          {/* Diagonal cross lines */}
          <div
            style={{
              width: 30,
              height: 1,
              background: 'var(--border)',
              position: 'absolute',
              transform: 'rotate(45deg)',
            }}
          />
          <div
            style={{
              width: 30,
              height: 1,
              background: 'var(--border)',
              position: 'absolute',
              transform: 'rotate(-45deg)',
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

/** Generic mini chart for mayan, celtic, and other traditions */
function GenericMiniChart({ tradition }: { tradition: string }) {
  const tradStyle = TRADITION_STYLES[tradition.toLowerCase()];
  const color = tradStyle?.color || 'var(--text-muted)';
  const t = tradition.toLowerCase();
  const Icon = t === 'mayan' || t === 'celtic' ? Globe : Star;
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
      <Icon style={{ width: 28, height: 28, color, opacity: 0.5 }} />
    </div>
  );
}

function MiniChart({ chart }: { chart: ChartItem }) {
  const type = chart.chart_type.toLowerCase();
  if (type === 'vedic') return <VedicMiniChart chart={chart} />;
  if (type === 'western') return <WesternMiniChart />;
  if (type === 'chinese') return <ChineseMiniChart />;
  if (type === 'hellenistic') return <HellenisticMiniChart />;
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
            onMouseEnter={(e) => { e.currentTarget.style.color = '#E5484D'; e.currentTarget.style.background = 'rgba(229,72,77,0.08)'; }}
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
                          onMouseEnter={(e) => { e.currentTarget.style.color = '#E5484D'; }}
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

/* ---------- Main Page ---------- */

function ChartsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const personIdParam = searchParams.get('person_id');
  const queryClient = useQueryClient();

  const [filter, setFilter] = useState<TraditionFilter>('All');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showAll, setShowAll] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const deleteMutation = useMutation({
    mutationFn: (chartId: string) => apiClient.delete(`/api/v1/charts/${chartId}`),
    onSuccess: () => {
      setDeleteTarget(null);
      queryClient.invalidateQueries({ queryKey: ['charts'] });
    },
  });

  const handleDeleteChart = (chartId: string) => {
    setDeleteTarget(chartId);
  };

  const confirmDelete = () => {
    if (deleteTarget) deleteMutation.mutate(deleteTarget);
  };

  // Fetch user's default profile
  const { data: defaultProfileResponse } = useQuery({
    queryKey: ['default-profile'],
    queryFn: () => apiClient.get<Person>('/api/v1/persons/me'),
  });
  const defaultProfile = defaultProfileResponse?.data || null;

  // Determine the active person_id filter
  // Priority: query param > default profile (unless "show all" is active)
  const activePersonId = showAll
    ? null
    : personIdParam || defaultProfile?.person_id || null;

  // Fetch all persons (needed for personMap in both modes)
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

  // The name of the person being filtered
  const activePersonName = activePersonId ? personMap[activePersonId] : null;

  // Fetch charts: either for one person or for all persons
  const personIds = persons.map((p) => p.person_id);

  const { data: chartsResponse, isLoading: chartsLoading } = useQuery({
    queryKey: ['charts', activePersonId, personIds],
    queryFn: async () => {
      if (activePersonId) {
        // Fetch charts for a single person
        const res = await apiClient
          .get<ChartItem[]>(`/api/v1/persons/${activePersonId}/charts`)
          .catch(() => ({ data: [] as ChartItem[], success: false, message: '' }));
        return res.data || [];
      } else {
        // Fetch charts for all persons
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
      }
    },
    enabled: activePersonId
      ? true
      : personIds.length > 0 && !personsLoading,
  });

  const allCharts = chartsResponse || [];
  const isLoading = personsLoading || (activePersonId ? chartsLoading : (personIds.length > 0 && chartsLoading));

  // Filter charts by tradition
  const filteredCharts = useMemo(() => {
    if (filter === 'All') return allCharts;
    return allCharts.filter(
      (c) => c.chart_type.toLowerCase() === filter.toLowerCase()
    );
  }, [allCharts, filter]);

  const handleShowAll = () => {
    setShowAll(true);
    // Clear person_id from URL if present
    if (personIdParam) {
      router.push('/charts');
    }
  };

  const handleClearFilter = () => {
    setShowAll(false);
    // Reset to default profile by clearing the query param
    if (personIdParam) {
      router.push('/charts');
    }
  };

  // Whether we are in a filtered-by-person mode
  const isFilteredByPerson = activePersonId !== null;

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

      {/* Person filter banner */}
      {isFilteredByPerson && activePersonName && (
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
              onClick={handleShowAll}
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
                onClick={handleClearFilter}
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
      )}

      {/* "All profiles" mode banner — show option to go back to default */}
      {showAll && defaultProfile && (
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
            onClick={() => setShowAll(false)}
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
      )}

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
              onDelete={handleDeleteChart}
            />
          ))}
        </div>
      ) : (
        <ChartListView charts={filteredCharts} personMap={personMap} onDelete={handleDeleteChart} />
      )}

      {/* Delete confirmation modal */}
      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
        title="Delete this chart?"
        description="This chart and its interpretations will be removed. You can always recalculate it later."
        confirmLabel="Delete Chart"
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

export default function ChartsPage() {
  return (
    <Suspense fallback={<LoadingGrid />}>
      <ChartsPageContent />
    </Suspense>
  );
}
