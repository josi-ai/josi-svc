'use client'

import { WidgetCard } from './widget-card'

const PILLARS: Array<{
  label: string
  stem: string
  branch: string
  element: string
  animal: string
}> = [
  { label: 'Year', stem: '\u58EC', branch: '\u7533', element: 'Water', animal: 'Monkey' },
  { label: 'Month', stem: '\u7678', branch: '\u536F', element: 'Water', animal: 'Rabbit' },
  { label: 'Day', stem: '\u4E19', branch: '\u5348', element: 'Fire', animal: 'Horse' },
  { label: 'Hour', stem: '\u7532', branch: '\u5348', element: 'Earth', animal: 'Snake' },
]

export default function BaziSummary({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="chinese" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          BaZi Summary
        </div>

        <div className="font-display text-[15px] text-[var(--text-primary)] mb-2.5">
          Day Master: Yang Fire ({'\u4E19'})
        </div>

        {/* Four Pillars grid */}
        <div className="grid grid-cols-4 gap-1">
          {PILLARS.map((p) => (
            <div
              key={p.label}
              className="text-center py-1.5 px-1 rounded-md border"
              style={{
                background: 'var(--surface)',
                borderColor: 'var(--border-subtle)',
              }}
            >
              <div className="text-[8px] uppercase tracking-[0.5px] text-[var(--text-faint)] mb-0.5">
                {p.label}
              </div>
              <div className="text-sm mb-px">{p.stem}</div>
              <div className="text-[9px] font-medium text-[var(--text-primary)]">
                {p.element}
              </div>
              <div className="text-[8px] text-[var(--text-muted)]">
                {p.animal}
              </div>
            </div>
          ))}
        </div>

        <div className="text-[11px] text-[var(--text-muted)] mt-2.5 leading-relaxed">
          Strong fire element this month
        </div>
      </div>
    </WidgetCard>
  )
}
