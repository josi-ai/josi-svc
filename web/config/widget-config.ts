export type WidgetType =
  | 'todays-sky'
  | 'muhurta-timeline'
  | 'chart-quick-view'
  | 'current-dasha'
  | 'ai-chat-access'
  | 'latest-reading'
  | 'bazi-summary'
  | 'western-transit'
  | 'available-astrologers';

export type WidgetSize = 'full' | 'half' | 'third';
export type TraditionBadge = 'vedic' | 'western' | 'chinese' | 'celtic' | 'ai' | 'general';

export interface WidgetGridDimensions {
  /** Grid columns the widget spans (out of 3) */
  w: number;
  /** Grid rows the widget spans */
  h: number;
  /** Minimum width in grid columns */
  minW?: number;
  /** Minimum height in grid rows */
  minH?: number;
  /** Maximum width in grid columns */
  maxW?: number;
  /** Maximum height in grid rows */
  maxH?: number;
}

export interface WidgetDefinition {
  type: WidgetType;
  label: string;
  description: string;
  /** Extended description shown in the add-widget modal preview */
  previewDescription: string;
  icon: string;
  tradition: TraditionBadge;
  defaultSize: WidgetSize;
  /** Default grid dimensions for react-grid-layout */
  gridDimensions: WidgetGridDimensions;
  category: string;
}

export interface WidgetInstance {
  id: string;
  type: WidgetType;
  size: WidgetSize;
}

export const TRADITION_COLORS: Record<TraditionBadge, { bg: string; text: string }> = {
  vedic: { bg: 'rgba(200,145,58,0.12)', text: 'var(--gold-bright)' },
  western: { bg: 'var(--blue-bg)', text: 'var(--blue)' },
  chinese: { bg: 'rgba(196,80,60,0.1)', text: '#C45040' },
  celtic: { bg: 'var(--green-bg)', text: 'var(--green)' },
  ai: { bg: 'rgba(123,90,175,0.1)', text: '#7B5AAF' },
  general: { bg: 'rgba(100,110,130,0.1)', text: 'var(--text-muted)' },
};

export const widgetCatalog: WidgetDefinition[] = [
  {
    type: 'todays-sky',
    label: "Today's Sky",
    description: 'Tithi, nakshatra, yoga for today',
    previewDescription:
      'Live Vedic panchang showing today\'s tithi, nakshatra, yoga, karana, and vara. Includes Rahu Kaal and other inauspicious time windows at a glance.',
    icon: '\u2600',
    tradition: 'vedic',
    defaultSize: 'full',
    gridDimensions: { w: 3, h: 3, minW: 2, minH: 2, maxH: 6 },
    category: 'Vedic',
  },
  {
    type: 'muhurta-timeline',
    label: 'Muhurta Timeline',
    description: 'Auspicious/inauspicious time windows',
    previewDescription:
      'Visual timeline of today\'s muhurta periods, color-coded by auspiciousness. See at a glance when to schedule important activities.',
    icon: '\u23F0',
    tradition: 'vedic',
    defaultSize: 'half',
    gridDimensions: { w: 2, h: 4, minW: 1, minH: 3, maxH: 8 },
    category: 'Vedic',
  },
  {
    type: 'chart-quick-view',
    label: 'Chart Quick View',
    description: 'Mini birth chart with key placements',
    previewDescription:
      'Compact view of your birth chart showing lagna, Moon sign, Sun sign, and key planetary placements. Quick access to your chart details.',
    icon: '\uD83D\uDCCA',
    tradition: 'vedic',
    defaultSize: 'third',
    gridDimensions: { w: 1, h: 3, minW: 1, minH: 2, maxW: 2, maxH: 6 },
    category: 'Vedic',
  },
  {
    type: 'current-dasha',
    label: 'Current Dasha',
    description: 'Your active planetary period',
    previewDescription:
      'Displays your current Vimshottari Dasha period (Maha, Antar, Pratyantar) with start/end dates and the ruling planet\'s significations.',
    icon: '\uD83D\uDCC8',
    tradition: 'vedic',
    defaultSize: 'third',
    gridDimensions: { w: 1, h: 3, minW: 1, minH: 2, maxW: 2, maxH: 6 },
    category: 'Vedic',
  },
  {
    type: 'ai-chat-access',
    label: 'AI Chat',
    description: 'Ask Josi AI anything',
    previewDescription:
      'Quick access to Josi AI for personalized astrological guidance. Ask about your chart, current transits, compatibility, or any astrology question.',
    icon: '\uD83E\uDD16',
    tradition: 'ai',
    defaultSize: 'third',
    gridDimensions: { w: 1, h: 3, minW: 1, minH: 2, maxW: 2, maxH: 6 },
    category: 'General',
  },
  {
    type: 'latest-reading',
    label: 'Latest Reading',
    description: 'Most recent AI-generated insight',
    previewDescription:
      'Shows your most recent AI-generated reading with a summary and link to the full interpretation. Keeps your latest insights front and center.',
    icon: '\uD83D\uDCD6',
    tradition: 'vedic',
    defaultSize: 'third',
    gridDimensions: { w: 1, h: 3, minW: 1, minH: 2, maxW: 2, maxH: 5 },
    category: 'General',
  },
  {
    type: 'bazi-summary',
    label: 'BaZi Summary',
    description: 'Chinese Four Pillars overview',
    previewDescription:
      'Overview of your BaZi (Four Pillars of Destiny) chart showing Year, Month, Day, and Hour pillars with their Heavenly Stems and Earthly Branches.',
    icon: '\uD83C\uDFEE',
    tradition: 'chinese',
    defaultSize: 'third',
    gridDimensions: { w: 1, h: 3, minW: 1, minH: 2, maxW: 2, maxH: 5 },
    category: 'Chinese',
  },
  {
    type: 'western-transit',
    label: 'Western Transit',
    description: 'Current Western transits',
    previewDescription:
      'Real-time Western tropical transits showing major planetary aspects to your natal chart. Highlights significant transits happening now.',
    icon: '\u2B50',
    tradition: 'western',
    defaultSize: 'half',
    gridDimensions: { w: 1, h: 3, minW: 1, minH: 2, maxH: 6 },
    category: 'Western',
  },
  {
    type: 'available-astrologers',
    label: 'Available Astrologers',
    description: "Who's online now",
    previewDescription:
      'See which professional astrologers are currently available for consultations. Browse by tradition, rating, and specialty.',
    icon: '\uD83D\uDC64',
    tradition: 'general',
    defaultSize: 'third',
    gridDimensions: { w: 1, h: 3, minW: 1, minH: 2, maxW: 2, maxH: 5 },
    category: 'General',
  },
];

/** Ordered category labels for the add-widget modal */
export const WIDGET_CATEGORIES = ['Vedic', 'Western', 'Chinese', 'General'] as const;

export const defaultWidgets: WidgetInstance[] = [
  { id: 'w1', type: 'todays-sky', size: 'full' },       // row 1: full width
  { id: 'w2', type: 'chart-quick-view', size: 'third' }, // row 2: 3 across
  { id: 'w3', type: 'current-dasha', size: 'third' },
  { id: 'w4', type: 'ai-chat-access', size: 'third' },
  { id: 'w5', type: 'muhurta-timeline', size: 'half' },  // row 3: 2 + 1
  { id: 'w6', type: 'western-transit', size: 'half' },
  { id: 'w7', type: 'latest-reading', size: 'third' },   // row 4: 3 across
  { id: 'w8', type: 'bazi-summary', size: 'third' },
  // available-astrologers removed from defaults — no astrologers table yet, widget crashes on stale cache
];

/**
 * Build a react-grid-layout Layout array from a list of widget instances.
 * Widgets are placed left-to-right, wrapping at `cols` columns.
 */
export function buildLayoutFromWidgets(
  widgets: WidgetInstance[],
  cols: number,
): Array<{ i: string; x: number; y: number; w: number; h: number; minW?: number; minH?: number; maxW?: number; maxH?: number }> {
  let x = 0;
  let y = 0;
  let rowMaxH = 0;
  return widgets.map((widget) => {
    const def = widgetCatalog.find((w) => w.type === widget.type);
    const dim = def?.gridDimensions ?? { w: 1, h: 3 };
    // Scale width to the number of columns available
    const w = Math.min(Math.round((dim.w / 3) * cols), cols);
    const minW = dim.minW ? Math.min(Math.round((dim.minW / 3) * cols), cols) : undefined;
    const maxW = dim.maxW ? Math.min(dim.maxW, cols) : cols;

    if (x + w > cols) {
      x = 0;
      y += rowMaxH;
      rowMaxH = 0;
    }

    const item = {
      i: widget.id, x, y, w, h: dim.h,
      minW, minH: dim.minH,
      maxW, maxH: dim.maxH,
    };
    x += w;
    rowMaxH = Math.max(rowMaxH, dim.h);
    if (x >= cols) {
      x = 0;
      y += rowMaxH;
      rowMaxH = 0;
    }
    return item;
  });
}
