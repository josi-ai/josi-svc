'use client';

import { useMemo } from 'react';
import { X } from 'lucide-react';
import {
  type WidgetType,
  widgetCatalog,
  TRADITION_COLORS,
} from '@/config/widget-config';

interface AddWidgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (type: WidgetType) => void;
  activeWidgets: WidgetType[];
}

export function AddWidgetModal({
  isOpen,
  onClose,
  onAdd,
  activeWidgets,
}: AddWidgetModalProps) {
  const grouped = useMemo(() => {
    const map = new Map<string, typeof widgetCatalog>();
    for (const w of widgetCatalog) {
      const list = map.get(w.category) ?? [];
      list.push(w);
      map.set(w.category, list);
    }
    return map;
  }, []);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="mt-24 w-full max-w-lg rounded-2xl border border-border bg-card p-6 shadow-dropdown overflow-y-auto max-h-[calc(100vh-8rem)]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-display text-display-sm text-text-primary">
            Add Widget
          </h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-surface text-text-muted transition-colors hover:bg-card-hover hover:text-text-primary"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Categories */}
        {Array.from(grouped.entries()).map(([category, widgets]) => (
          <div key={category} className="mb-6 last:mb-2">
            <div className="mb-3 border-b border-border-subtle pb-1.5 text-label font-bold uppercase tracking-widest text-text-faint">
              {category}
            </div>

            <div className="space-y-1">
              {widgets.map((w) => {
                const isActive = activeWidgets.includes(w.type);
                const colors = TRADITION_COLORS[w.tradition];

                return (
                  <div
                    key={w.type}
                    className="flex items-center gap-3.5 rounded-xl p-2.5 transition-colors hover:bg-card-hover"
                  >
                    {/* Icon */}
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-border-subtle bg-surface text-base">
                      {w.icon}
                    </div>

                    {/* Text */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[13px] font-semibold text-text-primary">
                          {w.label}
                        </span>
                        <span
                          className="inline-block rounded px-1.5 py-0.5 text-caption font-bold uppercase tracking-wide"
                          style={{
                            background: colors.bg,
                            color: colors.text,
                          }}
                        >
                          {w.tradition}
                        </span>
                      </div>
                      <div className="text-[11px] leading-snug text-text-muted">
                        {w.description}
                      </div>
                    </div>

                    {/* Add / Added button */}
                    {isActive ? (
                      <span className="shrink-0 rounded-md px-3 py-1 text-[11px] font-semibold text-text-faint">
                        Added &#10003;
                      </span>
                    ) : (
                      <button
                        onClick={() => onAdd(w.type)}
                        className="shrink-0 rounded-md border border-border px-3 py-1 text-[11px] font-semibold text-text-secondary transition-colors hover:border-gold hover:bg-gold hover:text-white"
                      >
                        Add
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
