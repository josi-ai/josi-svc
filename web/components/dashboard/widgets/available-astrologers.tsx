'use client'

import { WidgetCard } from './widget-card'

export default function AvailableAstrologers({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="general" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          Available Astrologers
        </div>

        {/* Astrologer mini card */}
        <div className="flex gap-3 items-center mb-3">
          {/* Avatar */}
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center font-display text-[15px] text-[var(--text-primary)] flex-shrink-0"
            style={{ background: 'var(--avatar-placeholder)' }}
          >
            P
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-[var(--text-primary)] mb-px">
              Priya Shankar
            </div>
            <div className="text-[10px] text-[var(--text-muted)]">
              Vedic &middot; 15 years
            </div>
            <div
              className="text-[9px] font-medium mt-0.5"
              style={{ color: 'var(--green)' }}
            >
              &#9679; Available now
            </div>
          </div>

          {/* Book button */}
          <button
            className="px-3.5 py-1.5 rounded-lg text-[11px] font-semibold text-white border-none cursor-pointer flex-shrink-0"
            style={{ background: 'var(--gold)' }}
          >
            Book
          </button>
        </div>

        <div
          className="text-xs font-semibold cursor-pointer"
          style={{ color: 'var(--gold)' }}
        >
          View all astrologers &rarr;
        </div>
      </div>
    </WidgetCard>
  )
}
