'use client'

import { X } from 'lucide-react'
import { type TraditionBadge, TRADITION_COLORS } from '@/config/widget-config'

interface WidgetCardProps {
  tradition: TraditionBadge
  onRemove: () => void
  children: React.ReactNode
  className?: string
}

export function WidgetCard({ tradition, onRemove, children, className }: WidgetCardProps) {
  const colors = TRADITION_COLORS[tradition]
  return (
    <div
      className={`group relative bg-[var(--card)] border border-[var(--border)] rounded-2xl transition-colors ${className || ''}`}
      style={{ boxShadow: 'var(--shadow-card)', height: '100%', display: 'flex', flexDirection: 'column' }}
    >
      {/* Tradition badge */}
      <span
        className="absolute top-3 right-3 text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded z-10"
        style={{ background: colors.bg, color: colors.text }}
      >
        {tradition}
      </span>
      {/* Remove button */}
      <button
        onClick={onRemove}
        className="absolute top-3 right-16 opacity-0 group-hover:opacity-100 transition-opacity w-5 h-5 rounded flex items-center justify-center text-[var(--text-faint)] hover:text-[var(--red)] hover:bg-[var(--red-bg)] z-10"
      >
        <X size={12} />
      </button>
      <div style={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
        {children}
      </div>
    </div>
  )
}
