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

  // Calculate progress from antardasha if available, else mahadasha
  const activePeriod = antardasha || mahadasha
  const progress = activePeriod
    ? calculateProgress(activePeriod.start_date, activePeriod.end_date)
    : 0
  const endLabel = activePeriod ? formatEndDate(activePeriod.end_date) : ''

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
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Current Dasha
          </div>

          <div className="font-display text-base text-[var(--text-primary)] mb-1">
            {mahadasha.planet} Maha Dasha
          </div>
          {antardasha && (
            <div className="text-xs text-[var(--text-secondary)] mb-1">
              {antardasha.planet} Antar Dasha
            </div>
          )}

          {/* Progress bar */}
          <div className="w-full h-1.5 rounded-full bg-[var(--border-subtle)] overflow-hidden my-2">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${progress}%`,
                background: 'var(--gold-bright)',
              }}
            />
          </div>

          <div className="flex justify-between items-center">
            <span className="text-[11px] text-[var(--text-faint)]">
              {progress}% elapsed
            </span>
            <span className="text-[11px] text-[var(--text-muted)]">
              Until {endLabel}
            </span>
          </div>

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
