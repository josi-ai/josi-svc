'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Search,
  Star,
  ChevronDown,
  Clock,
  Globe,
  BadgeCheck,
  Users,
  SlidersHorizontal,
  Sparkles,
  Calendar,
  Video,
  MessageSquare,
  Phone,
  FileText,
  ArrowRight,
} from 'lucide-react';
import Link from 'next/link';

/* ================================================================
   Types
   ================================================================ */

interface Astrologer {
  astrologer_id: string;
  user_id: string;
  professional_name: string;
  bio: string | null;
  years_experience: number;
  specializations: string[];
  languages: string[];
  hourly_rate: number;
  currency: string;
  rating: number;
  total_consultations: number;
  total_reviews: number;
  verification_status_id: number;
  verification_status_name: string;
  is_active: boolean;
  is_featured: boolean;
  profile_image_url: string | null;
  joined_at: string;
}

interface SearchResponse {
  astrologers: Astrologer[];
  total: number;
  limit: number;
  offset: number;
}

/* ================================================================
   Demo Data
   ================================================================ */

const DEMO_ASTROLOGERS: Astrologer[] = [
  {
    astrologer_id: 'demo-1',
    user_id: 'u1',
    professional_name: 'Priya Shankar',
    bio: 'Renowned Vedic astrologer specializing in predictive techniques and relationship compatibility analysis with a deep foundation in Parashari and Jaimini systems.',
    years_experience: 15,
    specializations: ['Vedic', 'Predictive', 'Relationship'],
    languages: ['Tamil', 'English'],
    hourly_rate: 1500,
    currency: 'INR',
    rating: 4.9,
    total_consultations: 2340,
    total_reviews: 487,
    verification_status_id: 2,
    verification_status_name: 'Verified',
    is_active: true,
    is_featured: false,
    profile_image_url: null,
    joined_at: '2023-06-15',
  },
  {
    astrologer_id: 'demo-2',
    user_id: 'u2',
    professional_name: 'Dr. Rajesh Sharma',
    bio: 'PhD in Jyotish Shastra with dual expertise in Vedic and Western systems. Specializes in career timing, medical astrology, and karmic pattern analysis.',
    years_experience: 22,
    specializations: ['Career', 'Medical', 'Karmic'],
    languages: ['Hindi', 'English'],
    hourly_rate: 2000,
    currency: 'INR',
    rating: 4.8,
    total_consultations: 3120,
    total_reviews: 612,
    verification_status_id: 2,
    verification_status_name: 'Verified',
    is_active: true,
    is_featured: false,
    profile_image_url: null,
    joined_at: '2022-11-01',
  },
  {
    astrologer_id: 'demo-3',
    user_id: 'u3',
    professional_name: 'Sarah Chen',
    bio: 'Bridging Eastern and Western traditions with expertise in Chinese BaZi, Zi Wei Dou Shu, and modern Western psychological astrology.',
    years_experience: 10,
    specializations: ['Chinese', 'Western', 'Spiritual'],
    languages: ['English', 'Mandarin'],
    hourly_rate: 75,
    currency: 'USD',
    rating: 4.7,
    total_consultations: 1250,
    total_reviews: 298,
    verification_status_id: 2,
    verification_status_name: 'Verified',
    is_active: true,
    is_featured: false,
    profile_image_url: null,
    joined_at: '2024-01-20',
  },
  {
    astrologer_id: 'demo-4',
    user_id: 'u4',
    professional_name: 'Meenakshi Iyer',
    bio: 'Third-generation Vedic astrologer with deep expertise in Nadi astrology and relationship counseling rooted in classical Jyotish traditions.',
    years_experience: 18,
    specializations: ['Vedic', 'Relationship', 'Spiritual'],
    languages: ['Tamil', 'Malayalam', 'English'],
    hourly_rate: 1200,
    currency: 'INR',
    rating: 4.9,
    total_consultations: 1870,
    total_reviews: 401,
    verification_status_id: 2,
    verification_status_name: 'Verified',
    is_active: true,
    is_featured: false,
    profile_image_url: null,
    joined_at: '2023-03-10',
  },
  {
    astrologer_id: 'demo-5',
    user_id: 'u5',
    professional_name: 'David Williams',
    bio: 'Classical astrologer blending Hellenistic time-lord techniques with modern Western chart interpretation for precise life-event timing.',
    years_experience: 12,
    specializations: ['Western', 'Hellenistic', 'Predictive'],
    languages: ['English'],
    hourly_rate: 60,
    currency: 'USD',
    rating: 4.6,
    total_consultations: 980,
    total_reviews: 215,
    verification_status_id: 2,
    verification_status_name: 'Verified',
    is_active: true,
    is_featured: false,
    profile_image_url: null,
    joined_at: '2023-09-05',
  },
  {
    astrologer_id: 'demo-6',
    user_id: 'u6',
    professional_name: 'Lakshmi Narayanan',
    bio: 'One of India\u2019s most respected Vedic astrologers with 25 years of practice. Known for precise karmic analysis and medical astrology consultations.',
    years_experience: 25,
    specializations: ['Vedic', 'Karmic', 'Medical'],
    languages: ['Tamil', 'Hindi', 'English'],
    hourly_rate: 2500,
    currency: 'INR',
    rating: 5.0,
    total_consultations: 5200,
    total_reviews: 1038,
    verification_status_id: 2,
    verification_status_name: 'Verified',
    is_active: true,
    is_featured: true,
    profile_image_url: null,
    joined_at: '2022-05-01',
  },
];

/* ================================================================
   Constants
   ================================================================ */

const SPECIALIZATIONS = [
  'Vedic', 'Western', 'Chinese', 'Hellenistic',
  'Medical', 'Karmic', 'Relationship', 'Career',
  'Spiritual', 'Predictive',
];

const TRADITIONS = ['Vedic', 'Western', 'Chinese', 'Hellenistic'];

const LANGUAGES = ['English', 'Hindi', 'Tamil', 'Malayalam', 'Mandarin'];

const AVATAR_COLORS: Record<string, string> = {
  P: '#7C3AED', // violet
  D: '#0891B2', // cyan
  S: '#059669', // emerald
  M: '#DB2777', // pink
  L: '#D97706', // amber
};

function getAvatarColor(name: string): string {
  const initial = name.charAt(0).toUpperCase();
  return AVATAR_COLORS[initial] || '#6366F1';
}

const SPEC_COLORS: Record<string, { bg: string; text: string }> = {
  Vedic:        { bg: 'rgba(217, 119, 6, 0.12)',  text: '#D97706' },
  Western:      { bg: 'rgba(99, 102, 241, 0.12)', text: '#818CF8' },
  Chinese:      { bg: 'rgba(220, 38, 38, 0.12)',  text: '#F87171' },
  Hellenistic:  { bg: 'rgba(139, 92, 246, 0.12)', text: '#A78BFA' },
  Medical:      { bg: 'rgba(5, 150, 105, 0.12)',  text: '#34D399' },
  Karmic:       { bg: 'rgba(168, 85, 247, 0.12)', text: '#C084FC' },
  Relationship: { bg: 'rgba(236, 72, 153, 0.12)', text: '#F472B6' },
  Career:       { bg: 'rgba(14, 165, 233, 0.12)', text: '#38BDF8' },
  Spiritual:    { bg: 'rgba(20, 184, 166, 0.12)', text: '#2DD4BF' },
  Predictive:   { bg: 'rgba(245, 158, 11, 0.12)', text: '#FBBF24' },
};

function formatRate(currency: string, rate: number): string {
  if (currency === 'USD') return `$${rate}`;
  if (currency === 'INR') return `\u20B9${rate.toLocaleString('en-IN')}`;
  return `${currency} ${rate}`;
}

/* ================================================================
   Sub-components
   ================================================================ */

function StarRating({ rating, reviews }: { rating: number; reviews: number }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((s) => (
          <Star
            key={s}
            className={`h-3.5 w-3.5 ${
              s <= Math.round(rating)
                ? 'fill-amber-400 text-amber-400'
                : 'fill-transparent text-text-faint'
            }`}
          />
        ))}
      </div>
      <span className="text-xs text-text-muted">
        {rating.toFixed(1)} ({reviews.toLocaleString()})
      </span>
    </div>
  );
}

function SpecBadge({ spec }: { spec: string }) {
  const colors = SPEC_COLORS[spec] || { bg: 'rgba(100,100,100,0.12)', text: 'var(--text-secondary)' };
  return (
    <span
      className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium"
      style={{ backgroundColor: colors.bg, color: colors.text }}
    >
      {spec}
    </span>
  );
}

function AstrologerCard({ astrologer }: { astrologer: Astrologer }) {
  const isVerified = astrologer.verification_status_name === 'Verified';
  const avatarBg = getAvatarColor(astrologer.professional_name);

  return (
    <div className="group rounded-2xl border border-border bg-card p-5 transition-all duration-200 hover:border-gold/30 hover:shadow-[0_0_24px_rgba(212,175,55,0.06)]">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-lg font-semibold text-white"
          style={{ backgroundColor: avatarBg }}
        >
          {astrologer.professional_name.charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 flex-wrap">
            <h3 className="truncate font-display text-sm font-semibold text-text-primary">
              {astrologer.professional_name}
            </h3>
            {isVerified && (
              <BadgeCheck className="h-4 w-4 shrink-0 text-blue" />
            )}
            {astrologer.is_featured && (
              <span
                className="inline-flex items-center rounded-full px-2 py-0 text-[10px] font-bold tracking-wide uppercase"
                style={{ backgroundColor: 'rgba(212, 175, 55, 0.15)', color: 'var(--gold)' }}
              >
                Featured
              </span>
            )}
          </div>
          <StarRating rating={astrologer.rating} reviews={astrologer.total_reviews} />
        </div>
      </div>

      {/* Bio snippet */}
      {astrologer.bio && (
        <p className="mt-3 line-clamp-2 text-xs text-text-muted leading-relaxed">
          {astrologer.bio}
        </p>
      )}

      {/* Specializations */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {astrologer.specializations.slice(0, 4).map((spec) => (
          <SpecBadge key={spec} spec={spec} />
        ))}
        {astrologer.specializations.length > 4 && (
          <span className="text-[10px] text-text-faint self-center">
            +{astrologer.specializations.length - 4} more
          </span>
        )}
      </div>

      {/* Meta row */}
      <div className="mt-3 flex items-center gap-3 text-xs text-text-muted">
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {astrologer.years_experience}y exp
        </span>
        <span className="flex items-center gap-1">
          <Globe className="h-3 w-3" />
          {astrologer.languages.slice(0, 2).join(', ')}
          {astrologer.languages.length > 2 && ` +${astrologer.languages.length - 2}`}
        </span>
        <span className="flex items-center gap-1">
          <Users className="h-3 w-3" />
          {astrologer.total_consultations.toLocaleString()}
        </span>
      </div>

      {/* Footer */}
      <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
        <span className="text-sm font-semibold text-text-primary">
          {formatRate(astrologer.currency, astrologer.hourly_rate)}
          <span className="text-xs font-normal text-text-muted">/hr</span>
        </span>
        <Link href={`/astrologers/${astrologer.astrologer_id}`}>
          <Button
            variant="outline"
            size="sm"
            className="border-gold/40 text-gold hover:bg-gold/10 hover:text-gold-bright"
          >
            View Profile
          </Button>
        </Link>
      </div>
    </div>
  );
}

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-10 w-full appearance-none rounded-lg border border-border bg-input px-3 pr-8 text-sm text-text-primary transition-colors focus:border-gold/60 focus:outline-none focus:ring-1 focus:ring-gold/50"
      >
        <option value="">{label}</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-faint" />
    </div>
  );
}

function AstrologerSkeleton() {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 animate-pulse">
      <div className="flex items-start gap-4">
        <div className="h-12 w-12 rounded-full bg-border" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-32 rounded bg-border" />
          <div className="h-3 w-48 rounded bg-border" />
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-3 w-full rounded bg-border" />
        <div className="h-3 w-2/3 rounded bg-border" />
      </div>
      <div className="mt-4 flex gap-2">
        <div className="h-6 w-16 rounded-full bg-border" />
        <div className="h-6 w-16 rounded-full bg-border" />
      </div>
    </div>
  );
}

/* ================================================================
   How It Works Card
   ================================================================ */

function HowItWorksCard({
  icon: Icon,
  step,
  title,
  description,
}: {
  icon: React.ComponentType<{ className?: string }>;
  step: number;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 text-center">
      <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full" style={{ backgroundColor: 'rgba(212, 175, 55, 0.1)' }}>
        <Icon className="h-5 w-5 text-gold" />
      </div>
      <div className="mb-1 text-[10px] font-bold uppercase tracking-widest text-text-faint">
        Step {step}
      </div>
      <h3 className="font-display text-sm font-semibold text-text-primary">{title}</h3>
      <p className="mt-1.5 text-xs text-text-muted leading-relaxed">{description}</p>
    </div>
  );
}

/* ================================================================
   Consultation Type Card
   ================================================================ */

function ConsultationCard({
  icon: Icon,
  title,
  description,
  price,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  price: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 transition-colors hover:border-gold/20">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg" style={{ backgroundColor: 'rgba(212, 175, 55, 0.1)' }}>
        <Icon className="h-5 w-5 text-gold" />
      </div>
      <h3 className="font-display text-sm font-semibold text-text-primary">{title}</h3>
      <p className="mt-1.5 text-xs text-text-muted leading-relaxed">{description}</p>
      <p className="mt-3 text-xs font-semibold text-gold">{price}</p>
    </div>
  );
}

/* ================================================================
   Main Page
   ================================================================ */

export default function AstrologersPage() {
  const [searchName, setSearchName] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [language, setLanguage] = useState('');
  const [tradition, setTradition] = useState('');

  /* --- Fetch from API (gracefully falls back to demo) --- */
  const { data, isLoading } = useQuery({
    queryKey: ['astrologers', 'marketplace'],
    queryFn: () => apiClient.get<SearchResponse>('/api/v1/astrologers/search?limit=20'),
    retry: false,
  });

  const apiAstrologers = data?.data?.astrologers || data?.data || [];
  const rawAstrologers: Astrologer[] = (Array.isArray(apiAstrologers) && apiAstrologers.length > 0)
    ? apiAstrologers
    : DEMO_ASTROLOGERS;
  const isDemo = !Array.isArray(apiAstrologers) || apiAstrologers.length === 0;

  /* --- Client-side filtering --- */
  const filtered = useMemo(() => {
    return rawAstrologers.filter((a) => {
      if (searchName && !a.professional_name.toLowerCase().includes(searchName.toLowerCase())) return false;
      if (specialization && !a.specializations.includes(specialization)) return false;
      if (language && !a.languages.includes(language)) return false;
      if (tradition && !a.specializations.includes(tradition)) return false;
      return true;
    });
  }, [rawAstrologers, searchName, specialization, language, tradition]);

  const hasFilters = !!(searchName || specialization || language || tradition);

  function clearFilters() {
    setSearchName('');
    setSpecialization('');
    setLanguage('');
    setTradition('');
  }

  return (
    <div className="space-y-8">
      {/* ============================================================
          Hero Section
          ============================================================ */}
      <section className="rounded-2xl border border-border bg-card px-6 py-10 text-center sm:px-12 sm:py-14">
        <h1 className="font-display text-display-lg text-text-primary leading-tight">
          Connect with Expert Astrologers
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-text-muted">
          Get personalized guidance from verified professionals across Vedic, Western,
          Chinese, and Hellenistic traditions
        </p>
        <div className="mt-5 flex items-center justify-center gap-3">
          <Badge variant="default">6 Traditions</Badge>
          <Badge variant="default">1-on-1 Sessions</Badge>
        </div>
      </section>

      {/* ============================================================
          How It Works
          ============================================================ */}
      <section>
        <h2 className="mb-4 font-display text-lg font-semibold text-text-primary">
          How It Works
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <HowItWorksCard
            icon={Search}
            step={1}
            title="Browse & Match"
            description="Find astrologers by tradition, language, specialization, and rating"
          />
          <HowItWorksCard
            icon={Calendar}
            step={2}
            title="Book a Session"
            description="Choose video, chat, or voice consultations at times that work for you"
          />
          <HowItWorksCard
            icon={Sparkles}
            step={3}
            title="Get Guidance"
            description="Receive personalized insights with your chart data shared securely"
          />
        </div>
      </section>

      {/* ============================================================
          Featured Astrologers
          ============================================================ */}
      <section>
        <h2 className="mb-4 font-display text-lg font-semibold text-text-primary">
          {isDemo ? 'Featured Astrologers' : 'Browse Astrologers'}
        </h2>

        {/* Search & Filters */}
        <div className="mb-5 rounded-2xl border border-border bg-card p-4">
          <div className="flex items-center gap-2 mb-3">
            <SlidersHorizontal className="h-4 w-4 text-text-muted" />
            <span className="text-xs font-medium uppercase tracking-wider text-text-faint">
              Search &amp; Filter
            </span>
            {hasFilters && (
              <button
                onClick={clearFilters}
                className="ml-auto text-xs text-gold hover:underline"
              >
                Clear all
              </button>
            )}
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-faint" />
              <Input
                placeholder="Search by name..."
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                className="pl-9"
              />
            </div>
            <FilterSelect
              label="Specialization"
              value={specialization}
              options={SPECIALIZATIONS}
              onChange={setSpecialization}
            />
            <FilterSelect
              label="Language"
              value={language}
              options={LANGUAGES}
              onChange={setLanguage}
            />
            <FilterSelect
              label="Tradition"
              value={tradition}
              options={TRADITIONS}
              onChange={setTradition}
            />
          </div>
        </div>

        {/* Demo banner */}
        {isDemo && !hasFilters && (
          <div
            className="mb-5 rounded-xl px-4 py-3 text-center text-xs text-text-muted"
            style={{ backgroundColor: 'rgba(212, 175, 55, 0.06)', border: '1px solid rgba(212, 175, 55, 0.12)' }}
          >
            <Sparkles className="mr-1.5 inline h-3.5 w-3.5 text-gold" />
            Featured astrologers — our marketplace is launching soon. These profiles showcase what to expect.
          </div>
        )}

        {/* Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <AstrologerSkeleton key={i} />
            ))}
          </div>
        ) : filtered.length === 0 && hasFilters ? (
          <div className="rounded-2xl border border-border bg-card p-12 text-center">
            <Users className="mx-auto h-10 w-10 text-text-faint mb-3" />
            <h3 className="font-display text-sm font-semibold text-text-primary mb-1">
              No astrologers found
            </h3>
            <p className="text-sm text-text-muted">
              No astrologers match your criteria. Try adjusting your filters.
            </p>
            <Button variant="outline" size="sm" className="mt-4" onClick={clearFilters}>
              Clear Filters
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((astrologer) => (
              <AstrologerCard key={astrologer.astrologer_id} astrologer={astrologer} />
            ))}
          </div>
        )}
      </section>

      {/* ============================================================
          Consultation Types
          ============================================================ */}
      <section>
        <h2 className="mb-4 font-display text-lg font-semibold text-text-primary">
          Consultation Types
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <ConsultationCard
            icon={Video}
            title="Video Call"
            description="Face-to-face with screen sharing for chart review"
            price="From &#8377;1,200/session"
          />
          <ConsultationCard
            icon={MessageSquare}
            title="Live Chat"
            description="Real-time text consultation for quick questions"
            price="From &#8377;500/session"
          />
          <ConsultationCard
            icon={Phone}
            title="Voice Call"
            description="Audio consultations, perfect for on-the-go"
            price="From &#8377;800/session"
          />
          <ConsultationCard
            icon={FileText}
            title="Detailed Report"
            description="Written analysis delivered within 48 hours"
            price="From &#8377;1,500/report"
          />
        </div>
      </section>

      {/* ============================================================
          Bottom CTA — Join as Astrologer
          ============================================================ */}
      <section
        className="rounded-2xl border px-6 py-10 text-center sm:px-12"
        style={{
          borderColor: 'rgba(212, 175, 55, 0.2)',
          background: 'linear-gradient(135deg, rgba(212, 175, 55, 0.04) 0%, rgba(212, 175, 55, 0.01) 100%)',
        }}
      >
        <h2 className="font-display text-lg font-semibold text-text-primary">
          Are you a professional astrologer?
        </h2>
        <p className="mx-auto mt-2 max-w-lg text-sm leading-relaxed text-text-muted">
          Join our marketplace and connect with thousands of seekers worldwide.
          Grow your practice with tools built for modern astrologers.
        </p>
        <a href="mailto:astrologers@josiam.com">
          <Button
            size="default"
            className="mt-5 bg-gold text-black font-semibold hover:opacity-90"
          >
            Apply to Join
            <ArrowRight className="ml-1.5 h-4 w-4" />
          </Button>
        </a>
        <p className="mt-3 text-[11px] text-text-faint">
          Verified credentials &middot; 3+ years experience &middot; Background check
        </p>
      </section>
    </div>
  );
}
