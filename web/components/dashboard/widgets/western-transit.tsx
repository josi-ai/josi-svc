'use client'

import { WidgetCard } from './widget-card'

export default function WesternTransit({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="western" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3.5">
          Western Transit Alert
        </div>

        <div className="flex gap-4 items-start">
          <div className="flex-1 min-w-0">
            <div className="flex flex-col gap-3">
              {/* Transit 1 */}
              <div>
                <div className="text-[13px] font-semibold text-[var(--text-primary)] mb-1">
                  Mercury enters Aries in 3 days
                </div>
                <div className="text-xs text-[var(--text-body)] leading-relaxed">
                  Communication becomes more direct and assertive. Good for bold
                  conversations.
                </div>
              </div>

              {/* Divider + Transit 2 */}
              <div
                className="border-t pt-3"
                style={{ borderColor: 'var(--border-divider)' }}
              >
                <div className="text-[13px] font-semibold text-[var(--text-primary)] mb-1">
                  Venus conjunct your natal Mars
                </div>
                <div className="text-xs text-[var(--text-body)] leading-relaxed">
                  Passionate energy this week. Creative and romantic impulses are
                  heightened.
                </div>
              </div>
            </div>
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
            <span
              className="z-[1] text-[7px] font-semibold uppercase tracking-wider text-[var(--text-faint)]"
            >
              Transit
            </span>
          </div>
        </div>
      </div>
    </WidgetCard>
  )
}
