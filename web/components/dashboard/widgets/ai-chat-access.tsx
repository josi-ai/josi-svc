'use client'

import { WidgetCard } from './widget-card'

export default function AiChatAccess({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="ai" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          AI Chat
        </div>

        {/* Avatar + label */}
        <div className="flex gap-3 items-center mb-3.5">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center text-xl flex-shrink-0"
            style={{
              background: 'var(--avatar-gradient)',
              color: 'var(--avatar-text)',
            }}
          >
            &#10022;
          </div>
          <div>
            <div className="text-[13px] font-semibold text-[var(--text-primary)] mb-0.5">
              Ask Josi AI
            </div>
            <div className="text-[11px] text-[var(--text-muted)]">
              About your chart, transits, or anything
            </div>
          </div>
        </div>

        {/* Faux input */}
        <div
          className="w-full py-2 px-3.5 rounded-lg text-xs border cursor-text"
          style={{
            background: 'var(--surface)',
            borderColor: 'var(--border)',
            color: 'var(--text-faint)',
          }}
        >
          What would you like to explore?
        </div>

        {/* Suggestion chips */}
        <div className="flex gap-1.5 mt-2.5 flex-wrap">
          <span
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-[11px] font-medium cursor-pointer transition-colors border"
            style={{
              background: 'var(--surface)',
              borderColor: 'var(--border)',
              color: 'var(--text-secondary)',
            }}
          >
            Career outlook
          </span>
          <span
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-[11px] font-medium cursor-pointer transition-colors border"
            style={{
              background: 'var(--surface)',
              borderColor: 'var(--border)',
              color: 'var(--text-secondary)',
            }}
          >
            Current transits
          </span>
        </div>
      </div>
    </WidgetCard>
  )
}
