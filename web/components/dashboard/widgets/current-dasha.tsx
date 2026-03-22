'use client'

import { WidgetCard } from './widget-card'

export default function CurrentDasha({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          Current Dasha
        </div>

        <div className="font-display text-base text-[var(--text-primary)] mb-1">
          Venus Maha Dasha
        </div>
        <div className="text-xs text-[var(--text-secondary)] mb-1">
          Saturn Antar Dasha
        </div>

        {/* Progress bar */}
        <div className="w-full h-1.5 rounded-full bg-[var(--border-subtle)] overflow-hidden my-2">
          <div
            className="h-full rounded-full"
            style={{ width: '35%', background: 'var(--gold-bright)' }}
          />
        </div>

        <div className="flex justify-between items-center">
          <span className="text-[11px] text-[var(--text-faint)]">
            35% elapsed
          </span>
          <span className="text-[11px] text-[var(--text-muted)]">
            Until March 2027
          </span>
        </div>

        <div
          className="text-xs font-semibold mt-3 cursor-pointer"
          style={{ color: 'var(--gold)' }}
        >
          Chat about this &rarr;
        </div>
      </div>
    </WidgetCard>
  )
}
