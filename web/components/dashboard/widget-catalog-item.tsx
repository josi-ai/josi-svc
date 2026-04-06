'use client';

import { Check } from 'lucide-react';
import { type WidgetType, type TraditionBadge, TRADITION_COLORS } from '@/config/widget-config';

interface WidgetCatalogItemProps {
  type: WidgetType;
  label: string;
  description: string;
  previewDescription: string;
  icon: string;
  tradition: TraditionBadge;
  isActive: boolean;
  onAdd: () => void;
}

export function WidgetCatalogItem({
  label, previewDescription, icon, tradition, isActive, onAdd,
}: WidgetCatalogItemProps) {
  const colors = TRADITION_COLORS[tradition];

  return (
    <div
      className="rounded-xl p-3 transition-all duration-150"
      style={{ background: isActive ? 'rgba(48, 164, 108, 0.04)' : 'transparent' }}
      onMouseEnter={(e) => {
        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'var(--card-hover)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.background = isActive ? 'rgba(48, 164, 108, 0.04)' : 'transparent';
      }}
    >
      <div className="flex items-start gap-3.5">
        {/* Icon */}
        <div
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg"
          style={{ background: 'var(--surface)', border: '1px solid var(--border-subtle)' }}
        >
          {icon}
        </div>

        {/* Text */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              {label}
            </span>
            <span
              className="inline-block rounded px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide"
              style={{ background: colors.bg, color: colors.text }}
            >
              {tradition}
            </span>
            {isActive && (
              <span
                className="inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide"
                style={{ background: 'rgba(48, 164, 108, 0.1)', color: 'var(--green)' }}
              >
                <Check className="h-2.5 w-2.5" />
                Active
              </span>
            )}
          </div>
          <div className="mt-0.5 text-[11px] leading-relaxed" style={{ color: 'var(--text-muted)' }}>
            {previewDescription}
          </div>
        </div>

        {/* Add / Added button */}
        <div className="shrink-0 pt-0.5">
          {isActive ? (
            <span className="inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-[11px] font-semibold" style={{ color: 'var(--text-faint)' }}>
              Added
            </span>
          ) : (
            <button
              onClick={onAdd}
              className="rounded-md px-3 py-1.5 text-[11px] font-semibold transition-all duration-150"
              style={{ border: '1px solid var(--border)', color: 'var(--text-secondary)', background: 'transparent' }}
              onMouseEnter={(e) => {
                const btn = e.currentTarget as HTMLElement;
                btn.style.borderColor = 'var(--gold)';
                btn.style.background = 'var(--gold)';
                btn.style.color = '#fff';
              }}
              onMouseLeave={(e) => {
                const btn = e.currentTarget as HTMLElement;
                btn.style.borderColor = 'var(--border)';
                btn.style.background = 'transparent';
                btn.style.color = 'var(--text-secondary)';
              }}
            >
              + Add
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
