'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';

import type { DashaPeriod, DashaResponse } from './_components/dasha-types';
import { LABEL, CARD } from './_components/dasha-helpers';
import { DashaInterpretationPanel } from './_components/dasha-interpretation-panel';
import {
  SkeletonBar,
  MahadashaTimeline,
  CurrentPeriodCard,
  AntardashaTimeline,
  UpcomingTransitions,
} from './_components/dasha-components';

export default function DashaPage() {
  const [personId, setPersonId] = useState<string | undefined>(undefined);
  const [selectedPeriod, setSelectedPeriod] = useState<DashaPeriod | null>(null);

  const { data: dashaResponse, isLoading, error } = useQuery({
    queryKey: ['dasha-vimshottari', personId],
    queryFn: () => apiClient.get<DashaResponse>(`/api/v1/dasha/vimshottari/${personId}`),
    enabled: !!personId,
  });

  const dasha = dashaResponse?.data || null;
  const currentMahaPlanet = dasha?.current_dasha?.mahadasha?.planet;
  const currentAntarPlanet = dasha?.current_dasha?.antardasha?.planet;
  const currentMahaFull = dasha?.dasha_sequence?.find((d) => d.planet === currentMahaPlanet && d.antardashas);
  const antardashas = currentMahaFull?.antardashas || [];

  const handlePlanetClick = (period: DashaPeriod) => {
    setSelectedPeriod((prev) =>
      prev?.planet === period.planet && prev?.start_date === period.start_date ? null : period
    );
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: 'var(--text-primary)', marginBottom: 4 }}>Dasha Timeline</h1>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Vimshottari Dasha periods showing the 120-year planetary time cycles.</p>
      </div>

      {/* Profile selector */}
      <div style={{ maxWidth: 320, marginBottom: 24 }}>
        <label style={LABEL}>Profile</label>
        <ProfileSelector value={personId} onChange={setPersonId} />
      </div>

      {/* Loading */}
      {isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 0', gap: 16 }}>
          <div style={{ width: 40, height: 40, borderRadius: '50%', border: '3px solid var(--border)', borderTopColor: 'var(--gold)', animation: 'spin 0.8s linear infinite' }} />
          <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>Calculating dasha periods...</p>
          <p style={{ fontSize: 11, color: 'var(--text-faint)' }}>Analysing 120-year planetary cycle from birth nakshatra</p>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {/* Error */}
      {error && !isLoading && (
        <div style={{ ...CARD, padding: 32, textAlign: 'center' as const }}>
          <p style={{ fontSize: 14, color: 'var(--red)', marginBottom: 8 }}>Failed to load dasha data</p>
          <p style={{ fontSize: 12, color: 'var(--text-faint)' }}>{(error as Error).message}</p>
        </div>
      )}

      {/* No profile */}
      {!personId && !isLoading && (
        <div style={{ ...CARD, padding: 48, textAlign: 'center' as const }}>
          <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>Select a profile above to view dasha periods.</p>
        </div>
      )}

      {/* Content */}
      {dasha && !isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, animation: 'fadeIn 0.25s ease-out' }}>
          <MahadashaTimeline periods={dasha.life_timeline || dasha.dasha_sequence || []} currentPlanet={currentMahaPlanet} onPlanetClick={handlePlanetClick} />

          {selectedPeriod && (
            <DashaInterpretationPanel
              planet={selectedPeriod.planet}
              startDate={selectedPeriod.start_date}
              endDate={selectedPeriod.end_date}
              onClose={() => setSelectedPeriod(null)}
            />
          )}

          {dasha.current_dasha && <CurrentPeriodCard current={dasha.current_dasha} birthNakshatra={dasha.birth_nakshatra} />}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
            <UpcomingTransitions changes={dasha.detailed_periods?.upcoming_changes} antardashas={antardashas} />
          </div>
          {antardashas.length > 0 && <AntardashaTimeline periods={antardashas} currentAntar={currentAntarPlanet} onPlanetClick={handlePlanetClick} />}
          <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }`}</style>
        </div>
      )}
    </div>
  );
}
