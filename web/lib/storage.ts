import { z } from 'zod';

/**
 * Type-safe localStorage helper with zod validation.
 * Invalid or corrupted data returns the fallback instead of crashing.
 */
export function loadFromStorage<T>(
  key: string,
  schema: z.ZodType<T>,
  fallback: T
): T {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    const result = schema.safeParse(parsed);
    if (result.success) return result.data;
    // Invalid shape — clear corrupted data
    console.warn(`[storage] Invalid data for "${key}", using fallback`, result.error.issues);
    localStorage.removeItem(key);
    return fallback;
  } catch {
    return fallback;
  }
}

export function saveToStorage<T>(key: string, data: T): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch {
    // Storage full or unavailable
  }
}

export function removeFromStorage(key: string): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.removeItem(key);
  } catch {
    // Ignore
  }
}

/* ---------- Zod schemas for widget data ---------- */

export const widgetInstanceSchema = z.object({
  id: z.string(),
  type: z.string(),
  size: z.string(),
});

export const widgetInstanceArraySchema = z.array(widgetInstanceSchema);

/** Loose validator for react-grid-layout Layouts (Record<string, LayoutItem[]>) */
const layoutItemSchema = z.object({
  i: z.string(),
  x: z.number(),
  y: z.number(),
  w: z.number(),
  h: z.number(),
  minW: z.number().optional(),
  minH: z.number().optional(),
  maxW: z.number().optional(),
  maxH: z.number().optional(),
});

export const layoutsSchema = z.record(z.string(), z.array(layoutItemSchema));
