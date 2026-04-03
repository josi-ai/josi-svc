'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface ChartInterpretation {
  chart_interpretation_id: string
  interpretation_type: string
  title: string
  summary: string
  language: string
  created_at: string
}

interface Chart {
  chart_id: string
  person_id: string
  chart_type: string
  tradition_id: number | null
  tradition_name: string | null
  interpretations?: ChartInterpretation[]
  created_at: string
}

/* ---------- Skeleton ---------- */

function Skeleton() {
  return (
    <div className="p-5">
      <div className="space-y-3 animate-pulse">
        <div
          className="h-3 w-24 rounded"
          style={{ background: 'var(--border)' }}
        />
        <div
          className="h-5 w-48 rounded"
          style={{ background: 'var(--border)' }}
        />
        <div
          className="h-4 w-full rounded"
          style={{ background: 'var(--border-subtle)' }}
        />
        <div
          className="h-4 w-3/4 rounded"
          style={{ background: 'var(--border-subtle)' }}
        />
        <div
          className="h-3 w-28 rounded"
          style={{ background: 'var(--border-subtle)' }}
        />
      </div>
    </div>
  )
}

/* ---------- Empty state ---------- */

function EmptyState() {
  return (
    <div className="p-5">
      <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
        Latest AI Reading
      </div>
      <p className="font-reading text-[13px] leading-[1.75] text-[var(--text-body-reading)] mb-4">
        No AI readings yet. Ask Josi AI a question to get your first reading.
      </p>
      <Link
        href="/ai"
        className="text-xs font-semibold"
        style={{ color: 'var(--gold)' }}
      >
        Try AI Insights &rarr;
      </Link>
    </div>
  )
}

/* ---------- Helpers ---------- */

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
  if (diffDays < 30) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
  return date.toLocaleDateString()
}

/* ---------- Component ---------- */

export default function LatestReading({ onRemove }: { onRemove: () => void }) {
  const { defaultProfile, isLoading: profileLoading } = useDefaultProfile()

  // Fetch charts for the default profile to find one with interpretations
  const {
    data: chartsResponse,
    isLoading: chartsLoading,
  } = useQuery({
    queryKey: ['charts', 'latest-reading', defaultProfile?.person_id],
    queryFn: () =>
      apiClient.get<Chart[]>(
        `/api/v1/charts/person/${defaultProfile!.person_id}`
      ),
    enabled: !!defaultProfile?.person_id,
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })

  const isLoading = profileLoading || chartsLoading

  // Find the latest interpretation across all charts
  const latestInterpretation = (() => {
    const charts = chartsResponse?.data
    if (!charts || !Array.isArray(charts)) return null

    let best: { interpretation: ChartInterpretation; chart: Chart } | null = null

    for (const chart of charts) {
      if (chart.interpretations && chart.interpretations.length > 0) {
        for (const interp of chart.interpretations) {
          if (
            !best ||
            new Date(interp.created_at) > new Date(best.interpretation.created_at)
          ) {
            best = { interpretation: interp, chart }
          }
        }
      }
    }

    return best
  })()

  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      {isLoading ? (
        <Skeleton />
      ) : !latestInterpretation ? (
        <EmptyState />
      ) : (
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Latest AI Reading
          </div>

          <div className="font-display text-[17px] text-[var(--text-primary)] mb-2 leading-snug">
            {latestInterpretation.interpretation.title ||
              latestInterpretation.interpretation.interpretation_type}
          </div>

          <p className="font-reading text-[13px] leading-[1.75] text-[var(--text-body-reading)] mb-2.5 line-clamp-2">
            {latestInterpretation.interpretation.summary}
          </p>

          <div className="text-[10px] text-[var(--text-faint)] mb-2.5">
            Generated {formatRelativeTime(latestInterpretation.interpretation.created_at)}
          </div>

          <div className="flex gap-3">
            <Link
              href="/ai"
              className="text-xs font-semibold cursor-pointer"
              style={{ color: 'var(--gold)' }}
            >
              Read more &rarr;
            </Link>
            <Link
              href="/ai?q=Tell me more about my last reading"
              className="text-xs font-semibold cursor-pointer"
              style={{ color: 'var(--purple)' }}
            >
              Chat about this &rarr;
            </Link>
          </div>
        </div>
      )}
    </WidgetCard>
  )
}
