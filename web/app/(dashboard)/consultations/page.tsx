'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Video,
  MessageSquare,
  Phone,
  Mail,
  Calendar,
  Clock,
  Star,
  ArrowRight,
  Users,
} from 'lucide-react';
import Link from 'next/link';

/* ---------- Types ---------- */

interface Consultation {
  consultation_id: string;
  user_id: string;
  astrologer_id: string;
  chart_id: string | null;
  consultation_type_id: number;
  consultation_type_name: string;
  status_id: number;
  status_name: string;
  user_questions: string | null;
  focus_areas: string[] | null;
  scheduled_at: string | null;
  duration_minutes: number | null;
  total_amount: number | null;
  currency: string;
  payment_status_id: number | null;
  payment_status_name: string | null;
  ai_summary: string | null;
  created_at: string;
  completed_at: string | null;
}

interface ConsultationsResponse {
  consultations: Consultation[];
  total: number;
  limit: number;
  offset: number;
}

/* ---------- Constants ---------- */

const TABS = ['All', 'Upcoming', 'Past'] as const;
type Tab = (typeof TABS)[number];

const STATUS_STYLES: Record<string, { variant: 'blue' | 'default' | 'green' | 'destructive' | 'outline'; label: string }> = {
  Pending:       { variant: 'outline',      label: 'Pending' },
  Scheduled:     { variant: 'blue',         label: 'Scheduled' },
  'In Progress': { variant: 'default',      label: 'In Progress' },
  Completed:     { variant: 'green',        label: 'Completed' },
  Cancelled:     { variant: 'destructive',  label: 'Cancelled' },
  Refunded:      { variant: 'outline',      label: 'Refunded' },
};

const TYPE_ICONS: Record<string, React.ElementType> = {
  Video: Video,
  Chat: MessageSquare,
  Voice: Phone,
  Email: Mail,
};

const AVATAR_COLORS = [
  'bg-amber-600', 'bg-indigo-600', 'bg-emerald-600', 'bg-rose-600',
  'bg-sky-600', 'bg-violet-600', 'bg-teal-600', 'bg-orange-600',
];

function avatarColor(id: string): string {
  const idx = id.charCodeAt(0) % AVATAR_COLORS.length;
  return AVATAR_COLORS[idx];
}

/* ---------- Helpers ---------- */

function formatDateTime(dateStr: string | null): { date: string; time: string } | null {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return null;
  return {
    date: d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }),
    time: d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
  };
}

function isUpcoming(c: Consultation): boolean {
  if (['Cancelled', 'Completed', 'Refunded'].includes(c.status_name)) return false;
  if (!c.scheduled_at) return c.status_name === 'Pending' || c.status_name === 'Scheduled';
  return new Date(c.scheduled_at) >= new Date();
}

function isPast(c: Consultation): boolean {
  return ['Completed', 'Cancelled', 'Refunded'].includes(c.status_name) ||
    (!!c.scheduled_at && new Date(c.scheduled_at) < new Date());
}

/* ---------- Sub-components ---------- */

function ConsultationSkeleton() {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 animate-pulse">
      <div className="flex items-start gap-4">
        <div className="h-10 w-10 rounded-full bg-border" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-40 rounded bg-border" />
          <div className="h-3 w-56 rounded bg-border" />
        </div>
        <div className="h-6 w-20 rounded-full bg-border" />
      </div>
      <div className="mt-4 flex gap-4">
        <div className="h-3 w-32 rounded bg-border" />
        <div className="h-3 w-24 rounded bg-border" />
      </div>
    </div>
  );
}

function ConsultationCard({ consultation }: { consultation: Consultation }) {
  const dt = formatDateTime(consultation.scheduled_at);
  const statusStyle = STATUS_STYLES[consultation.status_name] ?? { variant: 'outline' as const, label: consultation.status_name };
  const TypeIcon = TYPE_ICONS[consultation.consultation_type_name] ?? MessageSquare;
  const isLive = consultation.status_name === 'In Progress' || consultation.status_name === 'Scheduled';

  return (
    <div className="rounded-2xl border border-border bg-card p-5 transition-colors hover:border-gold/30">
      <div className="flex items-start gap-3">
        {/* Avatar */}
        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-white ${avatarColor(consultation.astrologer_id)}`}
        >
          <TypeIcon className="h-4 w-4" />
        </div>

        {/* Main content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-text-primary">
                  {consultation.consultation_type_name} Consultation
                </h3>
                <Badge variant={statusStyle.variant}>{statusStyle.label}</Badge>
              </div>
              <p className="mt-0.5 text-xs text-text-muted">
                Astrologer ID: {consultation.astrologer_id.slice(0, 8)}...
              </p>
            </div>
          </div>

          {/* Details row */}
          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-text-muted">
            {dt && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {dt.date}
              </span>
            )}
            {dt && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {dt.time}
              </span>
            )}
            {consultation.duration_minutes && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {consultation.duration_minutes} min
              </span>
            )}
            {consultation.total_amount != null && (
              <span className="font-medium text-text-secondary">
                {consultation.currency === 'USD' ? '$' : consultation.currency}
                {consultation.total_amount}
              </span>
            )}
          </div>

          {/* Focus areas */}
          {consultation.focus_areas && consultation.focus_areas.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {consultation.focus_areas.slice(0, 3).map((area) => (
                <Badge key={area} variant="outline" className="text-[10px] px-2 py-0.5">
                  {area}
                </Badge>
              ))}
            </div>
          )}

          {/* AI Summary snippet */}
          {consultation.ai_summary && (
            <p className="mt-2 line-clamp-2 text-xs text-text-muted italic">
              {consultation.ai_summary}
            </p>
          )}
        </div>

        {/* Action button */}
        <div className="shrink-0">
          {isLive ? (
            <Link href={`/consultations/${consultation.consultation_id}`}>
              <Button size="sm" className="gap-1">
                Join <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          ) : (
            <Link href={`/consultations/${consultation.consultation_id}`}>
              <Button variant="outline" size="sm">View</Button>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- Main Page ---------- */

export default function ConsultationsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('All');

  const { data, isLoading, isError } = useQuery({
    queryKey: ['my-consultations'],
    queryFn: () =>
      apiClient.get<ConsultationsResponse>('/api/v1/consultations/my-consultations?limit=50'),
  });

  const allConsultations = data?.data?.consultations ?? [];

  const filtered = (() => {
    switch (activeTab) {
      case 'Upcoming':
        return allConsultations.filter(isUpcoming);
      case 'Past':
        return allConsultations.filter(isPast);
      default:
        return allConsultations;
    }
  })();

  // Sort: upcoming first (by scheduled_at asc), then past (by scheduled_at desc)
  const sorted = [...filtered].sort((a, b) => {
    const aDate = a.scheduled_at ? new Date(a.scheduled_at).getTime() : 0;
    const bDate = b.scheduled_at ? new Date(b.scheduled_at).getTime() : 0;
    if (activeTab === 'Upcoming') return aDate - bDate;
    if (activeTab === 'Past') return bDate - aDate;
    // "All" tab: upcoming first, then past
    const aUp = isUpcoming(a);
    const bUp = isUpcoming(b);
    if (aUp && !bUp) return -1;
    if (!aUp && bUp) return 1;
    return aUp ? aDate - bDate : bDate - aDate;
  });

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="font-display text-display-md text-text-primary">Consultations</h1>
        <p className="mt-1 text-sm text-text-muted">
          Manage your astrologer consultations and session history
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 border-b border-border">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="relative px-4 py-2.5 text-sm font-medium transition-colors"
            style={{
              color: activeTab === tab ? 'var(--gold)' : 'var(--text-muted)',
              borderBottom: activeTab === tab ? '2px solid var(--gold)' : '2px solid transparent',
            }}
          >
            {tab}
            {tab === 'Upcoming' && allConsultations.filter(isUpcoming).length > 0 && (
              <span className="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-[var(--gold-bg)] px-1 text-[10px] font-semibold text-gold-bright">
                {allConsultations.filter(isUpcoming).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <ConsultationSkeleton key={i} />
          ))}
        </div>
      ) : isError ? (
        <div className="rounded-2xl border border-border bg-card p-12 text-center">
          <p className="text-sm text-text-muted">
            Failed to load consultations. Please try again later.
          </p>
        </div>
      ) : sorted.length === 0 ? (
        <div className="rounded-2xl border border-border bg-card px-6 py-16 text-center">
          {/* Illustration */}
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-[var(--gold-bg)]">
            <Calendar className="h-10 w-10 text-gold" />
          </div>

          <h2 className="font-display text-lg font-semibold text-text-primary">
            Your Consultations
          </h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-text-muted">
            Book a session with a professional astrologer to get personalized guidance
            on your chart, life questions, and spiritual journey.
          </p>

          {/* Feature cards */}
          <div className="mx-auto mt-8 grid max-w-xl grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-border bg-surface p-4">
              <Video className="mx-auto mb-2 h-6 w-6 text-gold" />
              <h4 className="text-xs font-semibold text-text-primary">Video Calls</h4>
              <p className="mt-1 text-[11px] leading-snug text-text-muted">
                Face-to-face sessions with screen sharing
              </p>
            </div>
            <div className="rounded-xl border border-border bg-surface p-4">
              <MessageSquare className="mx-auto mb-2 h-6 w-6 text-gold" />
              <h4 className="text-xs font-semibold text-text-primary">Live Chat</h4>
              <p className="mt-1 text-[11px] leading-snug text-text-muted">
                Real-time text consultations
              </p>
            </div>
            <div className="rounded-xl border border-border bg-surface p-4">
              <Phone className="mx-auto mb-2 h-6 w-6 text-gold" />
              <h4 className="text-xs font-semibold text-text-primary">Voice Calls</h4>
              <p className="mt-1 text-[11px] leading-snug text-text-muted">
                Audio consultations for on-the-go
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="mt-8">
            <Link href="/astrologers">
              <Button size="sm" className="gap-1 bg-gold text-black hover:bg-gold-bright">
                Browse Astrologers
                <span aria-hidden="true">&rarr;</span>
              </Button>
            </Link>
          </div>
          <p className="mt-4 text-xs text-text-faint">
            Your upcoming and past consultations will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {sorted.map((consultation) => (
            <ConsultationCard key={consultation.consultation_id} consultation={consultation} />
          ))}
        </div>
      )}
    </div>
  );
}
