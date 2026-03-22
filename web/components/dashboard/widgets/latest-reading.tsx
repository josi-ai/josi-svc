'use client'

import { WidgetCard } from './widget-card'

export default function LatestReading({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          Latest AI Reading
        </div>

        <div className="font-display text-[17px] text-[var(--text-primary)] mb-2 leading-snug">
          The Water Within
        </div>

        <p
          className="font-reading text-[13px] leading-[1.75] text-[var(--text-body-reading)] mb-2.5 line-clamp-2"
        >
          Your water-dominant chart speaks to a life guided by emotional
          intelligence and intuitive knowing. The Moon in Scorpio intensifies
          this pattern, creating depth in all your connections...
        </p>

        <div className="text-[10px] text-[var(--text-faint)] mb-2.5">
          Generated 2 days ago
        </div>

        <div className="flex gap-3">
          <span
            className="text-xs font-semibold cursor-pointer"
            style={{ color: 'var(--gold)' }}
          >
            Read more &rarr;
          </span>
          <span
            className="text-xs font-semibold cursor-pointer"
            style={{ color: 'var(--purple)' }}
          >
            Chat about this &rarr;
          </span>
        </div>
      </div>
    </WidgetCard>
  )
}
