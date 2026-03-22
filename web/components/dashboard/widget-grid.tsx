'use client';

import { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Plus } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import {
  type WidgetType,
  type WidgetInstance,
  type WidgetSize,
  widgetCatalog,
  defaultWidgets,
} from '@/config/widget-config';
import { AddWidgetModal } from './add-widget-modal';

const STORAGE_KEY = 'josi-dashboard-widgets';

export interface WidgetComponentProps {
  onRemove: () => void;
}

/* ------------------------------------------------------------------
 * Dynamic widget component map
 * Each widget file is loaded on demand via next/dynamic.
 * Another agent owns the actual widget component files — this map
 * simply points at them.
 * ------------------------------------------------------------------ */
const widgetComponents: Record<
  WidgetType,
  React.ComponentType<WidgetComponentProps>
> = {
  'todays-sky': dynamic(() => import('./widgets/todays-sky')),
  'chart-quick-view': dynamic(() => import('./widgets/chart-quick-view')),
  'current-dasha': dynamic(() => import('./widgets/current-dasha')),
  'ai-chat-access': dynamic(() => import('./widgets/ai-chat-access')),
  'muhurta-timeline': dynamic(() => import('./widgets/muhurta-timeline')),
  'western-transit': dynamic(() => import('./widgets/western-transit')),
  'latest-reading': dynamic(() => import('./widgets/latest-reading')),
  'available-astrologers': dynamic(
    () => import('./widgets/available-astrologers'),
  ),
  'bazi-summary': dynamic(() => import('./widgets/bazi-summary')),
};

/* ------------------------------------------------------------------
 * Size → Tailwind grid-column class mapping
 * ------------------------------------------------------------------ */
const sizeClasses: Record<WidgetSize, string> = {
  full: 'col-span-1 md:col-span-2 lg:col-span-3',
  half: 'col-span-1 md:col-span-2 lg:col-span-2',
  third: 'col-span-1',
};

/* ------------------------------------------------------------------
 * localStorage helpers
 * ------------------------------------------------------------------ */
function loadWidgets(): WidgetInstance[] {
  if (typeof window === 'undefined') return defaultWidgets;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as WidgetInstance[];
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch {
    // corrupted data — fall back to defaults
  }
  return defaultWidgets;
}

function saveWidgets(widgets: WidgetInstance[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(widgets));
  } catch {
    // localStorage might be full or unavailable — silently ignore
  }
}

/* ------------------------------------------------------------------
 * WidgetGrid component
 * ------------------------------------------------------------------ */
export function WidgetGrid() {
  const [widgets, setWidgets] = useState<WidgetInstance[]>(defaultWidgets);
  const [modalOpen, setModalOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const { user } = useAuth();

  const displayName = user?.full_name || user?.email || 'User';
  const now = new Date();
  const hour = now.getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  // Load from localStorage after mount (avoids SSR mismatch)
  useEffect(() => {
    setWidgets(loadWidgets());
    setMounted(true);
  }, []);

  // Persist whenever widgets change (skip initial default render)
  useEffect(() => {
    if (mounted) saveWidgets(widgets);
  }, [widgets, mounted]);

  const addWidget = useCallback(
    (type: WidgetType) => {
      const def = widgetCatalog.find((w) => w.type === type);
      if (!def) return;

      const id = `w-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      setWidgets((prev) => [
        ...prev,
        { id, type, size: def.defaultSize },
      ]);
    },
    [],
  );

  const removeWidget = useCallback((id: string) => {
    setWidgets((prev) => prev.filter((w) => w.id !== id));
  }, []);

  const activeTypes = widgets.map((w) => w.type);

  return (
    <div>
      {/* Header row */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            {greeting}, <strong style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{displayName}</strong>
          </p>
          <h2 className="font-display mt-1" style={{ fontSize: '1.75rem', color: 'var(--text-primary)' }}>
            {dateStr}
          </h2>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg font-semibold text-sm hover:opacity-90 transition-opacity"
          style={{ background: 'var(--gold)', color: 'var(--btn-add-text)' }}
        >
          <Plus className="h-3.5 w-3.5" />
          Add Widget
        </button>
      </div>

      {/* Widget grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {widgets.map((instance) => {
          const Component = widgetComponents[instance.type];
          if (!Component) return null;

          return (
            <div key={instance.id} className={sizeClasses[instance.size]}>
              <Component onRemove={() => removeWidget(instance.id)} />
            </div>
          );
        })}
      </div>

      {/* Add Widget modal */}
      <AddWidgetModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onAdd={(type) => {
          addWidget(type);
          setModalOpen(false);
        }}
        activeWidgets={activeTypes}
      />
    </div>
  );
}
