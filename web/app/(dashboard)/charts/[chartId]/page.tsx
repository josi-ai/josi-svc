'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Star } from 'lucide-react';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';
import { SouthIndianChart, NorthIndianChart, WesternWheelChart } from '@/components/charts/chart-visualizations';
import type { ChartDetail, ChartDetailPerson } from '@/types';
import { TABS, type Tab, getPlanets, getDefaultFormat } from './_components/chart-detail-helpers';
import { ChartDetailHeader } from './_components/chart-detail-header';
import { QuickInfoPanel } from './_components/quick-info-panel';
import { OverviewTab } from './_components/overview-tab';
import { PlanetsTab } from './_components/planets-tab';
import { HousesTab } from './_components/houses-tab';
import { AspectsTab } from './_components/aspects-tab';

const centerBox: React.CSSProperties = { display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' };
const dot: (bg: string) => React.CSSProperties = (bg) => ({
  width: 48, height: 48, borderRadius: '50%', margin: '0 auto 16px',
  background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
});

function LoadingState() {
  return (
    <div style={centerBox}>
      <div style={{ textAlign: 'center' }}>
        <div style={dot('var(--gold-bg)')}>
          <Star style={{ width: 20, height: 20, color: 'var(--gold)', animation: 'pulse 2s infinite' }} />
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading chart data...</p>
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div style={centerBox}>
      <div style={{ textAlign: 'center' }}>
        <div style={dot('var(--red-bg)')}>
          <span style={{ fontSize: 18, color: 'var(--red)', fontWeight: 700 }}>!</span>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Failed to load chart</p>
        <p style={{ fontSize: 11, color: 'var(--text-faint)' }}>{message}</p>
      </div>
    </div>
  );
}

export default function ChartDetailPage() {
  const params = useParams<{ chartId: string }>();
  const chartId = params.chartId;
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>('Overview');
  const [chartFormat, setChartFormat] = useState<string>('South Indian');
  const [tradition, setTradition] = useState<string>('Vedic');
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
    queryFn: () => apiClient.get<ChartDetail>(`/api/v1/charts/${chartId}`),
    enabled: !!chartId,
  });

  const chart = chartResponse?.data;

  // Fetch person for name/date
  const {
    data: personResponse,
  } = useQuery({
    queryKey: ['person', chart?.person_id],
    queryFn: () => apiClient.get<ChartDetailPerson>(`/api/v1/persons/${chart!.person_id}`),
    enabled: !!chart?.person_id,
  });

  const person = personResponse?.data;

  if (chartLoading) return <LoadingState />;
  if (chartError) return <ErrorState message={(chartErr as Error).message} />;
  if (!chart) return <ErrorState message="Chart not found" />;

  const planets = getPlanets(chart);




  const handleTraditionChange = (newTradition: string) => {
    setTradition(newTradition);
    setChartFormat(getDefaultFormat(newTradition));
  };

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
      <ChartDetailHeader
        chart={chart}
        person={person}
        tradition={tradition}
        onTraditionChange={handleTraditionChange}
        chartFormat={chartFormat}
        onChartFormatChange={setChartFormat}
        onDeleteClick={() => setShowDeleteConfirm(true)}
        isDeleting={deleteMutation.isPending}
      />

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
