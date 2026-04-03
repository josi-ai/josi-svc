'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface Transit {
  transiting_planet: string
  aspect_type: string
  natal_planet: string
  intensity?: number | string
  description?: string
  // API field names (mapped below)
  planet?: string
  aspect?: string
  natal_sign?: string
  current_sign?: string
  effects?: string
  orb?: number
}

/* ---------- Component ---------- */

export default function WesternTransit({ onRemove }: { onRemove: () => void }) {
  const { defaultProfile, isLoading: profileLoading } = useDefaultProfile()

  const {
    data: transitsResponse,
    isLoading: transitsLoading,
    isError,
  } = useQuery({
    queryKey: ['transits', 'current', defaultProfile?.person_id],
    queryFn: () =>
      apiClient.get<Transit[]>(
        `/api/v1/transits/current/${defaultProfile!.person_id}`
      ),
    enabled: !!defaultProfile?.person_id,
  })

  const rawData = transitsResponse?.data;
  const rawTransits: Transit[] = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.major_transits || [];
  // Normalize API fields to widget fields
  const transits = rawTransits.map((t) => ({
    ...t,
    transiting_planet: t.transiting_planet || t.planet || 'Unknown',
    aspect_type: t.aspect_type || t.aspect || '',
    natal_planet: t.natal_planet || `natal ${t.natal_sign || ''}`.trim(),
    intensity: t.intensity ?? t.orb,
    description: t.description || t.effects || '',
  }));
  const isLoading = profileLoading || transitsLoading

  /* ---------- No profile state ---------- */
  if (!profileLoading && !defaultProfile) {
    return (
      <WidgetCard tradition="western" onRemove={onRemove}>
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3.5">
            Western Transit Alert
          </div>
          <div className="text-xs text-[var(--text-muted)] leading-relaxed">
            Create a profile to see transits
          </div>
        </div>
      </WidgetCard>
    )
  }

  return (
    <WidgetCard tradition="western" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3.5">
          Western Transit Alert
        </div>

        <div className="flex gap-4 items-start">
          <div className="flex-1 min-w-0">
            {isLoading ? (
              <div className="flex flex-col gap-3">
                <div className="h-4 w-3/4 rounded bg-[var(--surface)] animate-pulse" />
                <div className="h-3 w-full rounded bg-[var(--surface)] animate-pulse" />
                <div className="h-3 w-2/3 rounded bg-[var(--surface)] animate-pulse" />
              </div>
            ) : isError ? (
              <div className="text-xs text-[var(--text-muted)] leading-relaxed">
                Unable to load transits right now
              </div>
            ) : transits.length === 0 ? (
              <div className="text-xs text-[var(--text-muted)] leading-relaxed">
                No significant transits active
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {transits.slice(0, 3).map((t, i) => (
                  <div
                    key={`${t.transiting_planet}-${t.natal_planet}-${i}`}
                    className={i > 0 ? 'border-t pt-3' : ''}
                    style={i > 0 ? { borderColor: 'var(--border-divider)' } : undefined}
                  >
                    <div className="text-[13px] font-semibold text-[var(--text-primary)] mb-1">
                      {t.transiting_planet} {t.aspect_type} {t.natal_planet}
                      {t.intensity != null && (
                        <span className="ml-2 text-[10px] font-medium text-[var(--text-muted)]">
                          {typeof t.intensity === 'number'
                            ? `${Math.round(t.intensity * 100)}%`
                            : t.intensity}
                        </span>
                      )}
                    </div>
                    {t.description && (
                      <div className="text-xs text-[var(--text-body)] leading-relaxed">
                        {t.description}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Circular chart preview (CSS-only) */}
          <div
            className="relative w-20 h-20 rounded-full flex-shrink-0 flex items-center justify-center mt-1"
            style={{ border: '1.5px solid var(--border-strong)' }}
          >
            {/* Inner circle */}
            <div
              className="absolute w-[60%] h-[60%] rounded-full"
              style={{ border: '1px solid var(--border)' }}
            />
            {/* Planet dots */}
            <div
              className="absolute w-[5px] h-[5px] rounded-full"
              style={{
                top: '12%',
                left: '58%',
                background: 'var(--gold-bright)',
              }}
            />
            <div
              className="absolute w-[5px] h-[5px] rounded-full"
              style={{
                top: '38%',
                right: '8%',
                background: 'var(--blue)',
              }}
            />
            <div
              className="absolute w-[5px] h-[5px] rounded-full"
              style={{
                bottom: '20%',
                right: '18%',
                background: 'var(--red)',
              }}
            />
            <div
              className="absolute w-[5px] h-[5px] rounded-full"
              style={{
                bottom: '14%',
                left: '22%',
                background: 'var(--green)',
              }}
            />
            <span className="z-[1] text-[7px] font-semibold uppercase tracking-wider text-[var(--text-faint)]">
              Transit
            </span>
          </div>
        </div>
      </div>
    </WidgetCard>
  )
}
