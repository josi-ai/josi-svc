'use client';

import { useMemo, useState, useEffect, useRef } from 'react';
import { X, Search, Check } from 'lucide-react';
import {
  type WidgetType,
  widgetCatalog,
  TRADITION_COLORS,
  WIDGET_CATEGORIES,
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
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Reset search when modal opens
  useEffect(() => {
    if (isOpen) {
      setSearch('');
      setSelectedCategory(null);
      // Focus the search input after the transition
      setTimeout(() => searchInputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Filter widgets by search and category
  const filteredWidgets = useMemo(() => {
    const q = search.toLowerCase().trim();
    return widgetCatalog.filter((w) => {
      const matchesSearch =
        !q ||
        w.label.toLowerCase().includes(q) ||
        w.description.toLowerCase().includes(q) ||
        w.tradition.toLowerCase().includes(q) ||
        w.category.toLowerCase().includes(q);
      const matchesCategory = !selectedCategory || w.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [search, selectedCategory]);

  // Group filtered widgets by category (ordered)
  const grouped = useMemo(() => {
    const map = new Map<string, typeof widgetCatalog>();
    for (const category of WIDGET_CATEGORIES) {
      const items = filteredWidgets.filter((w) => w.category === category);
      if (items.length > 0) map.set(category, items);
    }
    // Also include any categories not in the ordered list
    for (const w of filteredWidgets) {
      if (!WIDGET_CATEGORIES.includes(w.category as any)) {
        const list = map.get(w.category) ?? [];
        if (!list.includes(w)) list.push(w);
        map.set(w.category, list);
      }
    }
    return map;
  }, [filteredWidgets]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center animate-in fade-in duration-150"
      style={{ background: 'rgba(0, 0, 0, 0.4)', backdropFilter: 'blur(4px)' }}
      onClick={onClose}
    >
      <div
        className="mt-20 w-full max-w-lg rounded-2xl border overflow-hidden animate-in slide-in-from-top-4 duration-200"
        style={{
          background: 'var(--card)',
          borderColor: 'var(--border)',
          boxShadow: '0 24px 48px rgba(0,0,0,0.3)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 pt-6 pb-4"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          <div>
            <h2
              className="font-display"
              style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}
            >
              Add Widget
            </h2>
            <p
              className="mt-0.5"
              style={{ fontSize: '12px', color: 'var(--text-muted)' }}
            >
              Customize your dashboard with widgets from any tradition
            </p>
          </div>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg transition-colors"
            style={{
              border: '1px solid var(--border)',
              background: 'var(--surface)',
              color: 'var(--text-muted)',
            }}
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Search */}
        <div className="px-6 pt-4 pb-3">
          <div
            className="flex items-center gap-2 rounded-lg px-3 py-2"
            style={{
              background: 'var(--background)',
              border: '1px solid var(--border)',
            }}
          >
            <Search
              className="h-3.5 w-3.5 shrink-0"
              style={{ color: 'var(--text-faint)' }}
            />
            <input
              ref={searchInputRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search widgets..."
              className="flex-1 bg-transparent text-sm outline-none"
              style={{
                color: 'var(--text-primary)',
                caretColor: 'var(--gold)',
              }}
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="flex h-5 w-5 items-center justify-center rounded"
                style={{ color: 'var(--text-faint)' }}
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </div>
        </div>

        {/* Category filter pills */}
        <div className="px-6 pb-3 flex gap-2 overflow-x-auto">
          <button
            onClick={() => setSelectedCategory(null)}
            className="shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-all"
            style={{
              background: !selectedCategory
                ? 'var(--gold-bg)'
                : 'var(--background)',
              color: !selectedCategory
                ? 'var(--gold-bright)'
                : 'var(--text-muted)',
              border: `1px solid ${
                !selectedCategory ? 'var(--gold)' : 'var(--border)'
              }`,
              borderColor: !selectedCategory
                ? 'rgba(200,145,58,0.3)'
                : 'var(--border)',
            }}
          >
            All
          </button>
          {WIDGET_CATEGORIES.map((cat) => {
            const isActive = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() =>
                  setSelectedCategory(isActive ? null : cat)
                }
                className="shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-all"
                style={{
                  background: isActive
                    ? 'var(--gold-bg)'
                    : 'var(--background)',
                  color: isActive
                    ? 'var(--gold-bright)'
                    : 'var(--text-muted)',
                  border: `1px solid ${
                    isActive ? 'rgba(200,145,58,0.3)' : 'var(--border)'
                  }`,
                }}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* Widget list */}
        <div
          className="px-6 pb-6 overflow-y-auto"
          style={{ maxHeight: 'calc(100vh - 20rem)' }}
        >
          {grouped.size === 0 && (
            <div className="py-8 text-center">
              <p
                className="text-sm"
                style={{ color: 'var(--text-muted)' }}
              >
                No widgets match your search.
              </p>
            </div>
          )}

          {Array.from(grouped.entries()).map(([category, widgets]) => (
            <div key={category} className="mb-5 last:mb-2">
              <div
                className="mb-2.5 pb-1.5 text-[10px] font-bold uppercase tracking-[2px]"
                style={{
                  color: 'var(--text-faint)',
                  borderBottom: '1px solid var(--border-subtle)',
                }}
              >
                {category}
              </div>

              <div className="space-y-1">
                {widgets.map((w) => {
                  const isActive = activeWidgets.includes(w.type);
                  const colors = TRADITION_COLORS[w.tradition];

                  return (
                    <div
                      key={w.type}
                      className="rounded-xl p-3 transition-all duration-150"
                      style={{
                        background: isActive
                          ? 'rgba(48, 164, 108, 0.04)'
                          : 'transparent',
                      }}
                      onMouseEnter={(e) => {
                        if (!isActive)
                          (e.currentTarget as HTMLElement).style.background =
                            'var(--card-hover)';
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.background =
                          isActive
                            ? 'rgba(48, 164, 108, 0.04)'
                            : 'transparent';
                      }}
                    >
                      <div className="flex items-start gap-3.5">
                        {/* Icon */}
                        <div
                          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg"
                          style={{
                            background: 'var(--surface)',
                            border: '1px solid var(--border-subtle)',
                          }}
                        >
                          {w.icon}
                        </div>

                        {/* Text */}
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span
                              className="text-[13px] font-semibold"
                              style={{ color: 'var(--text-primary)' }}
                            >
                              {w.label}
                            </span>
                            <span
                              className="inline-block rounded px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide"
                              style={{
                                background: colors.bg,
                                color: colors.text,
                              }}
                            >
                              {w.tradition}
                            </span>
                            {isActive && (
                              <span
                                className="inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide"
                                style={{
                                  background: 'rgba(48, 164, 108, 0.1)',
                                  color: '#30A46C',
                                }}
                              >
                                <Check className="h-2.5 w-2.5" />
                                Active
                              </span>
                            )}
                          </div>
                          <div
                            className="mt-0.5 text-[11px] leading-relaxed"
                            style={{ color: 'var(--text-muted)' }}
                          >
                            {w.previewDescription}
                          </div>
                        </div>

                        {/* Add / Added button */}
                        <div className="shrink-0 pt-0.5">
                          {isActive ? (
                            <span
                              className="inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-[11px] font-semibold"
                              style={{ color: 'var(--text-faint)' }}
                            >
                              Added
                            </span>
                          ) : (
                            <button
                              onClick={() => onAdd(w.type)}
                              className="rounded-md px-3 py-1.5 text-[11px] font-semibold transition-all duration-150"
                              style={{
                                border: '1px solid var(--border)',
                                color: 'var(--text-secondary)',
                                background: 'transparent',
                              }}
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
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
