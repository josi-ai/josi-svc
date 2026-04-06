/**
 * Types and constants for the AI Chat page.
 */

export interface Message { role: 'user' | 'assistant'; content: string }

export interface Chart {
  chart_id: string;
  chart_type: string;
  person_id: string;
  chart_data?: {
    planets?: Record<string, { sign?: string; longitude?: number; house?: number; is_retrograde?: boolean }>;
    ascendant?: { sign?: string; degree?: number };
    dasha?: {
      current_dasha?: {
        mahadasha?: { planet: string; start_date: string; end_date: string };
        antardasha?: { planet: string; start_date: string; end_date: string };
      };
    };
  };
}

export interface DashaResponse {
  person_id: string;
  current_dasha: {
    mahadasha: { planet: string; start_date: string; end_date: string };
    antardasha?: { planet: string; start_date: string; end_date: string };
  } | null;
}

export interface Transit {
  transiting_planet: string;
  aspect_type: string;
  natal_planet: string;
  intensity?: number | string;
  description?: string;
}

export const SUGGESTIONS = [
  'What does my current dasha mean?',
  'How are transits affecting me today?',
  'Tell me about my career prospects',
  'What remedies should I consider?',
  'Explain my birth chart',
  'What are my strongest placements?',
];

export const STYLES = [
  { value: 1, label: 'Balanced' },
  { value: 2, label: 'Psychological' },
  { value: 3, label: 'Spiritual' },
  { value: 4, label: 'Practical' },
  { value: 5, label: 'Predictive' },
];
