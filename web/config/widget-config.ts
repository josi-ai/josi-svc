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

export interface WidgetDefinition {
  type: WidgetType;
  label: string;
  description: string;
  icon: string;
  tradition: TraditionBadge;
  defaultSize: WidgetSize;
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
    icon: '\u2600',
    tradition: 'vedic',
    defaultSize: 'full',
    category: 'Daily & Timing',
  },
  {
    type: 'muhurta-timeline',
    label: 'Muhurta Timeline',
    description: 'Auspicious/inauspicious time windows',
    icon: '\u23F0',
    tradition: 'vedic',
    defaultSize: 'half',
    category: 'Daily & Timing',
  },
  {
    type: 'chart-quick-view',
    label: 'Chart Quick View',
    description: 'Mini birth chart with key placements',
    icon: '\uD83D\uDCCA',
    tradition: 'vedic',
    defaultSize: 'third',
    category: 'Your Charts',
  },
  {
    type: 'current-dasha',
    label: 'Current Dasha',
    description: 'Your active planetary period',
    icon: '\uD83D\uDCC8',
    tradition: 'vedic',
    defaultSize: 'third',
    category: 'Your Charts',
  },
  {
    type: 'ai-chat-access',
    label: 'AI Chat',
    description: 'Ask Josi AI anything',
    icon: '\uD83E\uDD16',
    tradition: 'ai',
    defaultSize: 'third',
    category: 'AI & Insights',
  },
  {
    type: 'latest-reading',
    label: 'Latest Reading',
    description: 'Most recent AI-generated insight',
    icon: '\uD83D\uDCD6',
    tradition: 'vedic',
    defaultSize: 'third',
    category: 'AI & Insights',
  },
  {
    type: 'bazi-summary',
    label: 'BaZi Summary',
    description: 'Chinese Four Pillars overview',
    icon: '\uD83C\uDFEE',
    tradition: 'chinese',
    defaultSize: 'third',
    category: 'Multi-Tradition',
  },
  {
    type: 'western-transit',
    label: 'Western Transit',
    description: 'Current Western transits',
    icon: '\u2B50',
    tradition: 'western',
    defaultSize: 'half',
    category: 'Multi-Tradition',
  },
  {
    type: 'available-astrologers',
    label: 'Available Astrologers',
    description: "Who's online now",
    icon: '\uD83D\uDC64',
    tradition: 'general',
    defaultSize: 'third',
    category: 'Connect',
  },
];

export const defaultWidgets: WidgetInstance[] = [
  { id: 'w1', type: 'todays-sky', size: 'full' },
  { id: 'w2', type: 'chart-quick-view', size: 'third' },
  { id: 'w3', type: 'current-dasha', size: 'third' },
  { id: 'w4', type: 'ai-chat-access', size: 'third' },
  { id: 'w5', type: 'muhurta-timeline', size: 'half' },
  { id: 'w6', type: 'western-transit', size: 'half' },
  { id: 'w7', type: 'bazi-summary', size: 'third' },
  { id: 'w8', type: 'latest-reading', size: 'third' },
  { id: 'w9', type: 'available-astrologers', size: 'third' },
];
