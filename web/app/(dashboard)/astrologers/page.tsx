'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Search, Users, Sparkles, Video, MessageSquare, Phone, FileText, ArrowRight } from 'lucide-react';
import {
  type Astrologer, type SearchResponse,
  DEMO_ASTROLOGERS, TRADITIONS, LANGUAGES, RATINGS,
} from './_components/astrologer-types';
import { Dropdown, Chip, AstrologerCard, AstrologerSkeleton, ConsultationTypeCard } from './_components/astrologer-sub-components';

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
      {/* Hero */}
      <section style={{ padding: '48px 24px 40px', textAlign: 'center',
        background: 'radial-gradient(ellipse at 50% 0%, rgba(200,145,58,0.08) 0%, transparent 70%)', marginBottom: 32 }}>
        <h1 className="font-display" style={{ fontSize: 32, fontWeight: 400, color: 'var(--text-primary)', margin: 0, lineHeight: 1.2 }}>Find Your Guide</h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 10, lineHeight: 1.6, maxWidth: 440, marginInline: 'auto' }}>
          Verified astrologers across six traditions, ready for one-on-one sessions
        </p>
      </section>

      {/* Filters */}
      <section style={{ marginBottom: 24, padding: '0 4px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
          <div style={{ position: 'relative' }}>
            <Search style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', width: 14, height: 14, color: 'var(--text-faint)', pointerEvents: 'none' }} />
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
            <button type="button" onClick={clearAll} style={{ fontSize: 12, color: 'var(--gold)', background: 'none', border: 'none', cursor: 'pointer', padding: '4px 0' }}>Clear all</button>
          </div>
        )}
      </section>

      {/* Demo banner */}
      {isDemo && !hasFilters && (
        <div style={{ margin: '0 4px 20px', padding: '10px 16px', borderRadius: 10,
          background: 'rgba(200,145,58,0.06)', border: '1px solid rgba(200,145,58,0.12)',
          textAlign: 'center', fontSize: 12, color: 'var(--text-muted)' }}>
          <Sparkles style={{ width: 14, height: 14, display: 'inline', verticalAlign: -2, marginRight: 6, color: 'var(--gold)' }} />
          Featured astrologers — our marketplace is launching soon
        </div>
      )}

      {/* Grid */}
      <section style={{ padding: '0 4px', marginBottom: 40 }}>
        {isLoading ? (
          <div className="astro-grid">{Array.from({ length: 6 }).map((_, i) => <AstrologerSkeleton key={i} />)}</div>
        ) : filtered.length === 0 && hasFilters ? (
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: '56px 24px', textAlign: 'center' }}>
            <Users style={{ width: 36, height: 36, color: 'var(--text-faint)', margin: '0 auto 12px' }} />
            <h3 className="font-display" style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 6px' }}>No astrologers found</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '0 0 16px' }}>Try adjusting your filters to see more results.</p>
            <button type="button" onClick={clearAll} style={{ padding: '8px 20px', borderRadius: 8, border: '1px solid rgba(200,145,58,0.4)', background: 'transparent', color: 'var(--gold)', fontSize: 13, cursor: 'pointer' }}>Clear Filters</button>
          </div>
        ) : (
          <div className="astro-grid">{filtered.map((a) => <AstrologerCard key={a.astrologer_id} a={a} />)}</div>
        )}
      </section>

      {/* Consultation Types */}
      <section style={{ padding: '0 4px', marginBottom: 40 }}>
        <h2 className="font-display" style={{ fontSize: 20, fontWeight: 400, color: 'var(--text-primary)', margin: '0 0 16px' }}>Consultation Types</h2>
        <div style={{ display: 'flex', gap: 14, overflowX: 'auto', paddingBottom: 4 }}>
          <ConsultationTypeCard icon={Video} title="Video Call" desc="Face-to-face with screen sharing for chart review" price="From &#8377;1,200/session" />
          <ConsultationTypeCard icon={MessageSquare} title="Live Chat" desc="Real-time text consultation for quick questions" price="From &#8377;500/session" />
          <ConsultationTypeCard icon={Phone} title="Voice Call" desc="Audio consultations, perfect for on-the-go" price="From &#8377;800/session" />
          <ConsultationTypeCard icon={FileText} title="Detailed Report" desc="Written analysis delivered within 48 hours" price="From &#8377;1,500/report" />
        </div>
      </section>

      {/* Join CTA */}
      <section style={{ margin: '0 4px 32px', borderRadius: 14, padding: '48px 24px', textAlign: 'center',
        background: 'radial-gradient(ellipse at 50% 50%, rgba(200,145,58,0.08) 0%, transparent 70%)',
        border: '1px solid rgba(200,145,58,0.12)' }}>
        <h2 className="font-display" style={{ fontSize: 22, fontWeight: 400, color: 'var(--text-primary)', margin: 0 }}>Are you a professional astrologer?</h2>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8, maxWidth: 400, marginInline: 'auto', lineHeight: 1.6 }}>
          Join our marketplace and connect with seekers worldwide. Grow your practice with tools built for modern astrologers.
        </p>
        <a href="mailto:astrologers@josiam.com">
          <button type="button" style={{ marginTop: 20, padding: '10px 28px', borderRadius: 8, border: 'none',
            background: 'var(--gold)', color: 'var(--primary-foreground)', fontSize: 14, fontWeight: 600, cursor: 'pointer',
            transition: 'opacity 0.2s, box-shadow 0.2s', display: 'inline-flex', alignItems: 'center', gap: 6 }}
            onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.9'; e.currentTarget.style.boxShadow = '0 0 20px rgba(200,145,58,0.3)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.boxShadow = 'none'; }}>
            Apply to Join <ArrowRight style={{ width: 16, height: 16 }} />
          </button>
        </a>
        <p style={{ marginTop: 14, fontSize: 11, color: 'var(--text-faint)' }}>Verified credentials &middot; 3+ years experience &middot; Background check</p>
      </section>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
        .astro-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:20px; }
        @media(max-width:768px) { .astro-grid { grid-template-columns:1fr !important; } section > div[style*="grid-template-columns: repeat(4"] { grid-template-columns:repeat(2,1fr) !important; } }
        @media(max-width:480px) { section > div[style*="grid-template-columns: repeat(2"] { grid-template-columns:1fr !important; } }
      `}</style>
    </div>
  );
}
