'use client';

import React from 'react';
import { Calendar, Clock, ArrowRight, Video, MessageSquare, Phone } from 'lucide-react';
import Link from 'next/link';
import {
  type Consultation,
  TYPE_ICONS, TYPE_GRAD, STATUS_STYLE, AREA_CLR,
  formatDateTime,
} from './consultation-types';

/* ── Skeleton ──────────────────────────────────────────────────── */

export function ConsultationSkeleton() {
  const bar = (w: string, h: number, mt = 0) => (
    <div style={{ height: h, width: w, borderRadius: 6, background: 'var(--border)', marginTop: mt, animation: 'pulse 2s infinite' }} />
  );
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 20 }}>
      <div style={{ display: 'flex', gap: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'var(--border)', animation: 'pulse 2s infinite', flexShrink: 0 }} />
        <div style={{ flex: 1 }}>{bar('55%', 16)}{bar('40%', 12, 10)}</div>
        <div style={{ width: 72, height: 24, borderRadius: 20, background: 'var(--border)', animation: 'pulse 2s infinite' }} />
      </div>
      <div style={{ display: 'flex', gap: 16, marginTop: 16 }}>{bar('120px', 12)}{bar('80px', 12)}</div>
      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>{bar('60px', 22)}{bar('72px', 22)}</div>
    </div>
  );
}

/* ── Consultation Card ─────────────────────────────────────────── */

export function ConsultationCard({ consultation }: { consultation: Consultation }) {
  const dt = formatDateTime(consultation.scheduled_at);
  const TypeIcon = TYPE_ICONS[consultation.consultation_type_name] ?? MessageSquare;
  const grad = TYPE_GRAD[consultation.consultation_type_name] ?? TYPE_GRAD.Email;
  const status = STATUS_STYLE[consultation.status_name] ?? STATUS_STYLE.Pending;
  const isLive = consultation.status_name === 'In Progress' || consultation.status_name === 'Scheduled';

  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 20, transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s' }}
      onMouseEnter={(e) => { const s = e.currentTarget.style; s.transform = 'translateY(-1px)'; s.boxShadow = '0 4px 20px rgba(0,0,0,0.18)'; s.borderColor = 'rgba(200,145,58,0.2)'; }}
      onMouseLeave={(e) => { const s = e.currentTarget.style; s.transform = ''; s.boxShadow = ''; s.borderColor = 'var(--border)'; }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: '50%', background: grad, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <TypeIcon style={{ width: 20, height: 20, color: '#fff' }} />
        </div>
        <div style={{ minWidth: 0, flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <h3 className="font-display" style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{consultation.consultation_type_name} Consultation</h3>
            <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: 20, fontSize: 10, fontWeight: 600, letterSpacing: 0.3, background: status.bg, color: status.fg, border: status.border, lineHeight: '18px' }}>{consultation.status_name}</span>
          </div>
          <p style={{ marginTop: 4, fontSize: 12, color: 'var(--text-faint)' }}>Astrologer: {consultation.astrologer_id.slice(0, 8)}...</p>
          <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 14, fontSize: 12, color: 'var(--text-muted)' }}>
            {dt && <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}><Calendar style={{ width: 13, height: 13, color: 'rgba(200,145,58,0.6)' }} />{dt.date}</span>}
            {dt && <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}><Clock style={{ width: 13, height: 13, color: 'rgba(200,145,58,0.6)' }} />{dt.time}</span>}
            {consultation.duration_minutes && <span>{consultation.duration_minutes} min</span>}
            {consultation.total_amount != null && (
              <span style={{ fontWeight: 600, color: 'var(--gold)' }}>
                {consultation.currency === 'USD' ? '$' : consultation.currency === 'INR' ? '\u20B9' : consultation.currency}{consultation.total_amount}
              </span>
            )}
          </div>
          {consultation.focus_areas && consultation.focus_areas.length > 0 && (
            <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {consultation.focus_areas.slice(0, 3).map((area) => {
                const [bg, fg] = AREA_CLR[area] || ['rgba(100,100,100,0.08)', 'var(--text-muted)'];
                return <span key={area} style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 20, fontSize: 10, fontWeight: 600, letterSpacing: 0.3, background: bg, color: fg, lineHeight: '18px' }}>{area}</span>;
              })}
            </div>
          )}
          {consultation.ai_summary && (
            <p style={{ marginTop: 10, fontSize: 12, lineHeight: 1.5, color: 'var(--text-muted)', fontStyle: 'italic', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{consultation.ai_summary}</p>
          )}
        </div>
        <div style={{ flexShrink: 0, alignSelf: 'center' }}>
          <Link href={`/consultations/${consultation.consultation_id}`}>
            {isLive ? (
              <button type="button" style={{ padding: '8px 18px', borderRadius: 8, border: 'none', background: 'var(--gold)', color: 'var(--primary-foreground)', fontSize: 13, fontWeight: 600, cursor: 'pointer', transition: 'opacity 0.2s, box-shadow 0.2s', display: 'inline-flex', alignItems: 'center', gap: 5 }}
                onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.boxShadow = '0 0 16px rgba(200,145,58,0.3)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.boxShadow = 'none'; }}>
                Join <ArrowRight style={{ width: 14, height: 14 }} />
              </button>
            ) : (
              <button type="button" style={{ padding: '8px 18px', borderRadius: 8, border: '1px solid rgba(200,145,58,0.4)', background: 'transparent', color: 'var(--gold)', fontSize: 13, fontWeight: 500, cursor: 'pointer', transition: 'all 0.2s' }}
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

/* ── Consultation Type Card (empty state) ────────────────────── */

export function TypeCard({ icon: Icon, title, desc, price, grad }: {
  icon: React.ComponentType<{ style?: React.CSSProperties }>; title: string; desc: string; price: string; grad: string;
}) {
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12, padding: 20, textAlign: 'center', transition: 'border-color 0.2s', flex: '1 1 0' }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(200,145,58,0.25)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; }}>
      <div style={{ width: 44, height: 44, borderRadius: '50%', background: grad, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px' }}>
        <Icon style={{ width: 20, height: 20, color: '#fff' }} />
      </div>
      <h3 className="font-display" style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{title}</h3>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.5 }}>{desc}</p>
      <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--gold)', marginTop: 10 }}>{price}</p>
    </div>
  );
}
