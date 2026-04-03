'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface Pillar {
  heavenly_stem?: string
  earthly_branch?: string
  element?: string
  animal?: string
}

interface ChartData {
  four_pillars?: {
    year?: Pillar
    month?: Pillar
    day?: Pillar
    hour?: Pillar
  }
  day_master?: string
  day_master_element?: string
  [key: string]: unknown
}

interface Chart {
  chart_id: string
  chart_type: string
  chart_data: ChartData | null
}

/* ---------- Helpers ---------- */

const PILLAR_ORDER: Array<{ key: 'year' | 'month' | 'day' | 'hour'; label: string }> = [
  { key: 'year', label: 'Year' },
  { key: 'month', label: 'Month' },
  { key: 'day', label: 'Day' },
  { key: 'hour', label: 'Hour' },
]

/* ---------- Component ---------- */

export default function BaziSummary({ onRemove }: { onRemove: () => void }) {
  const { defaultProfile, isLoading: profileLoading } = useDefaultProfile()

  const {
    data: chartsResponse,
    isLoading: chartsLoading,
  } = useQuery({
    queryKey: ['charts', 'person', defaultProfile?.person_id],
    queryFn: () =>
      apiClient.get<Chart[]>(
        `/api/v1/charts/person/${defaultProfile!.person_id}`
      ),
    enabled: !!defaultProfile?.person_id,
  })

  const charts = chartsResponse?.data || []
  const chineseChart = charts.find((c) => c.chart_type === 'chinese')
  const chartData = chineseChart?.chart_data
  const fourPillars = chartData?.four_pillars

  const isLoading = profileLoading || chartsLoading

  /* ---------- No profile ---------- */
  if (!profileLoading && !defaultProfile) {
    return (
      <WidgetCard tradition="chinese" onRemove={onRemove}>
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            BaZi Summary
          </div>
          <div className="text-xs text-[var(--text-muted)] leading-relaxed">
            Create a profile to see your BaZi chart
          </div>
        </div>
      </WidgetCard>
    )
  }

  /* ---------- Loading ---------- */
  if (isLoading) {
    return (
      <WidgetCard tradition="chinese" onRemove={onRemove}>
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            BaZi Summary
          </div>
          <div className="grid grid-cols-4 gap-1">
            {[1, 2, 3, 4].map((n) => (
              <div
                key={n}
                className="h-16 rounded-md animate-pulse"
                style={{ background: 'var(--surface)' }}
              />
            ))}
          </div>
        </div>
      </WidgetCard>
    )
  }

  /* ---------- No Chinese chart ---------- */
  if (!chineseChart || !fourPillars) {
    return (
      <WidgetCard tradition="chinese" onRemove={onRemove}>
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            BaZi Summary
          </div>
          <div className="text-xs text-[var(--text-muted)] leading-relaxed mb-3">
            Calculate a Chinese chart to see your BaZi
          </div>
          <Link
            href="/charts/new"
            className="text-xs font-semibold"
            style={{ color: 'var(--gold)' }}
          >
            Calculate now &rarr;
          </Link>
        </div>
      </WidgetCard>
    )
  }

  /* ---------- Render pillars ---------- */
  const dayMasterLabel =
    chartData?.day_master || chartData?.day_master_element
      ? `Day Master: ${chartData.day_master_element || ''} (${fourPillars.day?.heavenly_stem || ''})`
      : null

  return (
    <WidgetCard tradition="chinese" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          BaZi Summary
        </div>

        {dayMasterLabel && (
          <div className="font-display text-[15px] text-[var(--text-primary)] mb-2.5">
            {dayMasterLabel}
          </div>
        )}

        {/* Four Pillars grid */}
        <div className="grid grid-cols-4 gap-1">
          {PILLAR_ORDER.map((p) => {
            const pillar = fourPillars[p.key]
            return (
              <div
                key={p.label}
                className="text-center py-1.5 px-1 rounded-md border"
                style={{
                  background: 'var(--surface)',
                  borderColor: 'var(--border-subtle)',
                }}
              >
                <div className="text-[8px] uppercase tracking-[0.5px] text-[var(--text-faint)] mb-0.5">
                  {p.label}
                </div>
                <div className="text-sm mb-px">
                  {pillar?.heavenly_stem || '--'}
                </div>
                <div className="text-[9px] font-medium text-[var(--text-primary)]">
                  {pillar?.element || '--'}
                </div>
                <div className="text-[8px] text-[var(--text-muted)]">
                  {pillar?.animal || pillar?.earthly_branch || '--'}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </WidgetCard>
  )
}
