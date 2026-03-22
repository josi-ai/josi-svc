'use client'

import { WidgetCard } from './widget-card'

const SEGMENTS: Array<{ flex: number; color: string; hasMarker?: boolean }> = [
  { flex: 2, color: 'var(--bar-good)' },
  { flex: 2, color: 'var(--bar-avoid)' },
  { flex: 1.5, color: 'var(--bar-good)' },
  { flex: 1.5, color: 'var(--bar-special)', hasMarker: true },
  { flex: 1, color: 'var(--bar-special)' },
  { flex: 2, color: 'var(--bar-good)' },
  { flex: 1.5, color: 'var(--bar-avoid)' },
  { flex: 1.5, color: 'var(--bar-neutral)' },
  { flex: 2, color: 'var(--bar-good)' },
]

const TIME_LABELS = ['6 AM', '8 AM', '10 AM', '12 PM', '2 PM', '4 PM', '6 PM']

const LEGEND: Array<{ label: string; color: string }> = [
  { label: 'Good', color: 'var(--bar-good)' },
  { label: 'Rahu', color: 'var(--bar-avoid)' },
  { label: 'Shubh', color: 'var(--bar-special)' },
  { label: 'Neutral', color: 'var(--bar-neutral)' },
]

export default function MuhurtaTimeline({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3.5">
          Muhurta Timeline
        </div>

        {/* Color-coded time bar */}
        <div
          className="flex h-7 rounded-md overflow-hidden border border-[var(--border)] mb-2 relative"
        >
          {SEGMENTS.map((seg, i) => (
            <div
              key={i}
              className="relative"
              style={{ flex: seg.flex, background: seg.color }}
            >
              {seg.hasMarker && (
                <div
                  className="absolute top-[-4px] w-0.5 h-9 z-[2]"
                  style={{
                    left: '40%',
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
          ))}
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
                style={{ background: item.color }}
              />
              <span className="text-[10px] text-[var(--text-muted)]">
                {item.label}
              </span>
            </div>
          ))}
        </div>

        {/* Rahu Kalam warning */}
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
            &#9888; Rahu Kalam: 12:00 - 1:30 PM
          </div>
          <div className="text-[10px] text-[var(--text-muted)] mt-0.5">
            Avoid starting new ventures during this period
          </div>
        </div>
      </div>
    </WidgetCard>
  )
}
