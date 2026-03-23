'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Plus, Star } from 'lucide-react';
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

const TRADITION_FILTERS = ['All', 'Vedic', 'Western', 'Chinese'] as const;
type TraditionFilter = (typeof TRADITION_FILTERS)[number];

const TRADITION_STYLES: Record<string, { label: string; variant: 'default' | 'blue' | 'green' | 'outline' }> = {
  vedic: { label: 'Vedic', variant: 'default' },
  western: { label: 'Western', variant: 'blue' },
  chinese: { label: 'Chinese', variant: 'green' },
  hellenistic: { label: 'Hellenistic', variant: 'outline' },
  mayan: { label: 'Mayan', variant: 'outline' },
  celtic: { label: 'Celtic', variant: 'outline' },
};

/* ---------- Helpers ---------- */

function getChartSummary(chart: ChartItem): string {
  const planets = chart.chart_data?.planets || chart.planet_positions || {};
  const sun = planets['Sun'];
  const moon = planets['Moon'];
  const parts: string[] = [];
  if (sun) parts.push(`Sun ${sun.sign}`);
  if (moon) parts.push(`Moon ${moon.sign}`);
  return parts.length > 0 ? parts.join(', ') : 'Chart calculated';
}

function getChartTypeName(type: string): string {
  // chart_type may include tradition + type, but typically just the tradition
  return type.charAt(0).toUpperCase() + type.slice(1);
}

/* ---------- Components ---------- */

function LoadingGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <Card key={i}>
          <CardContent className="p-5">
            <div className="animate-pulse space-y-3">
              <div className="h-4 w-16 rounded bg-border" />
              <div className="h-5 w-32 rounded bg-border" />
              <div className="h-3 w-24 rounded bg-border" />
              <div className="h-3 w-20 rounded bg-border" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-border bg-card py-16 text-center">
      <div
        className="w-14 h-14 rounded-2xl flex items-center justify-center mb-5"
        style={{ background: 'var(--gold-bg)' }}
      >
        <Star className="h-6 w-6" style={{ color: 'var(--gold)' }} />
      </div>
      <p className="text-sm text-text-muted mb-4">No charts yet. Create your first birth chart to get started.</p>
      <Link href="/chart-calculator">
        <Button variant="outline">Calculate your first chart</Button>
      </Link>
    </div>
  );
}

function ChartCard({ chart, personName }: { chart: ChartItem; personName?: string }) {
  const tradition = TRADITION_STYLES[chart.chart_type] || {
    label: getChartTypeName(chart.chart_type),
    variant: 'outline' as const,
  };

  return (
    <Link href={`/charts/${chart.chart_id}`}>
      <Card className="group cursor-pointer hover:border-[var(--gold)] hover:shadow-sm transition-all">
        <CardContent className="p-5">
          <div className="flex items-start justify-between mb-3">
            <Badge variant={tradition.variant}>{tradition.label}</Badge>
            <span className="text-[11px] text-text-faint">Natal</span>
          </div>

          <p className="text-sm font-semibold text-text-primary mb-1 group-hover:text-gold-bright transition-colors">
            {getChartSummary(chart)}
          </p>

          {personName && (
            <p className="text-xs text-text-secondary mb-2">{personName}</p>
          )}

          <p className="text-[11px] text-text-faint">
            {chart.calculated_at
              ? new Date(chart.calculated_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })
              : ''}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}

/* ---------- Main Page ---------- */

export default function ChartsPage() {
  const [filter, setFilter] = useState<TraditionFilter>('All');

  // Fetch all persons
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

  const {
    data: chartsResponse,
    isLoading: chartsLoading,
  } = useQuery({
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
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-display text-display-md text-text-primary mb-1">My Charts</h3>
          <p className="text-sm text-text-muted">View and manage your birth charts</p>
        </div>
        <Link href="/chart-calculator">
          <Button>
            <Plus className="h-4 w-4" /> Calculate New Chart
          </Button>
        </Link>
      </div>

      {/* Filter pills */}
      <div className="flex gap-2 mb-6">
        {TRADITION_FILTERS.map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filter === t
                ? 'bg-primary text-primary-foreground'
                : 'bg-card border border-border text-text-secondary hover:text-text-primary hover:border-[var(--gold)]'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingGrid />
      ) : filteredCharts.length === 0 && allCharts.length === 0 ? (
        <EmptyState />
      ) : filteredCharts.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-border bg-card py-16 text-center">
          <p className="text-sm text-text-muted">
            No {filter.toLowerCase()} charts found. Try a different filter.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCharts.map((chart) => (
            <ChartCard
              key={chart.chart_id}
              chart={chart}
              personName={personMap[chart.person_id]}
            />
          ))}
        </div>
      )}
    </div>
  );
}
