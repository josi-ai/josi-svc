'use client'

import { WidgetCard } from './widget-card'

export default function TodaysSky({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div
        className="p-7 relative overflow-hidden"
        style={{ background: 'var(--hero-gradient)', borderRadius: 'inherit' }}
      >
        {/* Subtle gold glow */}
        <div
          className="absolute -top-16 -right-10 w-48 h-48 rounded-full"
          style={{
            background:
              'radial-gradient(circle, rgba(200,145,58,0.06) 0%, transparent 70%)',
          }}
        />
        {/* Secondary blue glow */}
        <div
          className="absolute -bottom-10 left-[30%] w-40 h-40 rounded-full"
          style={{
            background:
              'radial-gradient(circle, rgba(106,159,216,0.03) 0%, transparent 60%)',
          }}
        />
        <div className="relative">
          <div
            className="text-[10px] uppercase tracking-[2.5px] font-semibold mb-3"
            style={{ color: 'var(--gold-bright)' }}
          >
            Today&apos;s Sky
          </div>
          <h2 className="font-display text-[28px] text-[var(--text-primary)] mb-2 leading-tight">
            Shukla Chaturthi in Rohini
          </h2>
          <p className="font-reading text-[15px] leading-relaxed text-[var(--text-body)] mb-5 max-w-xl">
            The Moon transits through Taurus in Rohini nakshatra. A day of
            nurturing abundance &mdash; creative and material pursuits are
            strongly favored.
          </p>
          <div className="flex gap-2 flex-wrap">
            <span
              className="text-[11px] font-medium px-3 py-1 rounded-full"
              style={{
                background: 'var(--gold-bg)',
                color: 'var(--gold-bright)',
              }}
            >
              Shubh Muhurta
            </span>
            <span
              className="text-[11px] font-medium px-3 py-1 rounded-full"
              style={{ background: 'var(--blue-bg)', color: 'var(--blue)' }}
            >
              Moon in Taurus
            </span>
            <span
              className="text-[11px] font-medium px-3 py-1 rounded-full"
              style={{ background: 'var(--green-bg)', color: 'var(--green)' }}
            >
              Wednesday &middot; Mercury
            </span>
          </div>
        </div>
      </div>
    </WidgetCard>
  )
}
