'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { useGlossary } from '@/hooks/use-glossary'
import { LocalizedTerm } from '@/components/ui/localized-term'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface PanchangDetail {
  tithi: { name: string; paksha: string; percent: number }
  nakshatra: { name: string; ruler: string; pada: number; percent: number }
  yoga: { name: string; quality: string; percent: number }
  karana: { name: string; quality: string }
  vara: { day: string; ruler: string }
  inauspicious_times: {
    rahu_kaal: string
    gulika_kaal: string
    yamaganda: string
  }
  sunrise: string
  sunset: string
}

interface PanchangResponse {
  tithi: string
  nakshatra: string
  yoga: string
  karana: string
  detailed_panchang: PanchangDetail
}

/* ---------- Skeleton ---------- */

function Skeleton() {
  return (
    <div
      className="p-7 relative overflow-hidden"
      style={{ background: 'var(--hero-gradient)', borderRadius: 'inherit' }}
    >
      <div className="relative space-y-3 animate-pulse">
        <div
          className="h-3 w-20 rounded"
          style={{ background: 'var(--border)' }}
        />
        <div
          className="h-7 w-60 rounded"
          style={{ background: 'var(--border)' }}
        />
        <div
          className="h-4 w-80 rounded"
          style={{ background: 'var(--border-subtle)' }}
        />
        <div className="flex gap-2 pt-1">
          <div
            className="h-6 w-24 rounded-full"
            style={{ background: 'var(--border-subtle)' }}
          />
          <div
            className="h-6 w-28 rounded-full"
            style={{ background: 'var(--border-subtle)' }}
          />
          <div
            className="h-6 w-32 rounded-full"
            style={{ background: 'var(--border-subtle)' }}
          />
        </div>
      </div>
    </div>
  )
}

/* ---------- Component ---------- */

export default function TodaysSky({ onRemove }: { onRemove: () => void }) {
  const { location, isLoading: profileLoading } = useDefaultProfile()
  const { t } = useGlossary()

  const today = new Date().toISOString().split('T')[0] + 'T06:00:00'

  const {
    data: panchangResponse,
    isLoading: panchangLoading,
    isError,
  } = useQuery({
    queryKey: ['panchang', today, location.latitude, location.longitude],
    queryFn: () =>
      apiClient.get<PanchangResponse>(
        `/api/v1/panchang/?date=${encodeURIComponent(today)}&latitude=${location.latitude}&longitude=${location.longitude}&timezone=${encodeURIComponent(location.timezone)}`
      ),
    enabled: !profileLoading,
    staleTime: 1000 * 60 * 30, // 30 minutes
    retry: 1,
  })

  const isLoading = profileLoading || panchangLoading

  const panchang = panchangResponse?.data
  const detail = panchang?.detailed_panchang

  /* ---------- Derived display values ---------- */

  // Localized term lookups for key astrological names
  const tithiT = detail ? t(detail.tithi.name) : null
  const nakshatraT = detail ? t(detail.nakshatra.name) : null
  const yogaT = detail ? t(detail.yoga.name) : null

  const headline = detail
    ? `${detail.tithi.paksha} ${detail.tithi.name} in ${detail.nakshatra.name}`
    : ''

  const headlineLocal = detail && (tithiT?.local || nakshatraT?.local)
    ? [tithiT?.local, nakshatraT?.local].filter(Boolean).join(' \u2022 ')
    : null

  const description = detail
    ? `The Moon transits through ${detail.nakshatra.name} nakshatra (ruled by ${detail.nakshatra.ruler}). ${detail.yoga.name} yoga is active — ${detail.yoga.quality || 'a period of cosmic influence'}.`
    : ''

  const rahuKaal = detail?.inauspicious_times?.rahu_kaal

  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      {isLoading ? (
        <Skeleton />
      ) : isError || !detail ? (
        <div
          className="p-7 relative overflow-hidden"
          style={{ background: 'var(--hero-gradient)', borderRadius: 'inherit' }}
        >
          <div className="relative">
            <div
              className="text-[10px] uppercase tracking-[2.5px] font-semibold mb-3"
              style={{ color: 'var(--gold-bright)' }}
            >
              Today&apos;s Sky
            </div>
            <p className="text-sm text-[var(--text-muted)]">
              Unable to load panchang data. Please try again later.
            </p>
          </div>
        </div>
      ) : (
        <div
          className="p-7 relative overflow-hidden"
          style={{ background: 'var(--hero-gradient)', borderRadius: 'inherit' }}
        >
          {/* Subtle gold glow */}
          <div
            className="absolute -top-16 -right-10 w-48 h-48 rounded-full"
            style={{
              background:
                'radial-gradient(circle, rgba(200,145,58,0.06) 0%, transparent 70%)',
            }}
          />
          {/* Secondary blue glow */}
          <div
            className="absolute -bottom-10 left-[30%] w-40 h-40 rounded-full"
            style={{
              background:
                'radial-gradient(circle, rgba(106,159,216,0.03) 0%, transparent 60%)',
            }}
          />
          <div className="relative">
            <div
              className="text-[10px] uppercase tracking-[2.5px] font-semibold mb-3"
              style={{ color: 'var(--gold-bright)' }}
            >
              Today&apos;s Sky
            </div>
            <h2 className="font-display text-[28px] text-[var(--text-primary)] mb-1 leading-tight">
              {headline}
            </h2>
            {headlineLocal && (
              <p className="text-[14px] mb-2" style={{ color: 'var(--text-muted)', opacity: 0.7, lineHeight: 1.3 }}>
                {headlineLocal}
              </p>
            )}
            <p className="font-reading text-[15px] leading-relaxed text-[var(--text-body)] mb-5 max-w-xl">
              {description}
            </p>
            <div className="flex gap-2 flex-wrap">
              {detail.yoga.quality && (
                <span
                  className="text-[11px] font-medium px-3 py-1 rounded-full"
                  style={{
                    background: 'var(--gold-bg)',
                    color: 'var(--gold-bright)',
                  }}
                >
                  <LocalizedTerm term={detail.yoga.name} style={{ display: 'inline' }} />{' '}
                  <LocalizedTerm term="Yoga" style={{ display: 'inline' }} />
                </span>
              )}
              <span
                className="text-[11px] font-medium px-3 py-1 rounded-full"
                style={{ background: 'var(--blue-bg)', color: 'var(--blue)' }}
              >
                <LocalizedTerm term="Karana" style={{ display: 'inline' }} />:{' '}
                <LocalizedTerm term={detail.karana.name} style={{ display: 'inline' }} />
              </span>
              <span
                className="text-[11px] font-medium px-3 py-1 rounded-full"
                style={{ background: 'var(--green-bg)', color: 'var(--green)' }}
              >
                {detail.vara.day} &middot; {detail.vara.ruler}
              </span>
              {rahuKaal && (
                <span
                  className="text-[11px] font-medium px-3 py-1 rounded-full"
                  style={{
                    background: 'var(--red-bg)',
                    color: 'var(--red)',
                  }}
                >
                  <LocalizedTerm term="Rahu Kaal" style={{ display: 'inline' }} />: {rahuKaal}
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </WidgetCard>
  )
}
