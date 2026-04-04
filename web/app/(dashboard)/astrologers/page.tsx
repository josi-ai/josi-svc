'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Search, ChevronDown, Clock, Globe, BadgeCheck, Users, Sparkles, Video, MessageSquare, Phone, FileText, ArrowRight, X } from 'lucide-react';
import Link from 'next/link';

/* ── Types ─────────────────────────────────────────────────────── */

interface Astrologer {
  astrologer_id: string; user_id: string; professional_name: string;
  bio: string | null; years_experience: number; specializations: string[];
  languages: string[]; hourly_rate: number; currency: string; rating: number;
  total_consultations: number; total_reviews: number; verification_status_id: number;
  verification_status_name: string; is_active: boolean; is_featured: boolean;
  profile_image_url: string | null; joined_at: string;
}
interface SearchResponse { astrologers: Astrologer[]; total: number; limit: number; offset: number; }

/* ── Demo Data ─────────────────────────────────────────────────── */

const mk = (id: string, uid: string, name: string, bio: string, yrs: number, specs: string[], langs: string[], rate: number, cur: string, rat: number, cons: number, revs: number, feat: boolean, joined: string): Astrologer => ({
  astrologer_id: id, user_id: uid, professional_name: name, bio, years_experience: yrs,
  specializations: specs, languages: langs, hourly_rate: rate, currency: cur, rating: rat,
  total_consultations: cons, total_reviews: revs, verification_status_id: 2,
  verification_status_name: 'Verified', is_active: true, is_featured: feat,
  profile_image_url: null, joined_at: joined,
});

const DEMO_ASTROLOGERS: Astrologer[] = [
  mk('demo-1','u1','Priya Shankar','Renowned Vedic astrologer specializing in predictive techniques and relationship compatibility analysis with a deep foundation in Parashari and Jaimini systems.',15,['Vedic','Predictive','Relationship'],['Tamil','English'],1500,'INR',4.9,2340,487,false,'2023-06-15'),
  mk('demo-2','u2','Dr. Rajesh Sharma','PhD in Jyotish Shastra with dual expertise in Vedic and Western systems. Specializes in career timing, medical astrology, and karmic pattern analysis.',22,['Career','Medical','Karmic'],['Hindi','English'],2000,'INR',4.8,3120,612,false,'2022-11-01'),
  mk('demo-3','u3','Sarah Chen','Bridging Eastern and Western traditions with expertise in Chinese BaZi, Zi Wei Dou Shu, and modern Western psychological astrology.',10,['Chinese','Western','Spiritual'],['English','Mandarin'],75,'USD',4.7,1250,298,false,'2024-01-20'),
  mk('demo-4','u4','Meenakshi Iyer','Third-generation Vedic astrologer with deep expertise in Nadi astrology and relationship counseling rooted in classical Jyotish traditions.',18,['Vedic','Relationship','Spiritual'],['Tamil','Malayalam','English'],1200,'INR',4.9,1870,401,false,'2023-03-10'),
  mk('demo-5','u5','David Williams','Classical astrologer blending Hellenistic time-lord techniques with modern Western chart interpretation for precise life-event timing.',12,['Western','Hellenistic','Predictive'],['English'],60,'USD',4.6,980,215,false,'2023-09-05'),
  mk('demo-6','u6','Lakshmi Narayanan','One of India\u2019s most respected Vedic astrologers with 25 years of practice. Known for precise karmic analysis and medical astrology consultations.',25,['Vedic','Karmic','Medical'],['Tamil','Hindi','English'],2500,'INR',5.0,5200,1038,true,'2022-05-01'),
];

/* ── Constants ─────────────────────────────────────────────────── */

const TRADITIONS = ['Vedic', 'Western', 'Chinese', 'Hellenistic'];
const LANGUAGES = ['English', 'Hindi', 'Tamil', 'Malayalam', 'Mandarin'];
const RATINGS = ['4.5+', '4.0+', '3.5+'];

const AVATAR_GRAD: Record<string, string> = {
  P: 'linear-gradient(135deg,#7C3AED,#A855F7)', D: 'linear-gradient(135deg,#0891B2,#22D3EE)',
  S: 'linear-gradient(135deg,#059669,#34D399)', M: 'linear-gradient(135deg,#DB2777,#F472B6)',
  L: 'linear-gradient(135deg,#C8913A,#E0B060)',
};

const TAG_CLR: Record<string, [string, string]> = {
  Vedic: ['rgba(200,145,58,0.12)','#D4A04A'], Western: ['rgba(106,159,216,0.12)','#6A9FD8'],
  Chinese: ['rgba(220,80,80,0.12)','#E07070'], Hellenistic: ['rgba(80,184,208,0.12)','#50B8D0'],
  Medical: ['rgba(106,175,122,0.12)','#6AAF7A'], Karmic: ['rgba(150,120,200,0.12)','#9678C8'],
  Relationship: ['rgba(218,122,148,0.12)','#DA7A94'], Career: ['rgba(80,160,210,0.12)','#50A0D2'],
  Spiritual: ['rgba(80,176,152,0.12)','#50B098'], Predictive: ['rgba(224,168,72,0.12)','#E0A848'],
};

function fmtRate(cur: string, r: number) {
  return cur === 'USD' ? `$${r}` : cur === 'INR' ? `\u20B9${r.toLocaleString('en-IN')}` : `${cur} ${r}`;
}

/* ── Dropdown ──────────────────────────────────────────────────── */

function Dropdown({ label, value, options, onChange }: {
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

function Chip({ label, onClear }: { label: string; onClear: () => void }) {
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

function Stars({ rating, reviews }: { rating: number; reviews: number }) {
  const full = Math.round(rating);
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
      <span style={{ color: '#C8913A', fontSize: 13, letterSpacing: 1 }}>{'★'.repeat(full)}</span>
      {full < 5 && <span style={{ color: 'var(--text-faint)', fontSize: 13, letterSpacing: 1 }}>{'★'.repeat(5 - full)}</span>}
      <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 2 }}>
        {rating.toFixed(1)} ({reviews.toLocaleString()})
      </span>
    </span>
  );
}

/* ── Tag Pill ──────────────────────────────────────────────────── */

function Tag({ label }: { label: string }) {
  const [bg, fg] = TAG_CLR[label] || ['rgba(100,100,100,0.12)', 'var(--text-secondary)'];
  return (
    <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 20, fontSize: 10,
      fontWeight: 600, letterSpacing: 0.3, background: bg, color: fg, lineHeight: '18px' }}>
      {label}
    </span>
  );
}

/* ── Astrologer Card ───────────────────────────────────────────── */

function Card({ a }: { a: Astrologer }) {
  const grad = AVATAR_GRAD[a.professional_name.charAt(0).toUpperCase()] || 'linear-gradient(135deg,#6366F1,#818CF8)';
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)',
      borderLeft: a.is_featured ? '3px solid var(--gold)' : '1px solid var(--border)',
      borderRadius: 14, padding: 20, transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s' }}
      onMouseEnter={(e) => { const s = e.currentTarget.style; s.transform = 'translateY(-2px)'; s.boxShadow = '0 4px 24px rgba(0,0,0,0.2)'; s.borderColor = 'rgba(200,145,58,0.25)'; }}
      onMouseLeave={(e) => { const s = e.currentTarget.style; s.transform = ''; s.boxShadow = ''; s.borderColor = 'var(--border)'; }}>

      {/* Header */}
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

      {/* Bio */}
      {a.bio && (
        <p style={{ marginTop: 14, fontSize: 13, lineHeight: 1.6, color: 'var(--text-muted)',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {a.bio}
        </p>
      )}

      {/* Tags */}
      <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {a.specializations.slice(0, 4).map((s) => <Tag key={s} label={s} />)}
        {a.specializations.length > 4 && (
          <span style={{ fontSize: 10, color: 'var(--text-faint)', alignSelf: 'center' }}>
            +{a.specializations.length - 4}
          </span>
        )}
      </div>

      {/* Meta */}
      <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 14, fontSize: 12, color: 'var(--text-faint)' }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
          <Clock style={{ width: 12, height: 12 }} />{a.years_experience}y exp
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
          <Globe style={{ width: 12, height: 12 }} />{a.languages.slice(0, 2).join(', ')}
          {a.languages.length > 2 && ` +${a.languages.length - 2}`}
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
          <Users style={{ width: 12, height: 12 }} />{a.total_consultations.toLocaleString()}
        </span>
      </div>

      {/* Footer */}
      <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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

function Skel() {
  const bar = (w: string, h: number, mt = 0) => (
    <div style={{ height: h, width: w, borderRadius: 6, background: 'var(--border)', marginTop: mt,
      animation: 'pulse 2s infinite' }} />
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

/* ── Consultation Card ─────────────────────────────────────────── */

function ConCard({ icon: Icon, title, desc, price }: {
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

/* ═════════════════════════════════════════════════════════════════
   Main Page
   ═════════════════════════════════════════════════════════════════ */

export default function AstrologersPage() {
  const [searchName, setSearchName] = useState('');
  const [tradition, setTradition] = useState('');
  const [language, setLanguage] = useState('');
  const [ratingFilter, setRatingFilter] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['astrologers', 'marketplace'],
    queryFn: () => apiClient.get<SearchResponse>('/api/v1/astrologers/search?limit=20'),
    retry: false,
  });

  const apiData = data?.data?.astrologers || data?.data || [];
  const astrologers: Astrologer[] = Array.isArray(apiData) && apiData.length > 0 ? apiData : DEMO_ASTROLOGERS;
  const isDemo = !Array.isArray(apiData) || apiData.length === 0;

  const filtered = useMemo(() => astrologers.filter((a) => {
    if (searchName && !a.professional_name.toLowerCase().includes(searchName.toLowerCase())) return false;
    if (tradition && !a.specializations.includes(tradition)) return false;
    if (language && !a.languages.includes(language)) return false;
    if (ratingFilter) { if (a.rating < parseFloat(ratingFilter)) return false; }
    return true;
  }), [astrologers, searchName, tradition, language, ratingFilter]);

  const hasFilters = !!(searchName || tradition || language || ratingFilter);
  const clearAll = () => { setSearchName(''); setTradition(''); setLanguage(''); setRatingFilter(''); };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>

      {/* ── Hero ──────────────────────────────────────────────── */}
      <section style={{ padding: '48px 24px 40px', textAlign: 'center',
        background: 'radial-gradient(ellipse at 50% 0%, rgba(200,145,58,0.08) 0%, transparent 70%)', marginBottom: 32 }}>
        <h1 className="font-display" style={{ fontSize: 32, fontWeight: 400, color: 'var(--text-primary)', margin: 0, lineHeight: 1.2 }}>
          Find Your Guide
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 10, lineHeight: 1.6, maxWidth: 440, marginInline: 'auto' }}>
          Verified astrologers across six traditions, ready for one-on-one sessions
        </p>
      </section>

      {/* ── Filters ───────────────────────────────────────────── */}
      <section style={{ marginBottom: 24, padding: '0 4px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
          <div style={{ position: 'relative' }}>
            <Search style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
              width: 14, height: 14, color: 'var(--text-faint)', pointerEvents: 'none' }} />
            <input type="text" placeholder="Search by name..." value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              style={{ width: '100%', height: 40, padding: '0 12px 0 34px', background: 'var(--card)',
                border: '1px solid var(--border)', borderRadius: 10, color: 'var(--text-primary)',
                fontSize: 13, outline: 'none', transition: 'border-color 0.2s, box-shadow 0.2s' }}
              onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--gold)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(200,145,58,0.15)'; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.boxShadow = 'none'; }} />
          </div>
          <Dropdown label="Tradition" value={tradition} options={TRADITIONS} onChange={setTradition} />
          <Dropdown label="Language" value={language} options={LANGUAGES} onChange={setLanguage} />
          <Dropdown label="Rating" value={ratingFilter} options={RATINGS} onChange={setRatingFilter} />
        </div>

        {hasFilters && (
          <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            {searchName && <Chip label={`"${searchName}"`} onClear={() => setSearchName('')} />}
            {tradition && <Chip label={tradition} onClear={() => setTradition('')} />}
            {language && <Chip label={language} onClear={() => setLanguage('')} />}
            {ratingFilter && <Chip label={`${ratingFilter} stars`} onClear={() => setRatingFilter('')} />}
            <button type="button" onClick={clearAll} style={{ fontSize: 12, color: 'var(--gold)',
              background: 'none', border: 'none', cursor: 'pointer', padding: '4px 0' }}>Clear all</button>
          </div>
        )}
      </section>

      {/* ── Demo banner ───────────────────────────────────────── */}
      {isDemo && !hasFilters && (
        <div style={{ margin: '0 4px 20px', padding: '10px 16px', borderRadius: 10,
          background: 'rgba(200,145,58,0.06)', border: '1px solid rgba(200,145,58,0.12)',
          textAlign: 'center', fontSize: 12, color: 'var(--text-muted)' }}>
          <Sparkles style={{ width: 14, height: 14, display: 'inline', verticalAlign: -2, marginRight: 6, color: 'var(--gold)' }} />
          Featured astrologers — our marketplace is launching soon
        </div>
      )}

      {/* ── Grid ──────────────────────────────────────────────── */}
      <section style={{ padding: '0 4px', marginBottom: 40 }}>
        {isLoading ? (
          <div className="astro-grid">{Array.from({ length: 6 }).map((_, i) => <Skel key={i} />)}</div>
        ) : filtered.length === 0 && hasFilters ? (
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
            padding: '56px 24px', textAlign: 'center' }}>
            <Users style={{ width: 36, height: 36, color: 'var(--text-faint)', margin: '0 auto 12px' }} />
            <h3 className="font-display" style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 6px' }}>
              No astrologers found
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '0 0 16px' }}>
              Try adjusting your filters to see more results.
            </p>
            <button type="button" onClick={clearAll} style={{ padding: '8px 20px', borderRadius: 8,
              border: '1px solid rgba(200,145,58,0.4)', background: 'transparent', color: 'var(--gold)',
              fontSize: 13, cursor: 'pointer' }}>Clear Filters</button>
          </div>
        ) : (
          <div className="astro-grid">{filtered.map((a) => <Card key={a.astrologer_id} a={a} />)}</div>
        )}
      </section>

      {/* ── Consultation Types ────────────────────────────────── */}
      <section style={{ padding: '0 4px', marginBottom: 40 }}>
        <h2 className="font-display" style={{ fontSize: 20, fontWeight: 400, color: 'var(--text-primary)', margin: '0 0 16px' }}>
          Consultation Types
        </h2>
        <div style={{ display: 'flex', gap: 14, overflowX: 'auto', paddingBottom: 4 }}>
          <ConCard icon={Video} title="Video Call" desc="Face-to-face with screen sharing for chart review" price="From &#8377;1,200/session" />
          <ConCard icon={MessageSquare} title="Live Chat" desc="Real-time text consultation for quick questions" price="From &#8377;500/session" />
          <ConCard icon={Phone} title="Voice Call" desc="Audio consultations, perfect for on-the-go" price="From &#8377;800/session" />
          <ConCard icon={FileText} title="Detailed Report" desc="Written analysis delivered within 48 hours" price="From &#8377;1,500/report" />
        </div>
      </section>

      {/* ── Join CTA ──────────────────────────────────────────── */}
      <section style={{ margin: '0 4px 32px', borderRadius: 14, padding: '48px 24px', textAlign: 'center',
        background: 'radial-gradient(ellipse at 50% 50%, rgba(200,145,58,0.08) 0%, transparent 70%)',
        border: '1px solid rgba(200,145,58,0.12)' }}>
        <h2 className="font-display" style={{ fontSize: 22, fontWeight: 400, color: 'var(--text-primary)', margin: 0 }}>
          Are you a professional astrologer?
        </h2>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8, maxWidth: 400, marginInline: 'auto', lineHeight: 1.6 }}>
          Join our marketplace and connect with seekers worldwide. Grow your practice with tools built for modern astrologers.
        </p>
        <a href="mailto:astrologers@josiam.com">
          <button type="button" style={{ marginTop: 20, padding: '10px 28px', borderRadius: 8, border: 'none',
            background: 'var(--gold)', color: '#000', fontSize: 14, fontWeight: 600, cursor: 'pointer',
            transition: 'opacity 0.2s, box-shadow 0.2s', display: 'inline-flex', alignItems: 'center', gap: 6 }}
            onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.boxShadow = '0 0 20px rgba(200,145,58,0.3)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.boxShadow = 'none'; }}>
            Apply to Join <ArrowRight style={{ width: 16, height: 16 }} />
          </button>
        </a>
        <p style={{ marginTop: 14, fontSize: 11, color: 'var(--text-faint)' }}>
          Verified credentials &middot; 3+ years experience &middot; Background check
        </p>
      </section>

      {/* ── Inline styles for grid + skeleton pulse ───────────── */}
      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
        .astro-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:20px; }
        @media(max-width:768px) {
          .astro-grid { grid-template-columns:1fr !important; }
          section > div[style*="grid-template-columns: repeat(4"] { grid-template-columns:repeat(2,1fr) !important; }
        }
        @media(max-width:480px) {
          section > div[style*="grid-template-columns: repeat(2"] { grid-template-columns:1fr !important; }
        }
      `}</style>
    </div>
  );
}
