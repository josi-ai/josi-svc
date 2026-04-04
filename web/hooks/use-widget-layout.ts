'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { type Layouts } from 'react-grid-layout';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import {
  type WidgetType,
  type WidgetInstance,
  widgetCatalog,
  defaultWidgets,
  buildLayoutFromWidgets,
} from '@/config/widget-config';

/* ---------- Types ---------- */

interface DashboardPreferences {
  widget_layout?: Layouts | null;
  active_widgets?: WidgetInstance[] | null;
}

interface UserPreferences {
  dashboard?: DashboardPreferences;
  [key: string]: any;
}

/* ---------- Constants ---------- */

const STORAGE_KEY = 'josi-dashboard-widgets';
const LAYOUT_STORAGE_KEY = 'josi-dashboard-layouts';
const DEBOUNCE_MS = 1000;

const BREAKPOINT_COLS: Record<string, number> = {
  lg: 3,
  md: 2,
  sm: 1,
  xs: 1,
};

/* ---------- localStorage helpers ---------- */

function loadLocalWidgets(): WidgetInstance[] {
  if (typeof window === 'undefined') return defaultWidgets;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as WidgetInstance[];
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch {
    // corrupted — fall back
  }
  return defaultWidgets;
}

function loadLocalLayouts(): Layouts | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(LAYOUT_STORAGE_KEY);
    if (raw) return JSON.parse(raw) as Layouts;
  } catch {
    // corrupted
  }
  return null;
}

function saveLocal(widgets: WidgetInstance[], layouts: Layouts) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(widgets));
    localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(layouts));
  } catch {
    // storage full or unavailable
  }
}

/* ---------- Default layouts builder ---------- */

function buildDefaultLayouts(widgets: WidgetInstance[]): Layouts {
  const layouts: Layouts = {};
  for (const [bp, cols] of Object.entries(BREAKPOINT_COLS)) {
    layouts[bp] = buildLayoutFromWidgets(widgets, cols);
  }
  return layouts;
}

/* ---------- Hook ---------- */

export function useWidgetLayout() {
  const { isAuthReady } = useAuth();
  const queryClient = useQueryClient();

  const [widgets, setWidgets] = useState<WidgetInstance[]>(defaultWidgets);
  const [layouts, setLayouts] = useState<Layouts>(() =>
    buildDefaultLayouts(defaultWidgets),
  );
  const [mounted, setMounted] = useState(false);

  // Debounce timer ref for layout persistence
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* ---------- Fetch preferences from backend ---------- */

  const { data: prefsData, isSuccess: prefsFetched, isError: prefsError } = useQuery({
    queryKey: ['me-preferences'],
    queryFn: () => apiClient.get<UserPreferences>('/api/v1/me/preferences'),
    enabled: isAuthReady,
    staleTime: 5 * 60 * 1000,
    retry: false, // Don't retry on 401 — just use defaults
  });

  /* ---------- Save preferences mutation ---------- */

  const saveMutation = useMutation({
    mutationFn: (prefs: { dashboard: DashboardPreferences }) =>
      apiClient.put('/api/v1/me/preferences', prefs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me-preferences'] });
    },
  });

  /* ---------- Initialize state from backend or localStorage ---------- */

  useEffect(() => {
    if (!prefsFetched) return;

    const dashboard = prefsData?.data?.dashboard;
    const serverWidgets = dashboard?.active_widgets;
    const serverLayouts = dashboard?.widget_layout;

    if (serverWidgets && Array.isArray(serverWidgets) && serverWidgets.length > 0) {
      // Validate widget types still exist in catalog
      const validWidgets = serverWidgets.filter((w: WidgetInstance) =>
        widgetCatalog.some((c) => c.type === w.type),
      );
      const resolvedWidgets = validWidgets.length > 0 ? validWidgets : defaultWidgets;
      setWidgets(resolvedWidgets);

      if (serverLayouts && typeof serverLayouts === 'object' && Object.keys(serverLayouts).length > 0) {
        setLayouts(serverLayouts as Layouts);
      } else {
        setLayouts(buildDefaultLayouts(resolvedWidgets));
      }
    } else {
      // Fall back to localStorage
      const localWidgets = loadLocalWidgets();
      const localLayouts = loadLocalLayouts();
      setWidgets(localWidgets);
      setLayouts(localLayouts ?? buildDefaultLayouts(localWidgets));
    }

    setMounted(true);
  }, [prefsFetched, prefsData]);

  // If prefs fetch fails (e.g. 401 before auth is ready), still mount with defaults
  useEffect(() => {
    if (prefsError && !mounted) {
      const localWidgets = loadLocalWidgets();
      const localLayouts = loadLocalLayouts();
      setWidgets(localWidgets);
      setLayouts(localLayouts ?? buildDefaultLayouts(localWidgets));
      setMounted(true);
    }
  }, [prefsError, mounted]);

  // If auth is not ready (e.g. anonymous user), still load from localStorage
  useEffect(() => {
    if (!isAuthReady) {
      const localWidgets = loadLocalWidgets();
      const localLayouts = loadLocalLayouts();
      setWidgets(localWidgets);
      setLayouts(localLayouts ?? buildDefaultLayouts(localWidgets));
      setMounted(true);
    }
  }, [isAuthReady]);

  /* ---------- Persist to backend (debounced) ---------- */

  const persistToBackend = useCallback(
    (newWidgets: WidgetInstance[], newLayouts: Layouts) => {
      // Always save locally for instant feedback
      saveLocal(newWidgets, newLayouts);

      // Debounced backend save
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        if (isAuthReady) {
          saveMutation.mutate({
            dashboard: {
              active_widgets: newWidgets,
              widget_layout: newLayouts,
            },
          });
        }
      }, DEBOUNCE_MS);
    },
    [isAuthReady, saveMutation],
  );

  /* ---------- Persist immediately (for add/remove) ---------- */

  const persistImmediately = useCallback(
    (newWidgets: WidgetInstance[], newLayouts: Layouts) => {
      saveLocal(newWidgets, newLayouts);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      if (isAuthReady) {
        saveMutation.mutate({
          dashboard: {
            active_widgets: newWidgets,
            widget_layout: newLayouts,
          },
        });
      }
    },
    [isAuthReady, saveMutation],
  );

  /* ---------- Layout change handler (from react-grid-layout) ---------- */

  const onLayoutChange = useCallback(
    (_currentLayout: any, allLayouts: Layouts) => {
      setLayouts(allLayouts);
      persistToBackend(widgets, allLayouts);
    },
    [widgets, persistToBackend],
  );

  /* ---------- Add widget ---------- */

  const addWidget = useCallback(
    (type: WidgetType) => {
      const def = widgetCatalog.find((w) => w.type === type);
      if (!def) return;

      const id = `w-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      const newWidget: WidgetInstance = { id, type, size: def.defaultSize };

      setWidgets((prev) => {
        const next = [...prev, newWidget];

        // Add the new widget to all breakpoint layouts
        const newLayouts = { ...layouts };
        for (const [bp, cols] of Object.entries(BREAKPOINT_COLS)) {
          const existing = newLayouts[bp] || [];
          // Find the max y position to place the new widget at the bottom
          let maxY = 0;
          for (const item of existing) {
            const bottom = item.y + item.h;
            if (bottom > maxY) maxY = bottom;
          }
          const w = Math.min(
            Math.round((def.gridDimensions.w / 3) * cols),
            cols,
          );
          newLayouts[bp] = [
            ...existing,
            {
              i: id,
              x: 0,
              y: maxY,
              w,
              h: def.gridDimensions.h,
              minW: def.gridDimensions.minW
                ? Math.min(Math.round((def.gridDimensions.minW / 3) * cols), cols)
                : undefined,
              minH: def.gridDimensions.minH,
              maxW: def.gridDimensions.maxW ? Math.min(def.gridDimensions.maxW, cols) : cols,
              maxH: def.gridDimensions.maxH,
            },
          ];
        }
        setLayouts(newLayouts);
        persistImmediately(next, newLayouts);

        return next;
      });
    },
    [layouts, persistImmediately],
  );

  /* ---------- Remove widget ---------- */

  const removeWidget = useCallback(
    (id: string) => {
      setWidgets((prev) => {
        const next = prev.filter((w) => w.id !== id);

        // Remove from all breakpoint layouts
        const newLayouts = { ...layouts };
        for (const bp of Object.keys(newLayouts)) {
          newLayouts[bp] = (newLayouts[bp] || []).filter(
            (item: any) => item.i !== id,
          );
        }
        setLayouts(newLayouts);
        persistImmediately(next, newLayouts);

        return next;
      });
    },
    [layouts, persistImmediately],
  );

  /* ---------- Cleanup debounce on unmount ---------- */

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  return {
    widgets,
    layouts,
    mounted,
    addWidget,
    removeWidget,
    onLayoutChange,
    isSaving: saveMutation.isPending,
  };
}
