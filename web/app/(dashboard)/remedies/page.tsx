'use client';

import { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { ProgressSummary } from '@/components/remedies/progress-summary';
import { DoshaSection } from '@/components/remedies/dosha-section';
import { TierSection } from '@/components/remedies/tier-section';
import { SkeletonRemedyCard, TIER_CONFIG, costTierKey, type RemedyCatalog, type Recommendation } from '@/components/remedies/remedy-card';
import { Sparkles, Pill } from 'lucide-react';

/* ==========================================================================
   Types
   ========================================================================== */

interface RecommendResponse {
  recommendations: Recommendation[];
  total_recommendations: number;
  chart_id: string;
}

interface ProgressRecord {
  remedy_progress_id: string;
  person_id: string;
  remedy_type: string;
  remedy_name: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
}

interface ChartItem {
  chart_id: string;
  person_id: string;
  chart_type: string;
}

/* ==========================================================================
   Page
   ========================================================================== */

export default function RemediesPage() {
  const [personId, setPersonId] = useState('');
  const [activeTier, setActiveTier] = useState<string | null>(null);
  const [actioningKey, setActioningKey] = useState<string | null>(null);
  const queryClient = useQueryClient();

  /* ------ Fetch person's charts to get a chart_id for recommendations ------ */
  const { data: chartsResponse } = useQuery({
    queryKey: ['person-charts', personId],
    queryFn: () => apiClient.get<ChartItem[]>(`/api/v1/charts/?person_id=${personId}`),
    enabled: !!personId,
  });
  const chartId = chartsResponse?.data?.[0]?.chart_id || null;

  /* ------ Fetch AI recommendations (if we have a chart) ------ */
  const { data: recResponse, isLoading: isLoadingRecs } = useQuery({
    queryKey: ['remedy-recommendations', chartId],
    queryFn: () => apiClient.post<RecommendResponse>('/api/v1/remedies/recommend', { chart_id: chartId }),
    enabled: !!chartId,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  });

  /* ------ Fetch remedy catalog as fallback ------ */
  const { data: catalogResponse, isLoading: isLoadingCatalog } = useQuery({
    queryKey: ['remedy-catalog'],
    queryFn: () => apiClient.get<{ remedies: RemedyCatalog[]; pagination: unknown }>('/api/v1/remedies/?limit=100'),
    enabled: !!personId && !chartId,
    staleTime: 10 * 60 * 1000,
  });

  /* ------ Fetch progress for this person ------ */
  const { data: progressResponse } = useQuery({
    queryKey: ['remedy-progress', personId],
    queryFn: () => apiClient.get<{ progress: ProgressRecord[]; total: number }>(`/api/v1/remedies/progress/${personId}`),
    enabled: !!personId,
  });

  /* ------ Track action mutation ------ */
  const trackMutation = useMutation({
    mutationFn: (body: { person_id: string; remedy_type: string; remedy_name: string; status: string }) =>
      apiClient.post('/api/v1/remedies/track', body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['remedy-progress', personId] });
      setActioningKey(null);
    },
    onError: () => setActioningKey(null),
  });

  /* ------ Derived data ------ */

  const progressMap = useMemo(() => {
    const map = new Map<string, string>();
    for (const r of progressResponse?.data?.progress || []) {
      map.set(`${r.remedy_type}::${r.remedy_name}`, r.status);
    }
    return map;
  }, [progressResponse]);

  const progressCounts = useMemo(() => {
    let total = 0, started = 0, completed = 0;
    progressMap.forEach((status) => {
      total++;
      if (status === 'in_progress') started++;
      if (status === 'completed') completed++;
    });
    return { total, started, completed };
  }, [progressMap]);

  const { tieredRemedies, doshas } = useMemo(() => {
    const recommendations = recResponse?.data?.recommendations || [];
    const catalogRemedies = catalogResponse?.data?.remedies || [];

    // Collect doshas
    const doshaSet = new Map<string, string>();
    for (const rec of recommendations) {
      if (rec.remedy?.dosha_type_name) {
        doshaSet.set(rec.remedy.dosha_type_name, rec.issue_description || '');
      }
    }
    const doshas = Array.from(doshaSet.entries()).map(([name, description]) => ({ name, description }));

    // Build unified list
    type Entry = { remedy: RemedyCatalog; recommendation?: Recommendation };
    const entries: Entry[] = recommendations.length > 0
      ? recommendations.filter((r) => r.remedy).map((r) => ({ remedy: r.remedy, recommendation: r }))
      : catalogRemedies.map((r) => ({ remedy: r }));

    // Group by tier
    const tiers: Record<string, Entry[]> = { free: [], low: [], medium: [], premium: [] };
    for (const e of entries) {
      tiers[costTierKey(e.remedy.cost_level)].push(e);
    }
    for (const tk of Object.keys(tiers)) {
      tiers[tk].sort((a, b) =>
        (b.recommendation?.relevance_score ?? b.remedy.effectiveness_rating) -
        (a.recommendation?.relevance_score ?? a.remedy.effectiveness_rating),
      );
    }
    return { tieredRemedies: tiers, doshas };
  }, [recResponse, catalogResponse]);

  const isLoading = isLoadingRecs || (isLoadingCatalog && !chartId);
  const hasRemedies = Object.values(tieredRemedies).some((arr) => arr.length > 0);

  const handleAction = useCallback(
    (remedyName: string, remedyType: string, status: string) => {
      if (!personId) return;
      setActioningKey(`${remedyType}::${remedyName}`);
      trackMutation.mutate({ person_id: personId, remedy_type: remedyType.toLowerCase(), remedy_name: remedyName, status });
    },
    [personId, trackMutation],
  );

  const tierKeys = ['free', 'low', 'medium', 'premium'] as const;
  const visibleTierKeys = activeTier ? [activeTier] : [...tierKeys];

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 16px' }}>
      <style>{`@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.4 } }`}</style>

      {/* Header */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 16 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
          Remedies &amp; Pariharams
        </h1>
        <div style={{ width: 220 }}>
          <ProfileSelector value={personId} onChange={setPersonId} />
        </div>
      </div>

      {/* Empty state */}
      {!personId && (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <Pill size={48} style={{ color: 'var(--border)', marginBottom: 16 }} />
          <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
            Select a profile to see remedies
          </h2>
          <p style={{ fontSize: 14 }}>Choose a profile above to receive personalized remedy recommendations based on their chart.</p>
        </div>
      )}

      {/* Loading */}
      {personId && isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {Array.from({ length: 6 }).map((_, i) => <SkeletonRemedyCard key={i} />)}
        </div>
      )}

      {/* Content */}
      {personId && !isLoading && (
        <>
          {progressCounts.total > 0 && (
            <ProgressSummary total={progressCounts.total} started={progressCounts.started} completed={progressCounts.completed} />
          )}

          <DoshaSection doshas={doshas} />

          {/* Tier filter tabs */}
          {hasRemedies && (
            <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
              <button
                onClick={() => setActiveTier(null)}
                style={{
                  padding: '6px 14px', fontSize: 12, fontWeight: activeTier === null ? 600 : 500,
                  color: activeTier === null ? 'var(--text-primary)' : 'var(--text-muted)',
                  background: activeTier === null ? 'var(--card)' : 'transparent',
                  border: `1px solid ${activeTier === null ? 'var(--gold)' : 'var(--border)'}`,
                  borderRadius: 20, cursor: 'pointer',
                }}
              >
                All
              </button>
              {tierKeys.map((tk) => {
                const tier = TIER_CONFIG[tk];
                const count = tieredRemedies[tk]?.length || 0;
                if (count === 0) return null;
                const isActive = activeTier === tk;
                return (
                  <button
                    key={tk}
                    onClick={() => setActiveTier(isActive ? null : tk)}
                    style={{
                      padding: '6px 14px', fontSize: 12, fontWeight: isActive ? 600 : 500,
                      color: isActive ? tier.color : 'var(--text-muted)',
                      background: isActive ? tier.bg : 'transparent',
                      border: `1px solid ${isActive ? tier.color : 'var(--border)'}`,
                      borderRadius: 20, cursor: 'pointer',
                    }}
                  >
                    {tier.label} ({count})
                  </button>
                );
              })}
            </div>
          )}

          {hasRemedies && visibleTierKeys.map((tk) => (
            <TierSection key={tk} tierKey={tk} remedies={tieredRemedies[tk] || []} progressMap={progressMap} onAction={handleAction} actioningKey={actioningKey} />
          ))}

          {!hasRemedies && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
              <Sparkles size={40} style={{ color: 'var(--border)', marginBottom: 12 }} />
              <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                No remedy recommendations available yet.{!chartId && ' Calculate a chart first to receive personalized remedies.'}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
