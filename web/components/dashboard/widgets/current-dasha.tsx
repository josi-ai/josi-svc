'use client'

import { useState } from 'react'
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

function formatDateTime(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })
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

/* ---------- Level Row ---------- */

function DashaLevelRow({ label, period }: { label: string; period: DashaPeriod }) {
  const progress = calculateProgress(period.start_date, period.end_date)
  const startStr = formatDateTime(period.start_date)
  const endStr = formatDateTime(period.end_date)
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 3 }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>{label}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--gold)' }}>{period.planet}</span>
        <span style={{ fontSize: 10, color: 'var(--text-faint)', marginLeft: 'auto', fontWeight: 500 }}>{progress}%</span>
      </div>
      <div style={{ width: '100%', height: 5, borderRadius: 3, background: 'var(--border-subtle)', overflow: 'hidden', marginBottom: 3 }}>
        <div style={{ height: '100%', borderRadius: 3, width: `${progress}%`, background: 'var(--gold)', transition: 'width 0.5s ease' }} />
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
        {startStr} → {endStr}
      </div>
    </div>
  )
}

/* ---------- Levels Container ---------- */

function DashaLevels({ levels }: { levels: { period: DashaPeriod | undefined; label: string }[] }) {
  const [expanded, setExpanded] = useState(false)

  const primary = levels.slice(0, 3)
  const secondary = levels.slice(3)
  const hasSecondary = secondary.some(l => l.period)

  return (
    <div className="p-5">
      <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--text-faint)', marginBottom: 12 }}>
        Current Dasha
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {primary.map(({ period, label }) => {
          if (!period) return null
          return <DashaLevelRow key={label} label={label} period={period} />
        })}

        {/* Expanded levels 4-5 */}
        {expanded && secondary.map(({ period, label }) => {
          if (!period) return null
          return <DashaLevelRow key={label} label={label} period={period} />
        })}
      </div>

      {/* See more / See less toggle */}
      {hasSecondary && (
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            display: 'inline-block', marginTop: 10, fontSize: 11, fontWeight: 600,
            color: 'var(--text-muted)', background: 'none', border: 'none',
            cursor: 'pointer', padding: 0, textDecoration: 'underline',
            textUnderlineOffset: 2,
          }}
        >
          {expanded ? 'See less' : 'See more (Sookshamam & Pranam)'}
        </button>
      )}

      <a href="/dasha" style={{ display: 'inline-block', marginTop: 10, fontSize: 12, fontWeight: 600, color: 'var(--gold)', textDecoration: 'none' }}>
        View full Dasha &rarr;
      </a>
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

  // Build all 5 levels — same indentation, label first
  const levels: { period: DashaPeriod | undefined; label: string }[] = [
    { period: mahadasha, label: 'Dasha' },
    { period: antardasha, label: 'Bukthi' },
    { period: pratyantardasha, label: 'Antaram' },
    { period: sookshma, label: 'Sookshamam' },
    { period: prana, label: 'Pranam' },
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
        /* Data state — levels 1-3 visible, 4-5 behind "See more" */
        <DashaLevels levels={levels} />
      )}
    </WidgetCard>
  )
}
