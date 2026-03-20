'use client';

import { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
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
          <h3 className="font-display text-display-md text-text-primary mb-1">
            Dashboard
          </h3>
          <p className="text-sm text-text-muted">
            Your personalized cosmic command center
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => setModalOpen(true)}
          className="border-gold text-gold-bright hover:bg-[rgba(200,145,58,0.08)]"
        >
          <Plus className="h-4 w-4" />
          Add Widget
        </Button>
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
