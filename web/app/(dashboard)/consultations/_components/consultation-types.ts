import { Video, MessageSquare, Phone, Mail } from 'lucide-react';

export interface Consultation {
  consultation_id: string; user_id: string; astrologer_id: string;
  chart_id: string | null; consultation_type_id: number;
  consultation_type_name: string; status_id: number; status_name: string;
  user_questions: string | null; focus_areas: string[] | null;
  scheduled_at: string | null; duration_minutes: number | null;
  total_amount: number | null; currency: string;
  payment_status_id: number | null; payment_status_name: string | null;
  ai_summary: string | null; created_at: string; completed_at: string | null;
}

export interface ConsultationsResponse {
  consultations: Consultation[]; total: number; limit: number; offset: number;
}

export const TABS = ['All', 'Upcoming', 'Past'] as const;
export type Tab = (typeof TABS)[number];

export const TYPE_ICONS: Record<string, React.ElementType> = {
  Video, Chat: MessageSquare, Voice: Phone, Email: Mail,
};

export const TYPE_GRAD: Record<string, string> = {
  Video: 'var(--gradient-video)', Chat: 'var(--gradient-chat)',
  Voice: 'var(--gradient-voice)', Email: 'var(--gradient-email)',
};

export const STATUS_STYLE: Record<string, { bg: string; fg: string; border: string }> = {
  Pending:       { bg: 'transparent', fg: 'var(--text-muted)', border: '1px solid var(--border)' },
  Scheduled:     { bg: 'var(--gold-bg)', fg: 'var(--gold-bright)', border: '1px solid rgba(200,145,58,0.25)' },
  'In Progress': { bg: 'var(--gold-bg)', fg: 'var(--gold)', border: '1px solid rgba(200,145,58,0.3)' },
  Completed:     { bg: 'var(--green-bg)', fg: 'var(--green)', border: '1px solid rgba(52,211,153,0.25)' },
  Cancelled:     { bg: 'var(--red-bg)', fg: 'var(--red)', border: '1px solid rgba(239,68,68,0.25)' },
  Refunded:      { bg: 'transparent', fg: 'var(--text-muted)', border: '1px solid var(--border)' },
};

export const AREA_CLR: Record<string, [string, string]> = {
  Career: ['var(--blue-bg)','var(--blue)'], Relationship: ['rgba(218,122,148,0.10)','var(--pink)'],
  Health: ['var(--green-bg)','var(--green)'], Finance: ['var(--gold-bg)','var(--gold-bright)'],
  Spiritual: ['var(--green-bg)','var(--green)'], Family: ['var(--purple-bg)','var(--purple)'],
};

export function formatDateTime(dateStr: string | null): { date: string; time: string } | null {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return null;
  return {
    date: d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }),
    time: d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
  };
}

export function isUpcoming(c: Consultation): boolean {
  if (['Cancelled', 'Completed', 'Refunded'].includes(c.status_name)) return false;
  if (!c.scheduled_at) return c.status_name === 'Pending' || c.status_name === 'Scheduled';
  return new Date(c.scheduled_at) >= new Date();
}

export function isPast(c: Consultation): boolean {
  return ['Completed', 'Cancelled', 'Refunded'].includes(c.status_name) ||
    (!!c.scheduled_at && new Date(c.scheduled_at) < new Date());
}
