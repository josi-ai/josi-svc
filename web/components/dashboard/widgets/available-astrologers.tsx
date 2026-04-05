'use client'

import Link from 'next/link'
import { WidgetCard } from './widget-card'

export default function AvailableAstrologers({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="general" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          Available Astrologers
        </div>
        <div className="text-xs text-[var(--text-muted)] leading-relaxed mb-3">
          No astrologers available yet — check back soon
        </div>
        <Link
          href="/astrologers"
          className="text-xs font-semibold"
          style={{ color: 'var(--gold)' }}
        >
          View all astrologers &rarr;
        </Link>
      </div>
    </WidgetCard>
  )
}
