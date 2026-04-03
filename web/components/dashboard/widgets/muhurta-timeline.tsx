'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface BestTimesResponse {
  date: string
  best_times: Array<{
    start_time: string
    end_time: string
    quality: string
    overall_score: number
  }>
  rahu_kaal: {
    start: string
    end: string
    duration_minutes: number
  }
  general_advice: string
}

interface PanchangResponse {
  detailed_panchang: {
    sunrise: string
    sunset: string
    inauspicious_times: {
      rahu_kaal: string
      gulika_kaal: string
      yamaganda: string
    }
    auspicious_times: {
      abhijit_muhurta: string
      brahma_muhurta: string
    }
  }
}

/* ---------- Types for timeline segments ---------- */

interface TimeSegment {
  label: string
  startMinute: number // minutes from 6AM
  endMinute: number
  type: 'good' | 'avoid' | 'special' | 'neutral'
}

/* ---------- Helpers ---------- */

const COLOR_MAP: Record<string, string> = {
  good: 'var(--bar-good)',
  avoid: 'var(--bar-avoid)',
  special: 'var(--bar-special)',
  neutral: 'var(--bar-neutral)',
}

const LEGEND: Array<{ label: string; type: string }> = [
  { label: 'Good', type: 'good' },
  { label: 'Rahu', type: 'avoid' },
  { label: 'Shubh', type: 'special' },
  { label: 'Neutral', type: 'neutral' },
]

const TIME_LABELS = ['6 AM', '8 AM', '10 AM', '12 PM', '2 PM', '4 PM', '6 PM']

/** Parse "HH:MM" or "HH:MM AM/PM" into minutes from midnight */
function parseTimeToMinutes(time: string): number {
  if (!time) return 0

  // Try "HH:MM AM/PM" format first
  const amPmMatch = time.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i)
  if (amPmMatch) {
    let hours = parseInt(amPmMatch[1], 10)
    const minutes = parseInt(amPmMatch[2], 10)
    const period = amPmMatch[3].toUpperCase()
    if (period === 'PM' && hours !== 12) hours += 12
    if (period === 'AM' && hours === 12) hours = 0
    return hours * 60 + minutes
  }

  // Try "HH:MM" (24-hour) format
  const match24 = time.match(/^(\d{1,2}):(\d{2})$/)
  if (match24) {
    return parseInt(match24[1], 10) * 60 + parseInt(match24[2], 10)
  }

  return 0
}

/** Convert minutes-from-midnight to "h:mm AM/PM" */
function minutesToLabel(m: number): string {
  const h = Math.floor(m / 60)
  const min = m % 60
  const period = h >= 12 ? 'PM' : 'AM'
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h
  return `${h12}:${min.toString().padStart(2, '0')} ${period}`
}

/** Build timeline segments from panchang timing data */
function buildSegmentsFromPanchang(detail: PanchangResponse['detailed_panchang']): TimeSegment[] {
  const DAY_START = 6 * 60 // 6 AM
  const DAY_END = 18 * 60 // 6 PM

  const segments: TimeSegment[] = []

  // Parse inauspicious times
  type TimePeriod = { label: string; start: number; end: number; type: 'avoid' | 'special' }
  const periods: TimePeriod[] = []

  // Rahu Kaal — could be "HH:MM - HH:MM" or "HH:MM AM - HH:MM PM" or just "HH:MM"
  const rahuStr = detail.inauspicious_times?.rahu_kaal || ''
  const rahuParts = rahuStr.split(/\s*-\s*/)
  if (rahuParts.length === 2) {
    const rs = parseTimeToMinutes(rahuParts[0].trim())
    const re = parseTimeToMinutes(rahuParts[1].trim())
    if (rs && re && rs < re) {
      periods.push({ label: 'Rahu Kaal', start: rs, end: re, type: 'avoid' })
    }
  }

  // Gulika Kaal
  const gulikaStr = detail.inauspicious_times?.gulika_kaal || ''
  const gulikaParts = gulikaStr.split(/\s*-\s*/)
  if (gulikaParts.length === 2) {
    const gs = parseTimeToMinutes(gulikaParts[0].trim())
    const ge = parseTimeToMinutes(gulikaParts[1].trim())
    if (gs && ge && gs < ge) {
      periods.push({ label: 'Gulika', start: gs, end: ge, type: 'avoid' })
    }
  }

  // Abhijit Muhurta (special / auspicious)
  const abhijitStr = detail.auspicious_times?.abhijit_muhurta || ''
  const abhijitParts = abhijitStr.split(/\s*-\s*/)
  if (abhijitParts.length === 2) {
    const as_ = parseTimeToMinutes(abhijitParts[0].trim())
    const ae = parseTimeToMinutes(abhijitParts[1].trim())
    if (as_ && ae && as_ < ae) {
      periods.push({ label: 'Abhijit', start: as_, end: ae, type: 'special' })
    }
  }

  // Sort periods by start time
  periods.sort((a, b) => a.start - b.start)

  // Fill timeline from DAY_START to DAY_END
  let cursor = DAY_START
  for (const p of periods) {
    const pStart = Math.max(p.start, DAY_START)
    const pEnd = Math.min(p.end, DAY_END)
    if (pStart >= DAY_END || pEnd <= DAY_START) continue

    if (cursor < pStart) {
      segments.push({
        label: 'Good',
        startMinute: cursor,
        endMinute: pStart,
        type: 'good',
      })
    }
    segments.push({
      label: p.label,
      startMinute: pStart,
      endMinute: pEnd,
      type: p.type,
    })
    cursor = pEnd
  }
  if (cursor < DAY_END) {
    segments.push({
      label: 'Good',
      startMinute: cursor,
      endMinute: DAY_END,
      type: 'good',
    })
  }

  return segments
}

/** Build segments from best-times-today response */
function buildSegmentsFromBestTimes(data: BestTimesResponse): TimeSegment[] {
  const DAY_START = 6 * 60
  const DAY_END = 18 * 60
  const segments: TimeSegment[] = []

  type TimePeriod = { label: string; start: number; end: number; type: 'avoid' | 'special' | 'good' }
  const periods: TimePeriod[] = []

  // Rahu kaal
  if (data.rahu_kaal) {
    const rs = parseTimeToMinutes(data.rahu_kaal.start)
    const re = parseTimeToMinutes(data.rahu_kaal.end)
    if (rs && re && rs < re) {
      periods.push({ label: 'Rahu Kaal', start: rs, end: re, type: 'avoid' })
    }
  }

  // Best times
  for (const t of data.best_times || []) {
    const ts = parseTimeToMinutes(t.start_time)
    const te = parseTimeToMinutes(t.end_time)
    if (ts && te && ts < te) {
      const type = t.quality === 'Excellent' ? 'special' : 'good'
      periods.push({ label: t.quality || 'Good', start: ts, end: te, type })
    }
  }

  periods.sort((a, b) => a.start - b.start)

  let cursor = DAY_START
  for (const p of periods) {
    const pStart = Math.max(p.start, DAY_START)
    const pEnd = Math.min(p.end, DAY_END)
    if (pStart >= DAY_END || pEnd <= DAY_START) continue

    if (cursor < pStart) {
      segments.push({ label: 'Neutral', startMinute: cursor, endMinute: pStart, type: 'neutral' })
    }
    segments.push({ label: p.label, startMinute: pStart, endMinute: pEnd, type: p.type })
    cursor = pEnd
  }
  if (cursor < DAY_END) {
    segments.push({ label: 'Neutral', startMinute: cursor, endMinute: DAY_END, type: 'neutral' })
  }

  return segments
}

/* ---------- Skeleton ---------- */

function Skeleton() {
  return (
    <div className="p-5 animate-pulse space-y-3">
      <div className="h-3 w-28 rounded" style={{ background: 'var(--border)' }} />
      <div className="h-7 w-full rounded-md" style={{ background: 'var(--border-subtle)' }} />
      <div className="flex justify-between">
        {TIME_LABELS.map((l) => (
          <div
            key={l}
            className="h-2 w-6 rounded"
            style={{ background: 'var(--border-subtle)' }}
          />
        ))}
      </div>
      <div className="h-10 w-full rounded-lg" style={{ background: 'var(--border-subtle)' }} />
    </div>
  )
}

/* ---------- Component ---------- */

export default function MuhurtaTimeline({ onRemove }: { onRemove: () => void }) {
  const { location, isLoading: profileLoading } = useDefaultProfile()

  // Try best-times-today first
  const {
    data: bestTimesResponse,
    isError: bestTimesError,
    isLoading: bestTimesLoading,
  } = useQuery({
    queryKey: ['best-times-today', location.latitude, location.longitude],
    queryFn: () =>
      apiClient.get<BestTimesResponse>(
        `/api/v1/muhurta/best-times-today?latitude=${location.latitude}&longitude=${location.longitude}&timezone=${encodeURIComponent(location.timezone)}`
      ),
    enabled: !profileLoading,
    staleTime: 1000 * 60 * 30,
    retry: 0, // Don't retry — we have a fallback
  })

  // Fallback to panchang if best-times-today fails
  const today = new Date().toISOString().split('T')[0] + 'T06:00:00'
  const {
    data: panchangResponse,
    isLoading: panchangLoading,
  } = useQuery({
    queryKey: ['panchang-muhurta', today, location.latitude, location.longitude],
    queryFn: () =>
      apiClient.get<PanchangResponse>(
        `/api/v1/panchang/?date=${encodeURIComponent(today)}&latitude=${location.latitude}&longitude=${location.longitude}&timezone=${encodeURIComponent(location.timezone)}`
      ),
    enabled: !profileLoading && bestTimesError,
    staleTime: 1000 * 60 * 30,
    retry: 1,
  })

  const isLoading = profileLoading || bestTimesLoading || (bestTimesError && panchangLoading)

  // Build segments from whichever data source is available
  let segments: TimeSegment[] = []
  let rahuKaalLabel = ''

  const bestTimes = bestTimesResponse?.data
  const panchangDetail = panchangResponse?.data?.detailed_panchang

  if (bestTimes) {
    segments = buildSegmentsFromBestTimes(bestTimes)
    if (bestTimes.rahu_kaal) {
      rahuKaalLabel = `${bestTimes.rahu_kaal.start} - ${bestTimes.rahu_kaal.end}`
    }
  } else if (panchangDetail) {
    segments = buildSegmentsFromPanchang(panchangDetail)
    rahuKaalLabel = panchangDetail.inauspicious_times?.rahu_kaal || ''
  }

  // Find current-time marker position
  const now = new Date()
  const nowMinutes = now.getHours() * 60 + now.getMinutes()
  const DAY_START = 6 * 60
  const DAY_END = 18 * 60
  const showMarker = nowMinutes >= DAY_START && nowMinutes <= DAY_END
  const markerPercent = showMarker
    ? ((nowMinutes - DAY_START) / (DAY_END - DAY_START)) * 100
    : 0

  const hasData = segments.length > 0

  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      {isLoading ? (
        <Skeleton />
      ) : !hasData ? (
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3.5">
            Muhurta Timeline
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            Unable to load muhurta data. Please try again later.
          </p>
        </div>
      ) : (
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3.5">
            Muhurta Timeline
          </div>

          {/* Color-coded time bar */}
          <div className="flex h-7 rounded-md overflow-hidden border border-[var(--border)] mb-2 relative">
            {segments.map((seg, i) => {
              const flex = seg.endMinute - seg.startMinute
              return (
                <div
                  key={i}
                  className="relative"
                  style={{
                    flex,
                    background: COLOR_MAP[seg.type] || COLOR_MAP.neutral,
                  }}
                  title={`${seg.label}: ${minutesToLabel(seg.startMinute)} – ${minutesToLabel(seg.endMinute)}`}
                />
              )
            })}
            {/* Current time marker */}
            {showMarker && (
              <div
                className="absolute top-[-4px] w-0.5 h-9 z-[2]"
                style={{
                  left: `${markerPercent}%`,
                  background: 'var(--gold-bright)',
                  boxShadow: '0 0 6px rgba(212,160,74,0.4)',
                }}
              >
                <div
                  className="absolute -top-[3px] -left-[3px] w-2 h-2 rounded-full"
                  style={{ background: 'var(--gold-bright)' }}
                />
              </div>
            )}
          </div>

          {/* Time labels */}
          <div className="flex justify-between text-[9px] text-[var(--text-faint)] mb-3.5">
            {TIME_LABELS.map((label) => (
              <span key={label}>{label}</span>
            ))}
          </div>

          {/* Legend */}
          <div className="flex gap-3.5 mb-3">
            {LEGEND.map((item) => (
              <div key={item.label} className="flex items-center gap-1.5">
                <div
                  className="w-2.5 h-2.5 rounded-sm"
                  style={{ background: COLOR_MAP[item.type] }}
                />
                <span className="text-[10px] text-[var(--text-muted)]">
                  {item.label}
                </span>
              </div>
            ))}
          </div>

          {/* Rahu Kalam warning */}
          {rahuKaalLabel && (
            <div
              className="py-2 px-3 rounded-lg border"
              style={{
                background: 'var(--red-bg)',
                borderColor: 'rgba(196,93,74,0.15)',
              }}
            >
              <div
                className="text-[11px] font-semibold"
                style={{ color: 'var(--red)' }}
              >
                &#9888; Rahu Kalam: {rahuKaalLabel}
              </div>
              <div className="text-[10px] text-[var(--text-muted)] mt-0.5">
                Avoid starting new ventures during this period
              </div>
            </div>
          )}
        </div>
      )}
    </WidgetCard>
  )
}
