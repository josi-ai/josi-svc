'use client';

import { useState, useMemo, Suspense } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import type { Person } from '@/types';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

import type { ChartItem, TraditionFilter, ViewMode } from './_components/chart-types';
import { LoadingGrid, LoadingList, EmptyState, NoFilterResults } from './_components/chart-empty-states';
import { ChartsHeader, PersonFilterBanner, AllProfilesBanner, FilterBar } from './_components/chart-filters';
import { ChartGridCard } from './_components/chart-grid-card';
import { ChartListView } from './_components/chart-list-view';

/* ---------- Hover Styles ---------- */

const HOVER_STYLES = `
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
`;

/* ---------- Main Page Content ---------- */

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
    if (personIdParam) router.push('/charts');
  };

  const handleClearFilter = () => {
    setShowAll(false);
    if (personIdParam) router.push('/charts');
  };

  const isFilteredByPerson = activePersonId !== null;

  return (
    <div>
      <style>{HOVER_STYLES}</style>

      <ChartsHeader />

      {/* Person filter banner */}
      {isFilteredByPerson && activePersonName && (
        <PersonFilterBanner
          activePersonName={activePersonName}
          personIdParam={personIdParam}
          onShowAll={handleShowAll}
          onClearFilter={handleClearFilter}
        />
      )}

      {/* "All profiles" mode banner */}
      {showAll && defaultProfile && (
        <AllProfilesBanner onShowMyProfile={() => setShowAll(false)} />
      )}

      <FilterBar
        filter={filter}
        onFilterChange={setFilter}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />

      {/* Content */}
      {isLoading ? (
        viewMode === 'grid' ? <LoadingGrid /> : <LoadingList />
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
