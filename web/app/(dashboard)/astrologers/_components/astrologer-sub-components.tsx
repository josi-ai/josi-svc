'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, X, BadgeCheck, Clock, Globe, Users, Sparkles, Video, MessageSquare, Phone, FileText, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { type Astrologer, TAG_CLR, AVATAR_GRAD, fmtRate } from './astrologer-types';

/* ── Dropdown ──────────────────────────────────────────────────── */

export function Dropdown({ label, value, options, onChange }: {
  label: string; value: string; options: string[]; onChange: (v: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);

  const focusRing = open ? { borderColor: 'var(--gold)', boxShadow: '0 0 0 2px rgba(200,145,58,0.15)' } : {};
  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button type="button" onClick={() => setOpen(!open)} style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%',
        height: 40, padding: '0 12px', background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, color: value ? 'var(--text-primary)' : 'var(--text-muted)', fontSize: 13,
        cursor: 'pointer', transition: 'border-color 0.2s, box-shadow 0.2s', outline: 'none', ...focusRing,
      }}>
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{value || label}</span>
        <ChevronDown style={{ width: 14, height: 14, flexShrink: 0, marginLeft: 8, color: 'var(--text-faint)',
          transition: 'transform 0.2s', transform: open ? 'rotate(180deg)' : 'none' }} />
      </button>
      {open && (
        <div style={{ position: 'absolute', top: 'calc(100% + 4px)', left: 0, right: 0, zIndex: 50,
          background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
          boxShadow: 'var(--shadow-dropdown)', overflow: 'hidden' }}>
          {['', ...options].map((opt) => {
            const active = value === opt;
            const display = opt || `All ${label}s`;
            return (
              <button key={opt} type="button" onClick={() => { onChange(opt); setOpen(false); }}
                style={{ display: 'block', width: '100%', padding: '9px 12px', textAlign: 'left', fontSize: 13,
                  color: active ? 'var(--gold)' : opt ? 'var(--text-primary)' : 'var(--text-muted)',
                  background: active ? 'var(--gold-bg-subtle)' : 'transparent',
                  border: 'none', cursor: 'pointer', transition: 'background 0.15s' }}
                onMouseEnter={(e) => { if (!active) e.currentTarget.style.background = 'var(--card-hover)'; }}
                onMouseLeave={(e) => { if (!active) e.currentTarget.style.background = 'transparent'; }}>
                {display}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ── Filter Chip ───────────────────────────────────────────────── */

export function Chip({ label, onClear }: { label: string; onClear: () => void }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '4px 10px',
      borderRadius: 20, fontSize: 12, fontWeight: 500, background: 'rgba(200,145,58,0.1)',
      color: 'var(--gold)', border: '1px solid rgba(200,145,58,0.2)' }}>
      {label}
      <button type="button" onClick={onClear} style={{ background: 'none', border: 'none',
        padding: 0, cursor: 'pointer', display: 'flex', color: 'var(--gold)' }}>
        <X style={{ width: 12, height: 12 }} />
      </button>
    </span>
  );
}

/* ── Stars ──────────────────────────────────────────────────────── */

export function Stars({ rating, reviews }: { rating: number; reviews: number }) {
  const full = Math.round(rating);
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
      <span style={{ color: 'var(--gold)', fontSize: 13, letterSpacing: 1 }}>{'★'.repeat(full)}</span>
      {full < 5 && <span style={{ color: 'var(--text-faint)', fontSize: 13, letterSpacing: 1 }}>{'★'.repeat(5 - full)}</span>}
      <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 2 }}>
        {rating.toFixed(1)} ({reviews.toLocaleString()})
      </span>
    </span>
  );
}

/* ── Tag Pill ──────────────────────────────────────────────────── */

export function Tag({ label }: { label: string }) {
  const [bg, fg] = TAG_CLR[label] || ['rgba(100,100,100,0.12)', 'var(--text-secondary)'];
  return (
    <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 20, fontSize: 10,
      fontWeight: 600, letterSpacing: 0.3, background: bg, color: fg, lineHeight: '18px' }}>
      {label}
    </span>
  );
}

/* ── Astrologer Card ───────────────────────────────────────────── */

export function AstrologerCard({ a }: { a: Astrologer }) {
  const grad = AVATAR_GRAD[a.professional_name.charAt(0).toUpperCase()] || 'linear-gradient(135deg,#6366F1,#818CF8)';
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)',
      borderLeft: a.is_featured ? '3px solid var(--gold)' : '1px solid var(--border)',
      borderRadius: 14, padding: 20, transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s' }}
      onMouseEnter={(e) => { const s = e.currentTarget.style; s.transform = 'translateY(-2px)'; s.boxShadow = '0 4px 24px rgba(0,0,0,0.2)'; s.borderColor = 'rgba(200,145,58,0.25)'; }}
      onMouseLeave={(e) => { const s = e.currentTarget.style; s.transform = ''; s.boxShadow = ''; s.borderColor = 'var(--border)'; }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
        <div style={{ width: 56, height: 56, borderRadius: '50%', background: grad, display: 'flex',
          alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 22, fontWeight: 600, color: '#fff' }}>
          {a.professional_name.charAt(0)}
        </div>
        <div style={{ minWidth: 0, flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <h3 className="font-display" style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)',
              margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {a.professional_name}
            </h3>
            {a.verification_status_name === 'Verified' && (
              <BadgeCheck style={{ width: 16, height: 16, color: 'var(--gold)', flexShrink: 0 }} />
            )}
            {a.is_featured && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, padding: '1px 8px',
                borderRadius: 20, fontSize: 9, fontWeight: 700, letterSpacing: 0.8, textTransform: 'uppercase',
                background: 'rgba(200,145,58,0.15)', color: 'var(--gold)' }}>
                <Sparkles style={{ width: 10, height: 10 }} /> Featured
              </span>
            )}
          </div>
          <div style={{ marginTop: 4 }}><Stars rating={a.rating} reviews={a.total_reviews} /></div>
        </div>
      </div>
      {a.bio && (
        <p style={{ marginTop: 14, fontSize: 13, lineHeight: 1.6, color: 'var(--text-muted)',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {a.bio}
        </p>
      )}
      <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {a.specializations.slice(0, 4).map((s) => <Tag key={s} label={s} />)}
        {a.specializations.length > 4 && (
          <span style={{ fontSize: 10, color: 'var(--text-faint)', alignSelf: 'center' }}>+{a.specializations.length - 4}</span>
        )}
      </div>
      <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 14, fontSize: 12, color: 'var(--text-faint)' }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}><Clock style={{ width: 12, height: 12 }} />{a.years_experience}y exp</span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}><Globe style={{ width: 12, height: 12 }} />{a.languages.slice(0, 2).join(', ')}{a.languages.length > 2 && ` +${a.languages.length - 2}`}</span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}><Users style={{ width: 12, height: 12 }} />{a.total_consultations.toLocaleString()}</span>
      </div>
      <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>
          <span style={{ fontSize: 18, fontWeight: 700, color: 'var(--gold)' }}>{fmtRate(a.currency, a.hourly_rate)}</span>
          <span style={{ fontSize: 12, color: 'var(--text-faint)', marginLeft: 2 }}>/hr</span>
        </span>
        <Link href={`/astrologers/${a.astrologer_id}`}>
          <button type="button" style={{ padding: '7px 18px', borderRadius: 8,
            border: '1px solid rgba(200,145,58,0.4)', background: 'transparent', color: 'var(--gold)',
            fontSize: 13, fontWeight: 500, cursor: 'pointer', transition: 'all 0.2s' }}
            onMouseEnter={(e) => { const s = e.currentTarget.style; s.background = 'rgba(200,145,58,0.1)'; s.borderColor = 'var(--gold)'; s.boxShadow = '0 0 12px rgba(200,145,58,0.15)'; }}
            onMouseLeave={(e) => { const s = e.currentTarget.style; s.background = 'transparent'; s.borderColor = 'rgba(200,145,58,0.4)'; s.boxShadow = 'none'; }}>
            View Profile
          </button>
        </Link>
      </div>
    </div>
  );
}

/* ── Skeleton ──────────────────────────────────────────────────── */

export function AstrologerSkeleton() {
  const bar = (w: string, h: number, mt = 0) => (
    <div style={{ height: h, width: w, borderRadius: 6, background: 'var(--border)', marginTop: mt, animation: 'pulse 2s infinite' }} />
  );
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 20 }}>
      <div style={{ display: 'flex', gap: 14 }}>
        <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--border)', animation: 'pulse 2s infinite' }} />
        <div style={{ flex: 1 }}>{bar('60%', 16)}{bar('40%', 12, 10)}</div>
      </div>
      {bar('100%', 12, 16)}{bar('70%', 12, 8)}
      <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>{bar('52px', 22)}{bar('60px', 22)}</div>
    </div>
  );
}

/* ── Consultation Type Card ───────────────────────────────────── */

export function ConsultationTypeCard({ icon: Icon, title, desc, price }: {
  icon: React.ComponentType<{ style?: React.CSSProperties }>; title: string; desc: string; price: string;
}) {
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12,
      padding: 18, transition: 'border-color 0.2s', flex: '1 0 220px', minWidth: 200 }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(200,145,58,0.25)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; }}>
      <div style={{ width: 40, height: 40, borderRadius: 10, background: 'rgba(200,145,58,0.1)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
        <Icon style={{ width: 20, height: 20, color: 'var(--gold)' }} />
      </div>
      <h3 className="font-display" style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{title}</h3>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.5 }}>{desc}</p>
      <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--gold)', marginTop: 10 }}>{price}</p>
    </div>
  );
}
