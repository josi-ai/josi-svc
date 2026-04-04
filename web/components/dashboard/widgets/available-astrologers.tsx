'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface Astrologer {
  astrologer_id: string
  name?: string
  display_name?: string
  specialization?: string
  specializations?: string[]
  rating?: number
  years_of_experience?: number
  is_available?: boolean
}

/* ---------- Component ---------- */

export default function AvailableAstrologers({ onRemove }: { onRemove: () => void }) {
  const {
    data: astrologersResponse,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['astrologers', 'search', 'widget'],
    queryFn: () =>
      apiClient.get<Astrologer[]>('/api/v1/astrologers/search?limit=3'),
    retry: false,
  })

  // Extract astrologers array — API returns { astrologers: [], total: 0 } nested in data
  const responseData = astrologersResponse?.data;
  let astrologers: Astrologer[] = [];
  if (Array.isArray(responseData)) {
    astrologers = responseData;
  } else if (responseData && typeof responseData === 'object') {
    const nested = (responseData as Record<string, unknown>).astrologers;
    astrologers = Array.isArray(nested) ? nested as Astrologer[] : [];
  }

  /* ---------- Helpers ---------- */
  function getInitial(a: Astrologer): string {
    const name = a.display_name || a.name || '?'
    return name.charAt(0).toUpperCase()
  }

  function getDisplayName(a: Astrologer): string {
    return a.display_name || a.name || 'Astrologer'
  }

  function getSpecLabel(a: Astrologer): string {
    const spec = a.specialization || a.specializations?.[0] || ''
    const years = a.years_of_experience
    const parts = [spec, years ? `${years} years` : ''].filter(Boolean)
    return parts.join(' \u00b7 ') || 'Astrologer'
  }

  return (
    <WidgetCard tradition="general" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          Available Astrologers
        </div>

        {/* Loading */}
        {isLoading && (
          <div className="flex flex-col gap-3 mb-3">
            {[1, 2].map((n) => (
              <div key={n} className="flex gap-3 items-center">
                <div
                  className="w-10 h-10 rounded-full animate-pulse flex-shrink-0"
                  style={{ background: 'var(--surface)' }}
                />
                <div className="flex-1">
                  <div className="h-3 w-24 rounded animate-pulse mb-1.5" style={{ background: 'var(--surface)' }} />
                  <div className="h-2.5 w-16 rounded animate-pulse" style={{ background: 'var(--surface)' }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error or empty */}
        {!isLoading && (isError || astrologers.length === 0) && (
          <div className="text-xs text-[var(--text-muted)] leading-relaxed mb-3">
            No astrologers available yet — check back soon
          </div>
        )}

        {/* Astrologer cards */}
        {!isLoading &&
          !isError &&
          astrologers.map((a, i) => (
            <div
              key={a.astrologer_id}
              className={`flex gap-3 items-center ${i < astrologers.length - 1 ? 'mb-3' : 'mb-3'}`}
            >
              {/* Avatar */}
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center font-display text-[15px] text-[var(--text-primary)] flex-shrink-0"
                style={{ background: 'var(--avatar-placeholder)' }}
              >
                {getInitial(a)}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold text-[var(--text-primary)] mb-px truncate">
                  {getDisplayName(a)}
                </div>
                <div className="text-[10px] text-[var(--text-muted)] truncate">
                  {getSpecLabel(a)}
                </div>
                {a.rating != null && (
                  <div className="text-[9px] text-[var(--text-muted)] mt-0.5">
                    {'★'.repeat(Math.round(a.rating))}{' '}
                    <span className="text-[var(--text-faint)]">
                      {a.rating.toFixed(1)}
                    </span>
                  </div>
                )}
                {a.is_available && (
                  <div
                    className="text-[9px] font-medium mt-0.5"
                    style={{ color: 'var(--green)' }}
                  >
                    &#9679; Available now
                  </div>
                )}
              </div>

              {/* Book button */}
              <Link
                href={`/astrologers/${a.astrologer_id}`}
                className="px-3.5 py-1.5 rounded-lg text-[11px] font-semibold text-white border-none cursor-pointer flex-shrink-0 no-underline"
                style={{ background: 'var(--gold)' }}
              >
                Book
              </Link>
            </div>
          ))}

        <Link
          href="/astrologers"
          className="text-xs font-semibold no-underline"
          style={{ color: 'var(--gold)' }}
        >
          View all astrologers &rarr;
        </Link>
      </div>
    </WidgetCard>
  )
}
