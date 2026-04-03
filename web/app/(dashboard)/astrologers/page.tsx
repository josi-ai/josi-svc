'use client';

import { useState, useCallback } from 'react';
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
} from 'lucide-react';
import Link from 'next/link';

/* ---------- Types ---------- */

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

/* ---------- Constants ---------- */

const SPECIALIZATIONS = [
  'Vedic', 'Western', 'Chinese', 'Hellenistic',
  'Medical', 'Karmic', 'Relationship', 'Career',
  'Spiritual', 'Predictive',
];

const LANGUAGES = ['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Bengali'];

const AVATAR_COLORS = [
  'bg-amber-600', 'bg-indigo-600', 'bg-emerald-600', 'bg-rose-600',
  'bg-sky-600', 'bg-violet-600', 'bg-teal-600', 'bg-orange-600',
];

function avatarColor(name: string): string {
  const idx = name.charCodeAt(0) % AVATAR_COLORS.length;
  return AVATAR_COLORS[idx];
}

const PAGE_SIZE = 12;

/* ---------- Sub-components ---------- */

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
        {rating.toFixed(1)} ({reviews})
      </span>
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

function AstrologerCard({ astrologer }: { astrologer: Astrologer }) {
  const isVerified = astrologer.verification_status_name === 'Verified';

  return (
    <div className="rounded-2xl border border-border bg-card p-5 transition-colors hover:border-gold/30">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-lg font-semibold text-white ${avatarColor(astrologer.professional_name)}`}
        >
          {astrologer.professional_name.charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <h3 className="truncate font-display text-sm font-semibold text-text-primary">
              {astrologer.professional_name}
            </h3>
            {isVerified && (
              <BadgeCheck className="h-4 w-4 shrink-0 text-blue" />
            )}
            {astrologer.is_featured && (
              <Badge variant="default" className="ml-1 text-[10px] px-2 py-0">Featured</Badge>
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
        {astrologer.specializations.slice(0, 3).map((spec) => (
          <Badge key={spec} variant="outline" className="text-[10px] px-2 py-0.5">
            {spec}
          </Badge>
        ))}
        {astrologer.specializations.length > 3 && (
          <span className="text-[10px] text-text-faint self-center">
            +{astrologer.specializations.length - 3} more
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
          {astrologer.total_consultations}
        </span>
      </div>

      {/* Footer */}
      <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
        <span className="text-sm font-semibold text-text-primary">
          {astrologer.currency === 'USD' ? '$' : astrologer.currency}{' '}
          {astrologer.hourly_rate}
          <span className="text-xs font-normal text-text-muted">/hr</span>
        </span>
        <Link href={`/astrologers/${astrologer.astrologer_id}`}>
          <Button variant="outline" size="sm">View Profile</Button>
        </Link>
      </div>
    </div>
  );
}

/* ---------- Filter Dropdown ---------- */

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

/* ---------- Main Page ---------- */

export default function AstrologersPage() {
  const [searchName, setSearchName] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [language, setLanguage] = useState('');
  const [minRating, setMinRating] = useState('');
  const [offset, setOffset] = useState(0);

  const buildEndpoint = useCallback(() => {
    const params = new URLSearchParams();
    if (specialization) params.append('specializations', specialization);
    if (language) params.append('languages', language);
    if (minRating) params.append('min_rating', minRating);
    params.append('limit', String(PAGE_SIZE));
    params.append('offset', String(offset));
    const qs = params.toString();
    return `/api/v1/astrologers/search${qs ? `?${qs}` : ''}`;
  }, [specialization, language, minRating, offset]);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['astrologers', specialization, language, minRating, offset],
    queryFn: () => apiClient.get<SearchResponse>(buildEndpoint()),
  });

  const astrologers = data?.data?.astrologers ?? [];

  // Client-side name filter (the API search endpoint filters server-side by spec/lang/rating)
  const filtered = searchName
    ? astrologers.filter((a) =>
        a.professional_name.toLowerCase().includes(searchName.toLowerCase())
      )
    : astrologers;

  const hasFilters = !!(specialization || language || minRating || searchName);

  function clearFilters() {
    setSearchName('');
    setSpecialization('');
    setLanguage('');
    setMinRating('');
    setOffset(0);
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="font-display text-display-md text-text-primary">Astrologers</h1>
        <p className="mt-1 text-sm text-text-muted">
          Browse verified professional astrologers across all traditions
        </p>
      </div>

      {/* Search & Filters */}
      <div className="mb-6 rounded-2xl border border-border bg-card p-4">
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
            onChange={(v) => { setSpecialization(v); setOffset(0); }}
          />
          <FilterSelect
            label="Language"
            value={language}
            options={LANGUAGES}
            onChange={(v) => { setLanguage(v); setOffset(0); }}
          />
          <FilterSelect
            label="Min Rating"
            value={minRating}
            options={['1', '2', '3', '4', '5']}
            onChange={(v) => { setMinRating(v); setOffset(0); }}
          />
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <AstrologerSkeleton key={i} />
          ))}
        </div>
      ) : isError ? (
        <div className="rounded-2xl border border-border bg-card p-12 text-center">
          <p className="text-sm text-text-muted">
            Failed to load astrologers. Please try again later.
          </p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-2xl border border-border bg-card p-12 text-center">
          <Users className="mx-auto h-10 w-10 text-text-faint mb-3" />
          <h3 className="font-display text-sm font-semibold text-text-primary mb-1">
            {hasFilters ? 'No astrologers found' : 'No astrologers yet'}
          </h3>
          <p className="text-sm text-text-muted">
            {hasFilters
              ? 'No astrologers match your criteria. Try adjusting your filters.'
              : 'No astrologers have registered yet — check back soon.'}
          </p>
          {hasFilters && (
            <Button variant="outline" size="sm" className="mt-4" onClick={clearFilters}>
              Clear Filters
            </Button>
          )}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((astrologer) => (
              <AstrologerCard key={astrologer.astrologer_id} astrologer={astrologer} />
            ))}
          </div>

          {/* Pagination */}
          {(data?.data?.total ?? 0) >= PAGE_SIZE && (
            <div className="mt-6 flex items-center justify-center gap-3">
              <Button
                variant="outline"
                size="sm"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
              >
                Previous
              </Button>
              <span className="text-xs text-text-muted">
                Page {Math.floor(offset / PAGE_SIZE) + 1}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={filtered.length < PAGE_SIZE}
                onClick={() => setOffset(offset + PAGE_SIZE)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
