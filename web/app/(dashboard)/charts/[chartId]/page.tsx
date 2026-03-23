'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Sun, Moon, Star, RotateCcw } from 'lucide-react';
import Link from 'next/link';

/* ---------- Types ---------- */

interface PlanetData {
  longitude: number;
  sign: string;
  sign_degree: number;
  house: number;
  nakshatra?: string;
  nakshatra_pada?: number;
  is_retrograde: boolean;
  dignity?: string;
}

interface HouseData {
  sign: string;
  degree: number;
}

interface AspectData {
  planet1: string;
  planet2: string;
  aspect: string;
  orb: number;
}

interface ChartData {
  planets: Record<string, PlanetData>;
  houses: Record<string, HouseData>;
  ascendant: { sign: string; degree: number };
  panchang?: { tithi?: string; nakshatra?: string; yoga?: string; karana?: string };
  dasha?: { current?: { maha?: string; antar?: string } };
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

/* ---------- Constants ---------- */

const TABS = ['Overview', 'Planets', 'Houses', 'Aspects'] as const;
type Tab = (typeof TABS)[number];

const PLANET_ORDER = [
  'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu',
];

const TRADITION_STYLES: Record<string, { label: string; variant: 'default' | 'blue' | 'green' | 'outline' }> = {
  vedic: { label: 'Vedic', variant: 'default' },
  western: { label: 'Western', variant: 'blue' },
  chinese: { label: 'Chinese', variant: 'green' },
  hellenistic: { label: 'Hellenistic', variant: 'outline' },
  mayan: { label: 'Mayan', variant: 'outline' },
  celtic: { label: 'Celtic', variant: 'outline' },
};

/* ---------- Helpers ---------- */

function formatDegree(deg: number): string {
  const d = Math.floor(deg);
  const m = Math.round((deg - d) * 60);
  return `${d}\u00B0${m.toString().padStart(2, '0')}'`;
}

function dignityColor(dignity?: string): string {
  if (!dignity) return '';
  const d = dignity.toLowerCase();
  if (d === 'exalted' || d === 'own' || d === 'moolatrikona') return 'text-green';
  if (d === 'debilitated' || d === 'enemy') return 'text-red';
  return 'text-text-secondary';
}

function dignityLabel(dignity?: string): string {
  if (!dignity) return '-';
  return dignity.charAt(0).toUpperCase() + dignity.slice(1);
}

/* ---------- Sub-components ---------- */

function LoadingState() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <div
          className="w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center"
          style={{ background: 'var(--gold-bg)' }}
        >
          <Star className="h-5 w-5 animate-pulse" style={{ color: 'var(--gold)' }} />
        </div>
        <p className="text-sm text-text-muted">Loading chart data...</p>
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <div
          className="w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center"
          style={{ background: 'var(--red-bg)' }}
        >
          <span className="text-lg" style={{ color: 'var(--red)' }}>!</span>
        </div>
        <p className="text-sm text-text-muted mb-2">Failed to load chart</p>
        <p className="text-xs text-text-faint">{message}</p>
      </div>
    </div>
  );
}

function PlacementCard({
  label,
  icon: Icon,
  sign,
  degree,
  house,
  nakshatra,
}: {
  label: string;
  icon: typeof Sun;
  sign: string;
  degree: number;
  house: number;
  nakshatra?: string;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-center gap-3 mb-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: 'var(--gold-bg)' }}
          >
            <Icon className="h-4 w-4" style={{ color: 'var(--gold)' }} />
          </div>
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wide">{label}</p>
            <p className="text-sm font-semibold text-text-primary">{sign}</p>
          </div>
        </div>
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-text-muted">Degree</span>
            <span className="text-text-secondary">{formatDegree(degree)}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-text-muted">House</span>
            <span className="text-text-secondary">{house}</span>
          </div>
          {nakshatra && (
            <div className="flex justify-between text-xs">
              <span className="text-text-muted">Nakshatra</span>
              <span className="text-text-secondary">{nakshatra}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function OverviewTab({ chart }: { chart: Chart }) {
  const planets = chart.chart_data?.planets || chart.planet_positions || {};
  const ascendant = chart.chart_data?.ascendant;
  const sun = planets['Sun'];
  const moon = planets['Moon'];
  const isVedic = chart.chart_type === 'vedic';
  const panchang = chart.chart_data?.panchang;
  const dasha = chart.chart_data?.dasha?.current;

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Card>
        <CardContent className="p-5">
          <p className="text-sm text-text-body-reading leading-relaxed">
            {sun && <>Sun in <span className="font-semibold text-text-primary">{sun.sign}</span></>}
            {moon && <>, Moon in <span className="font-semibold text-text-primary">{moon.sign}</span></>}
            {ascendant && <>, Ascendant <span className="font-semibold text-text-primary">{ascendant.sign}</span></>}
          </p>
        </CardContent>
      </Card>

      {/* Key Placements */}
      <div>
        <h4 className="text-xs uppercase tracking-wide text-text-muted mb-3 px-1">Key Placements</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sun && (
            <PlacementCard
              label="Sun"
              icon={Sun}
              sign={sun.sign}
              degree={sun.sign_degree}
              house={sun.house}
              nakshatra={isVedic ? sun.nakshatra : undefined}
            />
          )}
          {moon && (
            <PlacementCard
              label="Moon"
              icon={Moon}
              sign={moon.sign}
              degree={moon.sign_degree}
              house={moon.house}
              nakshatra={isVedic ? moon.nakshatra : undefined}
            />
          )}
          {ascendant && (
            <PlacementCard
              label="Ascendant"
              icon={Star}
              sign={ascendant.sign}
              degree={ascendant.degree}
              house={1}
              nakshatra={undefined}
            />
          )}
        </div>
      </div>

      {/* Panchang (Vedic only) */}
      {isVedic && panchang && (
        <div>
          <h4 className="text-xs uppercase tracking-wide text-text-muted mb-3 px-1">Panchang</h4>
          <Card>
            <CardContent className="p-5">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {panchang.tithi && (
                  <div>
                    <p className="text-xs text-text-muted mb-0.5">Tithi</p>
                    <p className="text-sm text-text-primary">{panchang.tithi}</p>
                  </div>
                )}
                {panchang.nakshatra && (
                  <div>
                    <p className="text-xs text-text-muted mb-0.5">Nakshatra</p>
                    <p className="text-sm text-text-primary">{panchang.nakshatra}</p>
                  </div>
                )}
                {panchang.yoga && (
                  <div>
                    <p className="text-xs text-text-muted mb-0.5">Yoga</p>
                    <p className="text-sm text-text-primary">{panchang.yoga}</p>
                  </div>
                )}
                {panchang.karana && (
                  <div>
                    <p className="text-xs text-text-muted mb-0.5">Karana</p>
                    <p className="text-sm text-text-primary">{panchang.karana}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Current Dasha (Vedic only) */}
      {isVedic && dasha && (
        <div>
          <h4 className="text-xs uppercase tracking-wide text-text-muted mb-3 px-1">Current Dasha</h4>
          <Card>
            <CardContent className="p-5">
              <div className="flex gap-6">
                {dasha.maha && (
                  <div>
                    <p className="text-xs text-text-muted mb-0.5">Maha Dasha</p>
                    <p className="text-sm font-semibold text-text-primary">{dasha.maha}</p>
                  </div>
                )}
                {dasha.antar && (
                  <div>
                    <p className="text-xs text-text-muted mb-0.5">Antar Dasha</p>
                    <p className="text-sm font-semibold text-text-primary">{dasha.antar}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Quick Stats */}
      <div>
        <h4 className="text-xs uppercase tracking-wide text-text-muted mb-3 px-1">Quick Stats</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-5">
              <p className="text-xs text-text-muted mb-0.5">Dominant Element</p>
              <p className="text-sm text-text-secondary italic">Coming soon</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-5">
              <p className="text-xs text-text-muted mb-0.5">Chart Pattern</p>
              <p className="text-sm text-text-secondary italic">Coming soon</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function PlanetsTab({ chart }: { chart: Chart }) {
  const planets = chart.chart_data?.planets || chart.planet_positions || {};
  const isVedic = chart.chart_type === 'vedic';

  // Collect ordered planets, falling back to all keys if standard ones are missing
  const orderedPlanets = PLANET_ORDER.filter((p) => planets[p]);
  const extraPlanets = Object.keys(planets).filter((p) => !PLANET_ORDER.includes(p));
  const allPlanets = [...orderedPlanets, ...extraPlanets];

  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-divider text-left">
                <th className="px-5 py-3 font-medium text-text-muted">Planet</th>
                <th className="px-5 py-3 font-medium text-text-muted">Sign</th>
                <th className="px-5 py-3 font-medium text-text-muted">Degree</th>
                <th className="px-5 py-3 font-medium text-text-muted">House</th>
                {isVedic && (
                  <>
                    <th className="px-5 py-3 font-medium text-text-muted">Nakshatra</th>
                    <th className="px-5 py-3 font-medium text-text-muted">Pada</th>
                  </>
                )}
                <th className="px-5 py-3 font-medium text-text-muted">Dignity</th>
                <th className="px-5 py-3 font-medium text-text-muted text-center">Retro</th>
              </tr>
            </thead>
            <tbody>
              {allPlanets.map((name) => {
                const p = planets[name];
                if (!p) return null;
                return (
                  <tr
                    key={name}
                    className="border-b border-divider last:border-0 hover:bg-card-hover transition-colors"
                  >
                    <td className="px-5 py-3 font-medium text-text-primary">{name}</td>
                    <td className="px-5 py-3 text-text-secondary">{p.sign}</td>
                    <td className="px-5 py-3 text-text-secondary font-mono text-xs">
                      {formatDegree(p.sign_degree)}
                    </td>
                    <td className="px-5 py-3 text-text-secondary">{p.house}</td>
                    {isVedic && (
                      <>
                        <td className="px-5 py-3 text-text-secondary">{p.nakshatra || '-'}</td>
                        <td className="px-5 py-3 text-text-secondary">{p.nakshatra_pada || '-'}</td>
                      </>
                    )}
                    <td className={`px-5 py-3 font-medium ${dignityColor(p.dignity)}`}>
                      {dignityLabel(p.dignity)}
                    </td>
                    <td className="px-5 py-3 text-center">
                      {p.is_retrograde ? (
                        <span className="inline-flex items-center gap-1 text-red font-semibold text-xs">
                          <RotateCcw className="h-3 w-3" /> R
                        </span>
                      ) : (
                        <span className="text-text-faint">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
              {allPlanets.length === 0 && (
                <tr>
                  <td colSpan={isVedic ? 8 : 6} className="px-5 py-12 text-center text-text-muted text-sm">
                    No planet data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function HousesTab() {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-16 text-center">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
          style={{ background: 'var(--blue-bg)' }}
        >
          <Star className="h-5 w-5" style={{ color: 'var(--blue)' }} />
        </div>
        <p className="text-sm text-text-muted">Houses view coming soon</p>
      </CardContent>
    </Card>
  );
}

function AspectsTab() {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-16 text-center">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
          style={{ background: 'var(--green-bg)' }}
        >
          <Star className="h-5 w-5" style={{ color: 'var(--green)' }} />
        </div>
        <p className="text-sm text-text-muted">Aspects grid coming soon</p>
      </CardContent>
    </Card>
  );
}

/* ---------- Main Page ---------- */

export default function ChartDetailPage() {
  const params = useParams<{ chartId: string }>();
  const router = useRouter();
  const chartId = params.chartId;
  const [activeTab, setActiveTab] = useState<Tab>('Overview');

  const {
    data: response,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['chart', chartId],
    queryFn: () => apiClient.get<Chart>(`/api/v1/charts/${chartId}`),
    enabled: !!chartId,
  });

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState message={(error as Error).message} />;

  const chart = response?.data;
  if (!chart) return <ErrorState message="Chart not found" />;

  const tradition = TRADITION_STYLES[chart.chart_type] || { label: chart.chart_type, variant: 'outline' as const };

  return (
    <div>
      {/* Top bar */}
      <div className="mb-6">
        <Link
          href="/charts"
          className="inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Charts
        </Link>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="font-display text-display-md text-text-primary">
              {chart.chart_type.charAt(0).toUpperCase() + chart.chart_type.slice(1)} Chart
            </h3>
            <Badge variant={tradition.variant}>{tradition.label}</Badge>
          </div>
          <div className="text-xs text-text-muted">
            {chart.calculated_at
              ? new Date(chart.calculated_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })
              : ''}
          </div>
        </div>
      </div>

      {/* Chart visualization placeholder */}
      <Card className="mb-6">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
            style={{ background: 'var(--gold-bg)' }}
          >
            <Star className="h-6 w-6" style={{ color: 'var(--gold)' }} />
          </div>
          <p className="text-sm font-medium text-text-primary mb-1">
            {tradition.label} Chart Visualization
          </p>
          <p className="text-xs text-text-muted">
            Interactive chart rendering coming soon
          </p>
        </CardContent>
      </Card>

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b border-border">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium transition-colors relative ${
              activeTab === tab
                ? 'text-text-primary'
                : 'text-text-muted hover:text-text-secondary'
            }`}
          >
            {tab}
            {activeTab === tab && (
              <span
                className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full"
                style={{ background: 'var(--gold)' }}
              />
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'Overview' && <OverviewTab chart={chart} />}
      {activeTab === 'Planets' && <PlanetsTab chart={chart} />}
      {activeTab === 'Houses' && <HousesTab />}
      {activeTab === 'Aspects' && <AspectsTab />}
    </div>
  );
}
