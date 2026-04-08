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
    sookshma?: DashaPeriod
    prana?: DashaPeriod
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
  const pratyantardasha = currentDasha?.pratyantardasha
  const sookshma = currentDasha?.sookshma
  const prana = currentDasha?.prana

  // Build all 5 levels
  const levels: { period: DashaPeriod | undefined; label: string; barHeight: number; opacity: number }[] = [
    { period: mahadasha, label: 'Dasha', barHeight: 6, opacity: 1 },
    { period: antardasha, label: 'Bukthi', barHeight: 5, opacity: 1 },
    { period: pratyantardasha, label: 'Antaram', barHeight: 4, opacity: 0.85 },
    { period: sookshma, label: 'Sookshma', barHeight: 3, opacity: 0.7 },
    { period: prana, label: 'Prana', barHeight: 2, opacity: 0.55 },
  ]

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
        /* Data state — all 5 levels */
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Current Dasha
          </div>

          {levels.map(({ period, label, barHeight, opacity }, idx) => {
            if (!period) return null
            const progress = calculateProgress(period.start_date, period.end_date)
            const endLabel = formatEndDate(period.end_date)
            const isFirst = idx === 0
            return (
              <div key={label} style={{ marginBottom: idx < levels.length - 1 ? 10 : 4, paddingLeft: idx * 4 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 3 }}>
                  <span style={{ fontSize: isFirst ? 14 : 12, fontWeight: isFirst ? 600 : 500, color: 'var(--text-primary)' }}>
                    {period.planet}{' '}
                    <span style={{ fontSize: 10, fontWeight: 400, color: 'var(--text-muted)' }}>{label}</span>
                  </span>
                  <span style={{ fontSize: 10, color: 'var(--text-faint)', fontWeight: 500 }}>{progress}%</span>
                </div>
                <div style={{ width: '100%', height: barHeight, borderRadius: barHeight, background: 'var(--border-subtle)', overflow: 'hidden' }}>
                  <div style={{ height: '100%', borderRadius: barHeight, width: `${progress}%`, background: 'var(--gold)', opacity, transition: 'width 0.5s ease' }} />
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-faint)', marginTop: 2 }}>Until {endLabel}</div>
              </div>
            )
          })}

          <a href="/dasha" style={{ display: 'inline-block', marginTop: 8, fontSize: 12, fontWeight: 600, color: 'var(--gold)', textDecoration: 'none' }}>
            View full Dasha &rarr;
          </a>
        </div>
      )}
    </WidgetCard>
  )
}
