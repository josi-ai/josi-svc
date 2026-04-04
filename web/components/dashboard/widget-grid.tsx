'use client';

import { useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Responsive, WidthProvider } from 'react-grid-layout';
import { Plus, GripVertical } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { type WidgetType } from '@/config/widget-config';
import { useWidgetLayout } from '@/hooks/use-widget-layout';
import { AddWidgetModal } from './add-widget-modal';

import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

export interface WidgetComponentProps {
  onRemove: () => void;
}

/* ------------------------------------------------------------------
 * Dynamic widget component map
 * Each widget file is loaded on demand via next/dynamic.
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
 * Grid configuration
 * ------------------------------------------------------------------ */
const BREAKPOINTS = { lg: 1200, md: 996, sm: 768, xs: 480 };
const COLS = { lg: 3, md: 2, sm: 1, xs: 1 };
const ROW_HEIGHT = 120;
const MARGIN: [number, number] = [16, 16];

/* ------------------------------------------------------------------
 * WidgetGrid component
 * ------------------------------------------------------------------ */
export function WidgetGrid() {
  const [modalOpen, setModalOpen] = useState(false);
  const { user } = useAuth();
  const {
    widgets,
    layouts,
    mounted,
    addWidget,
    removeWidget,
    onLayoutChange,
  } = useWidgetLayout();

  const displayName = user?.full_name || user?.email || 'User';
  const now = new Date();
  const hour = now.getHours();
  const greeting =
    hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const dateStr = now.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  const activeTypes = useMemo(() => widgets.map((w) => w.type), [widgets]);

  return (
    <div>
      {/* Header row */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            {greeting},{' '}
            <strong
              style={{ color: 'var(--text-primary)', fontWeight: 600 }}
            >
              {displayName}
            </strong>
          </p>
          <h2
            className="font-display mt-1"
            style={{ fontSize: '1.75rem', color: 'var(--text-primary)' }}
          >
            {dateStr}
          </h2>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg font-semibold text-sm hover:opacity-90 transition-opacity"
          style={{
            background: 'var(--gold)',
            color: 'var(--btn-add-text)',
          }}
        >
          <Plus className="h-3.5 w-3.5" />
          Add Widget
        </button>
      </div>

      {/* Widget grid — react-grid-layout */}
      {mounted && (
        <ResponsiveGridLayout
          className="widget-grid-layout"
          layouts={layouts}
          breakpoints={BREAKPOINTS}
          cols={COLS}
          rowHeight={ROW_HEIGHT}
          margin={MARGIN}
          containerPadding={[0, 0]}
          draggableHandle=".widget-drag-handle"
          onLayoutChange={onLayoutChange}
          isResizable={true}
          resizeHandles={['se']}
          useCSSTransforms={true}
          compactType="vertical"
        >
          {widgets.map((instance) => {
            const Component = widgetComponents[instance.type];
            if (!Component) return null;

            return (
              <div key={instance.id} className="widget-grid-item">
                {/* Drag handle */}
                <div className="widget-drag-handle">
                  <GripVertical className="h-4 w-4" />
                </div>
                <Component onRemove={() => removeWidget(instance.id)} />
              </div>
            );
          })}
        </ResponsiveGridLayout>
      )}

      {/* Fallback while not mounted (SSR / loading) */}
      {!mounted && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-[180px] rounded-2xl animate-pulse"
              style={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
              }}
            />
          ))}
        </div>
      )}

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

      {/* Scoped styles for grid items */}
      <style jsx global>{`
        .widget-grid-layout {
          position: relative;
        }
        .widget-grid-item {
          position: relative;
        }
        .widget-grid-item > :last-child {
          height: 100%;
        }
        /* Ensure widget cards fill their grid cell */
        .widget-grid-item > :last-child > div {
          height: 100%;
        }
        .widget-drag-handle {
          position: absolute;
          top: 10px;
          left: 10px;
          z-index: 20;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          border-radius: 6px;
          color: var(--text-faint);
          cursor: grab;
          opacity: 0;
          transition: opacity 0.15s ease, background 0.15s ease, color 0.15s ease;
        }
        .widget-grid-item:hover .widget-drag-handle {
          opacity: 1;
        }
        .widget-drag-handle:hover {
          background: var(--border);
          color: var(--text-secondary);
        }
        .widget-drag-handle:active {
          cursor: grabbing;
        }
        /* While dragging, highlight the item */
        .react-grid-item.react-draggable-dragging {
          z-index: 100;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
          border-radius: 16px;
          opacity: 0.9;
        }
        /* Placeholder shown where the item will land */
        .react-grid-placeholder {
          background: var(--gold) !important;
          opacity: 0.08 !important;
          border-radius: 16px;
          border: 2px dashed var(--gold) !important;
        }
        /* Resize handle styling */
        .react-grid-item > .react-resizable-handle {
          position: absolute;
          width: 20px;
          height: 20px;
          bottom: 4px;
          right: 4px;
          cursor: se-resize;
          opacity: 0;
          transition: opacity 0.15s;
        }
        .react-grid-item:hover > .react-resizable-handle {
          opacity: 0.5;
        }
        .react-grid-item > .react-resizable-handle::after {
          content: '';
          position: absolute;
          right: 4px;
          bottom: 4px;
          width: 8px;
          height: 8px;
          border-right: 2px solid var(--text-faint);
          border-bottom: 2px solid var(--text-faint);
          border-radius: 0 0 2px 0;
        }
        /* While resizing */
        .react-grid-item.resizing {
          z-index: 100;
          opacity: 0.9;
        }
        /* Widget content should overflow properly when resized */
        .widget-grid-item > :last-child {
          height: 100%;
          overflow: auto;
        }
        .widget-grid-item > :last-child > div {
          height: 100%;
          min-height: 100%;
        }
      `}</style>
    </div>
  );
}
