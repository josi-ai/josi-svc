import { z } from 'zod';
import { type Layouts } from 'react-grid-layout';
import {
  loadFromStorage,
  saveToStorage,
  removeFromStorage,
  widgetInstanceArraySchema,
  layoutsSchema,
} from '@/lib/storage';
import {
  type WidgetInstance,
  defaultWidgets,
  buildLayoutFromWidgets,
} from '@/config/widget-config';

/* ---------- Constants ---------- */

export const STORAGE_KEY = 'josi-dashboard-widgets';
export const LAYOUT_STORAGE_KEY = 'josi-dashboard-layouts';
export const VERSION_KEY = 'josi-dashboard-version';
export const CURRENT_VERSION = '3'; // Bump this to invalidate stale localStorage
export const DEBOUNCE_MS = 1000;

export const BREAKPOINT_COLS: Record<string, number> = {
  lg: 3,
  md: 2,
  sm: 1,
  xs: 1,
};

/* ---------- Types ---------- */

export interface DashboardPreferences {
  widget_layout?: Layouts | null;
  active_widgets?: WidgetInstance[] | null;
}

export interface UserPreferences {
  dashboard?: DashboardPreferences;
  [key: string]: unknown;
}

/* ---------- localStorage helpers ---------- */

export function loadLocalWidgets(): WidgetInstance[] {
  if (typeof window === 'undefined') return defaultWidgets;
  const savedVersion = loadFromStorage(VERSION_KEY, z.string(), '');
  if (savedVersion !== CURRENT_VERSION) {
    removeFromStorage(STORAGE_KEY);
    removeFromStorage(LAYOUT_STORAGE_KEY);
    saveToStorage(VERSION_KEY, CURRENT_VERSION);
    return defaultWidgets;
  }
  const widgets = loadFromStorage(STORAGE_KEY, widgetInstanceArraySchema, []);
  return widgets.length > 0 ? (widgets as WidgetInstance[]) : defaultWidgets;
}

export function loadLocalLayouts(): Layouts | null {
  if (typeof window === 'undefined') return null;
  const layouts = loadFromStorage(LAYOUT_STORAGE_KEY, layoutsSchema, null);
  return layouts as Layouts | null;
}

export function saveLocal(widgets: WidgetInstance[], layouts: Layouts) {
  saveToStorage(STORAGE_KEY, widgets);
  saveToStorage(LAYOUT_STORAGE_KEY, layouts);
}

/* ---------- Default layouts builder ---------- */

export function buildDefaultLayouts(widgets: WidgetInstance[]): Layouts {
  const layouts: Layouts = {};
  for (const [bp, cols] of Object.entries(BREAKPOINT_COLS)) {
    layouts[bp] = buildLayoutFromWidgets(widgets, cols);
  }
  return layouts;
}
