'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Calendar, ArrowRight, Video, MessageSquare, Phone } from 'lucide-react';
import Link from 'next/link';
import {
  type ConsultationsResponse, TABS, type Tab,
  isUpcoming, isPast,
} from './_components/consultation-types';
import { ConsultationSkeleton, ConsultationCard, TypeCard } from './_components/consultation-sub-components';

export default function ConsultationsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('All');

  const { data, isLoading, isError } = useQuery({
    queryKey: ['my-consultations'],
    queryFn: () => apiClient.get<ConsultationsResponse>('/api/v1/consultations/my-consultations?limit=50'),
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
      {/* Hero */}
      <section style={{ padding: '40px 24px 32px', textAlign: 'center',
        background: 'radial-gradient(ellipse at 50% 0%, rgba(200,145,58,0.08) 0%, transparent 70%)' }}>
        <h1 className="font-display" style={{ fontSize: 30, fontWeight: 400, color: 'var(--text-primary)', margin: 0, lineHeight: 1.2 }}>Your Sessions</h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8, lineHeight: 1.6 }}>Manage consultations with your astrologers</p>
      </section>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, padding: '4px', background: 'var(--card)', borderRadius: 12, margin: '0 0 28px', border: '1px solid var(--border)' }}>
        {TABS.map((tab) => {
          const active = activeTab === tab;
          return (
            <button key={tab} type="button" onClick={() => setActiveTab(tab)}
              style={{ flex: 1, padding: '9px 16px', borderRadius: 9, border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 500, transition: 'all 0.2s',
                background: active ? 'var(--gold)' : 'transparent', color: active ? 'var(--primary-foreground)' : 'var(--text-muted)',
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

      {/* Content */}
      {isLoading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {Array.from({ length: 4 }).map((_, i) => <ConsultationSkeleton key={i} />)}
        </div>
      ) : isError ? (
        <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: '48px 24px', textAlign: 'center' }}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>Failed to load consultations. Please try again later.</p>
        </div>
      ) : sorted.length === 0 ? (
        <div style={{ borderRadius: 14, padding: '48px 24px', textAlign: 'center', position: 'relative', background: 'var(--card)', border: '1px solid var(--border)', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', background: 'radial-gradient(ellipse at 50% 20%, rgba(200,145,58,0.06) 0%, transparent 60%)' }} />
          <div style={{ position: 'relative' }}>
            <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(200,145,58,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
              <Calendar style={{ width: 28, height: 28, color: 'var(--gold)' }} />
            </div>
            <h2 className="font-display" style={{ fontSize: 22, fontWeight: 400, color: 'var(--text-primary)', margin: 0 }}>Begin Your Journey</h2>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8, lineHeight: 1.6, maxWidth: 380, marginInline: 'auto' }}>
              Connect with a verified astrologer for personalized guidance on your chart, life path, and spiritual growth.
            </p>
            <div style={{ display: 'flex', gap: 14, marginTop: 28 }}>
              <TypeCard icon={Video} title="Video Session" desc="Face-to-face chart reading with screen sharing" price="From &#8377;1,200" grad="linear-gradient(135deg,#3B82F6,#60A5FA)" />
              <TypeCard icon={MessageSquare} title="Live Chat" desc="Real-time text guidance for quick questions" price="From &#8377;500" grad="linear-gradient(135deg,#7C3AED,#A855F7)" />
              <TypeCard icon={Phone} title="Voice Call" desc="Audio consultations, perfect for on-the-go" price="From &#8377;800" grad="linear-gradient(135deg,#059669,#34D399)" />
            </div>
            <div style={{ marginTop: 28 }}>
              <Link href="/astrologers">
                <button type="button" style={{ padding: '10px 28px', borderRadius: 8, border: 'none', background: 'var(--gold)', color: 'var(--primary-foreground)', fontSize: 14, fontWeight: 600, cursor: 'pointer', transition: 'opacity 0.2s, box-shadow 0.2s', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.boxShadow = '0 0 20px rgba(200,145,58,0.3)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.boxShadow = 'none'; }}>
                  Browse Astrologers <ArrowRight style={{ width: 16, height: 16 }} />
                </button>
              </Link>
            </div>
            <p style={{ marginTop: 16, fontSize: 11, color: 'var(--text-faint)' }}>Your upcoming and past sessions will appear here</p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {sorted.map((c) => <ConsultationCard key={c.consultation_id} consultation={c} />)}
        </div>
      )}

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
        @media(max-width:640px) { div[style*="flex"][style*="gap: 14"] > div[style*="flex: 1 1 0"] { min-width: 100% !important; } }
      `}</style>
    </div>
  );
}
