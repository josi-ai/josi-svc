'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  Video, MessageSquare, Phone, Mail, Calendar, Clock, ArrowRight,
} from 'lucide-react';
import Link from 'next/link';

/* ── Types ─────────────────────────────────────────────────────── */

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

/* ── Constants ─────────────────────────────────────────────────── */

const TABS = ['All', 'Upcoming', 'Past'] as const;
type Tab = (typeof TABS)[number];

const TYPE_ICONS: Record<string, React.ElementType> = {
  Video, Chat: MessageSquare, Voice: Phone, Email: Mail,
};

const TYPE_GRAD: Record<string, string> = {
  Video: 'var(--gradient-video)',
  Chat: 'var(--gradient-chat)',
  Voice: 'var(--gradient-voice)',
  Email: 'var(--gradient-email)',
};

const STATUS_STYLE: Record<string, { bg: string; fg: string; border: string }> = {
  Pending:       { bg: 'transparent', fg: 'var(--text-muted)', border: '1px solid var(--border)' },
  Scheduled:     { bg: 'var(--gold-bg)', fg: 'var(--gold-bright)', border: '1px solid rgba(200,145,58,0.25)' },
  'In Progress': { bg: 'var(--gold-bg)', fg: 'var(--gold)', border: '1px solid rgba(200,145,58,0.3)' },
  Completed:     { bg: 'var(--green-bg)', fg: 'var(--green)', border: '1px solid rgba(52,211,153,0.25)' },
  Cancelled:     { bg: 'var(--red-bg)', fg: 'var(--red)', border: '1px solid rgba(239,68,68,0.25)' },
  Refunded:      { bg: 'transparent', fg: 'var(--text-muted)', border: '1px solid var(--border)' },
};

const AREA_CLR: Record<string, [string, string]> = {
  Career: ['var(--blue-bg)','var(--blue)'], Relationship: ['rgba(218,122,148,0.10)','var(--pink)'],
  Health: ['var(--green-bg)','var(--green)'], Finance: ['var(--gold-bg)','var(--gold-bright)'],
  Spiritual: ['var(--green-bg)','var(--green)'], Family: ['var(--purple-bg)','var(--purple)'],
};

/* ── Helpers ───────────────────────────────────────────────────── */

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

/* ── Skeleton ──────────────────────────────────────────────────── */

function ConsultationSkeleton() {
  const bar = (w: string, h: number, mt = 0) => (
    <div style={{ height: h, width: w, borderRadius: 6, background: 'var(--border)', marginTop: mt,
      animation: 'pulse 2s infinite' }} />
  );
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 20 }}>
      <div style={{ display: 'flex', gap: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'var(--border)',
          animation: 'pulse 2s infinite', flexShrink: 0 }} />
        <div style={{ flex: 1 }}>
          {bar('55%', 16)}
          {bar('40%', 12, 10)}
        </div>
        <div style={{ width: 72, height: 24, borderRadius: 20, background: 'var(--border)',
          animation: 'pulse 2s infinite' }} />
      </div>
      <div style={{ display: 'flex', gap: 16, marginTop: 16 }}>
        {bar('120px', 12)}
        {bar('80px', 12)}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        {bar('60px', 22)}
        {bar('72px', 22)}
      </div>
    </div>
  );
}

/* ── Consultation Card ─────────────────────────────────────────── */

function ConsultationCard({ consultation }: { consultation: Consultation }) {
  const dt = formatDateTime(consultation.scheduled_at);
  const TypeIcon = TYPE_ICONS[consultation.consultation_type_name] ?? MessageSquare;
  const grad = TYPE_GRAD[consultation.consultation_type_name] ?? TYPE_GRAD.Email;
  const status = STATUS_STYLE[consultation.status_name] ?? STATUS_STYLE.Pending;
  const isLive = consultation.status_name === 'In Progress' || consultation.status_name === 'Scheduled';

  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
      padding: 20, transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s' }}
      onMouseEnter={(e) => { const s = e.currentTarget.style; s.transform = 'translateY(-1px)'; s.boxShadow = '0 4px 20px rgba(0,0,0,0.18)'; s.borderColor = 'rgba(200,145,58,0.2)'; }}
      onMouseLeave={(e) => { const s = e.currentTarget.style; s.transform = ''; s.boxShadow = ''; s.borderColor = 'var(--border)'; }}>

      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
        {/* Type icon */}
        <div style={{ width: 44, height: 44, borderRadius: '50%', background: grad, display: 'flex',
          alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <TypeIcon style={{ width: 20, height: 20, color: '#fff' }} />
        </div>

        {/* Content */}
        <div style={{ minWidth: 0, flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <h3 className="font-display" style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
              {consultation.consultation_type_name} Consultation
            </h3>
            <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: 20, fontSize: 10,
              fontWeight: 600, letterSpacing: 0.3, background: status.bg, color: status.fg,
              border: status.border, lineHeight: '18px' }}>
              {consultation.status_name}
            </span>
          </div>

          <p style={{ marginTop: 4, fontSize: 12, color: 'var(--text-faint)' }}>
            Astrologer: {consultation.astrologer_id.slice(0, 8)}...
          </p>

          {/* Date / time / duration / amount */}
          <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 14, fontSize: 12, color: 'var(--text-muted)' }}>
            {dt && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                <Calendar style={{ width: 13, height: 13, color: 'rgba(200,145,58,0.6)' }} />
                {dt.date}
              </span>
            )}
            {dt && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                <Clock style={{ width: 13, height: 13, color: 'rgba(200,145,58,0.6)' }} />
                {dt.time}
              </span>
            )}
            {consultation.duration_minutes && (
              <span>{consultation.duration_minutes} min</span>
            )}
            {consultation.total_amount != null && (
              <span style={{ fontWeight: 600, color: 'var(--gold)' }}>
                {consultation.currency === 'USD' ? '$' : consultation.currency === 'INR' ? '\u20B9' : consultation.currency}
                {consultation.total_amount}
              </span>
            )}
          </div>

          {/* Focus areas */}
          {consultation.focus_areas && consultation.focus_areas.length > 0 && (
            <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {consultation.focus_areas.slice(0, 3).map((area) => {
                const [bg, fg] = AREA_CLR[area] || ['rgba(100,100,100,0.08)', 'var(--text-muted)'];
                return (
                  <span key={area} style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 20,
                    fontSize: 10, fontWeight: 600, letterSpacing: 0.3, background: bg, color: fg, lineHeight: '18px' }}>
                    {area}
                  </span>
                );
              })}
            </div>
          )}

          {/* AI Summary */}
          {consultation.ai_summary && (
            <p style={{ marginTop: 10, fontSize: 12, lineHeight: 1.5, color: 'var(--text-muted)',
              fontStyle: 'italic', display: '-webkit-box', WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
              {consultation.ai_summary}
            </p>
          )}
        </div>

        {/* Action */}
        <div style={{ flexShrink: 0, alignSelf: 'center' }}>
          <Link href={`/consultations/${consultation.consultation_id}`}>
            {isLive ? (
              <button type="button" style={{ padding: '8px 18px', borderRadius: 8, border: 'none',
                background: 'var(--gold)', color: 'var(--primary-foreground)', fontSize: 13, fontWeight: 600, cursor: 'pointer',
                transition: 'opacity 0.2s, box-shadow 0.2s', display: 'inline-flex', alignItems: 'center', gap: 5 }}
                onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.boxShadow = '0 0 16px rgba(200,145,58,0.3)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.boxShadow = 'none'; }}>
                Join <ArrowRight style={{ width: 14, height: 14 }} />
              </button>
            ) : (
              <button type="button" style={{ padding: '8px 18px', borderRadius: 8,
                border: '1px solid rgba(200,145,58,0.4)', background: 'transparent', color: 'var(--gold)',
                fontSize: 13, fontWeight: 500, cursor: 'pointer', transition: 'all 0.2s' }}
                onMouseEnter={(e) => { const s = e.currentTarget.style; s.background = 'rgba(200,145,58,0.1)'; s.borderColor = 'var(--gold)'; }}
                onMouseLeave={(e) => { const s = e.currentTarget.style; s.background = 'transparent'; s.borderColor = 'rgba(200,145,58,0.4)'; }}>
                View
              </button>
            )}
          </Link>
        </div>
      </div>
    </div>
  );
}

/* ── Consultation Type Card (empty state) ──────────────────────── */

function TypeCard({ icon: Icon, title, desc, price, grad }: {
  icon: React.ComponentType<{ style?: React.CSSProperties }>; title: string; desc: string; price: string; grad: string;
}) {
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12,
      padding: 20, textAlign: 'center', transition: 'border-color 0.2s', flex: '1 1 0' }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(200,145,58,0.25)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; }}>
      <div style={{ width: 44, height: 44, borderRadius: '50%', background: grad, display: 'flex',
        alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px' }}>
        <Icon style={{ width: 20, height: 20, color: '#fff' }} />
      </div>
      <h3 className="font-display" style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
        {title}
      </h3>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.5 }}>{desc}</p>
      <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--gold)', marginTop: 10 }}>{price}</p>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   Main Page
   ═══════════════════════════════════════════════════════════════════ */

export default function ConsultationsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('All');

  const { data, isLoading, isError } = useQuery({
    queryKey: ['my-consultations'],
    queryFn: () =>
      apiClient.get<ConsultationsResponse>('/api/v1/consultations/my-consultations?limit=50'),
  });

  const allConsultations = data?.data?.consultations ?? [];
  const upcomingCount = allConsultations.filter(isUpcoming).length;

  const filtered = (() => {
    switch (activeTab) {
      case 'Upcoming': return allConsultations.filter(isUpcoming);
      case 'Past': return allConsultations.filter(isPast);
      default: return allConsultations;
    }
  })();

  const sorted = [...filtered].sort((a, b) => {
    const aDate = a.scheduled_at ? new Date(a.scheduled_at).getTime() : 0;
    const bDate = b.scheduled_at ? new Date(b.scheduled_at).getTime() : 0;
    if (activeTab === 'Upcoming') return aDate - bDate;
    if (activeTab === 'Past') return bDate - aDate;
    const aUp = isUpcoming(a);
    const bUp = isUpcoming(b);
    if (aUp && !bUp) return -1;
    if (!aUp && bUp) return 1;
    return aUp ? aDate - bDate : bDate - aDate;
  });

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>

      {/* ── Hero ──────────────────────────────────────────────── */}
      <section style={{ padding: '40px 24px 32px', textAlign: 'center',
        background: 'radial-gradient(ellipse at 50% 0%, rgba(200,145,58,0.08) 0%, transparent 70%)' }}>
        <h1 className="font-display" style={{ fontSize: 30, fontWeight: 400, color: 'var(--text-primary)', margin: 0, lineHeight: 1.2 }}>
          Your Sessions
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8, lineHeight: 1.6 }}>
          Manage consultations with your astrologers
        </p>
      </section>

      {/* ── Tabs ──────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 4, padding: '4px', background: 'var(--card)',
        borderRadius: 12, margin: '0 0 28px', border: '1px solid var(--border)' }}>
        {TABS.map((tab) => {
          const active = activeTab === tab;
          return (
            <button key={tab} type="button" onClick={() => setActiveTab(tab)}
              style={{ flex: 1, padding: '9px 16px', borderRadius: 9, border: 'none', cursor: 'pointer',
                fontSize: 13, fontWeight: 500, transition: 'all 0.2s',
                background: active ? 'var(--gold)' : 'transparent',
                color: active ? 'var(--primary-foreground)' : 'var(--text-muted)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
              {tab}
              {tab === 'Upcoming' && upcomingCount > 0 && (
                <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  minWidth: 18, height: 18, padding: '0 5px', borderRadius: 20, fontSize: 10, fontWeight: 700,
                  background: active ? 'rgba(0,0,0,0.2)' : 'rgba(200,145,58,0.15)',
                  color: active ? 'var(--primary-foreground)' : 'var(--gold)' }}>
                  {upcomingCount}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* ── Content ───────────────────────────────────────────── */}
      {isLoading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {Array.from({ length: 4 }).map((_, i) => <ConsultationSkeleton key={i} />)}
        </div>
      ) : isError ? (
        <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
          padding: '48px 24px', textAlign: 'center' }}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>
            Failed to load consultations. Please try again later.
          </p>
        </div>
      ) : sorted.length === 0 ? (
        /* ── Empty State ──────────────────────────────────────── */
        <div style={{ borderRadius: 14, padding: '48px 24px', textAlign: 'center', position: 'relative',
          background: 'var(--card)', border: '1px solid var(--border)', overflow: 'hidden' }}>
          {/* Atmospheric glow */}
          <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none',
            background: 'radial-gradient(ellipse at 50% 20%, rgba(200,145,58,0.06) 0%, transparent 60%)' }} />

          <div style={{ position: 'relative' }}>
            <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(200,145,58,0.1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
              <Calendar style={{ width: 28, height: 28, color: 'var(--gold)' }} />
            </div>

            <h2 className="font-display" style={{ fontSize: 22, fontWeight: 400, color: 'var(--text-primary)', margin: 0 }}>
              Begin Your Journey
            </h2>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8, lineHeight: 1.6, maxWidth: 380, marginInline: 'auto' }}>
              Connect with a verified astrologer for personalized guidance on your chart, life path, and spiritual growth.
            </p>

            {/* Consultation type cards */}
            <div style={{ display: 'flex', gap: 14, marginTop: 28 }}>
              <TypeCard icon={Video} title="Video Session"
                desc="Face-to-face chart reading with screen sharing"
                price="From &#8377;1,200" grad="linear-gradient(135deg,#3B82F6,#60A5FA)" />
              <TypeCard icon={MessageSquare} title="Live Chat"
                desc="Real-time text guidance for quick questions"
                price="From &#8377;500" grad="linear-gradient(135deg,#7C3AED,#A855F7)" />
              <TypeCard icon={Phone} title="Voice Call"
                desc="Audio consultations, perfect for on-the-go"
                price="From &#8377;800" grad="linear-gradient(135deg,#059669,#34D399)" />
            </div>

            {/* CTA */}
            <div style={{ marginTop: 28 }}>
              <Link href="/astrologers">
                <button type="button" style={{ padding: '10px 28px', borderRadius: 8, border: 'none',
                  background: 'var(--gold)', color: 'var(--primary-foreground)', fontSize: 14, fontWeight: 600, cursor: 'pointer',
                  transition: 'opacity 0.2s, box-shadow 0.2s', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.boxShadow = '0 0 20px rgba(200,145,58,0.3)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.boxShadow = 'none'; }}>
                  Browse Astrologers <ArrowRight style={{ width: 16, height: 16 }} />
                </button>
              </Link>
            </div>

            <p style={{ marginTop: 16, fontSize: 11, color: 'var(--text-faint)' }}>
              Your upcoming and past sessions will appear here
            </p>
          </div>
        </div>
      ) : (
        /* ── Consultation List ────────────────────────────────── */
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {sorted.map((c) => (
            <ConsultationCard key={c.consultation_id} consultation={c} />
          ))}
        </div>
      )}

      {/* ── Inline keyframes ──────────────────────────────────── */}
      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
        @media(max-width:640px) {
          div[style*="flex"][style*="gap: 14"] > div[style*="flex: 1 1 0"] {
            min-width: 100% !important;
          }
        }
      `}</style>
    </div>
  );
}
