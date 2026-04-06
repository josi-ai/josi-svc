'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface DashaPeriod {
  planet: string
  start_date: string
  end_date: string
  duration_years: number
}

interface DashaResponse {
  person_id: string
  birth_nakshatra: string
  current_dasha: {
    mahadasha: DashaPeriod
    antardasha?: DashaPeriod
    pratyantardasha?: DashaPeriod
    description?: string
  } | null
}

/* ---------- Helpers ---------- */

function calculateProgress(startDate: string, endDate: string): number {
  const start = new Date(startDate).getTime()
  const end = new Date(endDate).getTime()
  const now = Date.now()
  if (end <= start) return 0
  const pct = ((now - start) / (end - start)) * 100
  return Math.max(0, Math.min(100, Math.round(pct)))
}

function formatEndDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  } catch {
    return dateStr
  }
}

/* ---------- Skeleton ---------- */

function Skeleton() {
  return (
    <div className="p-5 animate-pulse space-y-2">
      <div className="h-3 w-24 rounded" style={{ background: 'var(--border)' }} />
      <div className="h-5 w-40 rounded" style={{ background: 'var(--border)' }} />
      <div className="h-4 w-32 rounded" style={{ background: 'var(--border-subtle)' }} />
      <div className="h-1.5 w-full rounded-full" style={{ background: 'var(--border-subtle)' }} />
      <div className="flex justify-between">
        <div className="h-3 w-16 rounded" style={{ background: 'var(--border-subtle)' }} />
        <div className="h-3 w-24 rounded" style={{ background: 'var(--border-subtle)' }} />
      </div>
    </div>
  )
}

/* ---------- Component ---------- */

export default function CurrentDasha({ onRemove }: { onRemove: () => void }) {
  const { defaultProfile, isLoading: profileLoading } = useDefaultProfile()

  const {
    data: dashaResponse,
    isLoading: dashaLoading,
    isError,
  } = useQuery({
    queryKey: ['dasha-vimshottari', defaultProfile?.person_id],
    queryFn: () =>
      apiClient.get<DashaResponse>(
        `/api/v1/dasha/vimshottari/${defaultProfile!.person_id}`
      ),
    enabled: !profileLoading && !!defaultProfile?.person_id,
    staleTime: 1000 * 60 * 60, // 1 hour
    retry: 1,
  })

  const isLoading = profileLoading || dashaLoading

  const dasha = dashaResponse?.data
  const currentDasha = dasha?.current_dasha
  const mahadasha = currentDasha?.mahadasha
  const antardasha = currentDasha?.antardasha

  // Calculate progress for each period independently
  const mahaProgress = mahadasha
    ? calculateProgress(mahadasha.start_date, mahadasha.end_date)
    : 0
  const mahaEndLabel = mahadasha ? formatEndDate(mahadasha.end_date) : ''

  const antarProgress = antardasha
    ? calculateProgress(antardasha.start_date, antardasha.end_date)
    : 0
  const antarEndLabel = antardasha ? formatEndDate(antardasha.end_date) : ''

  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      {isLoading ? (
        <Skeleton />
      ) : !defaultProfile ? (
        /* No profile CTA */
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Current Dasha
          </div>
          <p className="text-sm text-[var(--text-secondary)] mb-3">
            Create a birth profile to see your dasha periods.
          </p>
          <a
            href="/profiles"
            className="text-xs font-semibold"
            style={{ color: 'var(--gold)' }}
          >
            Add profile &rarr;
          </a>
        </div>
      ) : isError || !mahadasha ? (
        /* Error state */
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Current Dasha
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            Unable to load dasha data. Please try again later.
          </p>
        </div>
      ) : (
        /* Data state */
        <div className="p-5" data-testid="dasha-widget-v2">
          {(() => { console.log('[DASHA-DEBUG] antardasha:', antardasha, 'mahadasha:', mahadasha); return null; })()}
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Current Dasha
          </div>

          {/* Maha Dasha progress */}
          <div className="mb-3">
            <div className="flex justify-between items-baseline mb-1">
              <span className="font-display text-sm text-[var(--text-primary)] font-medium">
                {mahadasha.planet} Maha Dasha
              </span>
              <span className="text-[10px] text-[var(--text-faint)]">
                {mahaProgress}%
              </span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-[var(--border-subtle)] overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${mahaProgress}%`,
                  background: 'var(--gold-bright)',
                }}
              />
            </div>
            <div className="text-[10px] text-[var(--text-faint)] mt-1">
              Until {mahaEndLabel}
            </div>
          </div>

          {/* Antar Dasha progress */}
          {antardasha && (
            <div className="mb-1">
              <div className="flex justify-between items-baseline mb-1">
                <span className="text-xs text-[var(--text-secondary)] font-medium">
                  {antardasha.planet} Antar Dasha
                </span>
                <span className="text-[10px] text-[var(--text-faint)]">
                  {antarProgress}%
                </span>
              </div>
              <div className="w-full h-1 rounded-full bg-[var(--border-subtle)] overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${antarProgress}%`,
                    background: 'var(--gold)',
                  }}
                />
              </div>
              <div className="text-[10px] text-[var(--text-faint)] mt-1">
                Until {antarEndLabel}
              </div>
            </div>
          )}

          <div
            className="text-xs font-semibold mt-3 cursor-pointer"
            style={{ color: 'var(--gold)' }}
          >
            Chat about this &rarr;
          </div>
        </div>
      )}
    </WidgetCard>
  )
}
