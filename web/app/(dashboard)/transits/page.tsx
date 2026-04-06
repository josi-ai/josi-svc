'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { Globe } from 'lucide-react';

import type { TransitData, ForecastData } from './_components/transit-types';
import { SectionHeading } from './_components/section-heading';
import { TransitSummaryCard } from './_components/transit-summary-card';
import { PlanetaryPositionsTable } from './_components/positions-table';
import { TransitAspectsSection } from './_components/transit-aspects';
import { TransitCalendar } from './_components/transit-calendar';
import { TransitTimeline } from './_components/transit-forecast';
import { LoadingSkeleton, EmptyState, ErrorState } from './_components/transit-states';

export default function TransitsPage() {
  const [personId, setPersonId] = useState<string>('');

  const { data: response, isLoading, error } = useQuery({
    queryKey: ['transits', personId],
    queryFn: () => apiClient.get<TransitData>(`/api/v1/transits/current/${personId}`),
    enabled: !!personId,
  });

  // Forecast query (90 days for calendar + timeline)
  const { data: forecastResponse, isError: forecastError } = useQuery({
    queryKey: ['transit-forecast', personId, 90],
    queryFn: () => apiClient.get<ForecastData>(`/api/v1/transits/forecast/${personId}?days=90`),
    enabled: !!personId,
    retry: false,
  });

  const forecastEvents = forecastResponse?.data?.events ?? null;
  const forecastUnavailable = forecastError || (!!personId && forecastEvents === null && !forecastResponse);

  const data = response?.data;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 4px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28, flexWrap: 'wrap', gap: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 36, height: 36, borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'var(--gold-bg)',
            }}
          >
            <Globe style={{ width: 18, height: 18, color: 'var(--gold)' }} />
          </div>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              Current Transits
            </h1>
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Planetary positions affecting your chart
            </p>
          </div>
        </div>
        <div style={{ minWidth: 200 }}>
          <ProfileSelector value={personId} onChange={setPersonId} />
        </div>
      </div>

      {/* No profile */}
      {!personId && <EmptyState />}

      {/* Loading */}
      {isLoading && <LoadingSkeleton />}

      {/* Error */}
      {error && !isLoading && <ErrorState message={(error as Error).message} />}

      {/* Results */}
      {data && !isLoading && (
        <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
          <TransitSummaryCard transits={data.major_transits} />

          <SectionHeading>Current Planetary Positions</SectionHeading>
          <PlanetaryPositionsTable positions={data.current_planetary_positions} />

          <SectionHeading>Active Transit Aspects</SectionHeading>
          <TransitAspectsSection transits={data.major_transits} />

          <SectionHeading>Transit Calendar</SectionHeading>
          <TransitCalendar events={forecastEvents} fallback={!!forecastUnavailable} />

          <SectionHeading>Forecast Timeline</SectionHeading>
          <TransitTimeline events={forecastEvents} fallback={!!forecastUnavailable} />
        </div>
      )}
    </div>
  );
}
