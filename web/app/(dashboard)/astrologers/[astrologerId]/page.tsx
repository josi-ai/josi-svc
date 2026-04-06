'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookingModal } from '@/components/consultations/booking-modal';
import {
  ArrowLeft, Star, BadgeCheck, Clock, Globe, Users,
  Video, MessageSquare, Phone, Mail, ThumbsUp, CheckCircle,
} from 'lucide-react';
import Link from 'next/link';
import { type Astrologer, avatarColor } from '../_components/astrologer-types';

/* ---------- Types ---------- */

interface Review {
  review_id: string; astrologer_id: string; user_id: string;
  rating: number; title: string | null; review_text: string | null;
  accuracy_rating: number | null; communication_rating: number | null;
  empathy_rating: number | null; is_verified: boolean;
  helpful_votes: number; created_at: string;
}

interface ProfileResponse {
  astrologer: Astrologer;
  recent_reviews: Review[];
  specialization_display: string[];
}

/* ---------- Constants ---------- */

const TYPE_META: { type: string; Icon: React.ElementType }[] = [
  { type: 'Video', Icon: Video },
  { type: 'Chat', Icon: MessageSquare },
  { type: 'Voice', Icon: Phone },
  { type: 'Email', Icon: Mail },
];

/* ---------- Helpers ---------- */

function StarRating({ rating, size = 14 }: { rating: number; size?: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((s) => (
        <Star key={s} style={{ width: size, height: size }}
          className={s <= Math.round(rating) ? 'fill-amber-400 text-amber-400' : 'fill-transparent text-text-faint'} />
      ))}
    </div>
  );
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function DetailItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-start gap-2.5">
      <div className="mt-0.5 text-text-faint">{icon}</div>
      <div><p className="text-xs text-text-faint">{label}</p><p className="text-sm font-medium text-text-primary">{value}</p></div>
    </div>
  );
}

/* ---------- Main Page ---------- */

export default function AstrologerProfilePage() {
  const { astrologerId } = useParams<{ astrologerId: string }>();
  const [showBooking, setShowBooking] = useState(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['astrologer-profile', astrologerId],
    queryFn: () => apiClient.get<ProfileResponse>(`/api/v1/astrologers/${astrologerId}`),
    enabled: !!astrologerId,
  });

  const astrologer = data?.data?.astrologer;
  const reviews = data?.data?.recent_reviews ?? [];
  const specDisplay = data?.data?.specialization_display ?? [];

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-6 w-32 rounded bg-border" />
        <div className="rounded-2xl border border-border bg-card p-8 space-y-4">
          <div className="flex gap-4">
            <div className="h-16 w-16 rounded-full bg-border" />
            <div className="flex-1 space-y-2">
              <div className="h-5 w-48 rounded bg-border" />
              <div className="h-4 w-32 rounded bg-border" />
            </div>
          </div>
          <div className="h-20 w-full rounded bg-border" />
        </div>
      </div>
    );
  }

  if (isError || !astrologer) {
    return (
      <div className="rounded-2xl border border-border bg-card p-12 text-center">
        <p className="text-sm text-text-muted">Astrologer not found.</p>
        <Link href="/astrologers">
          <Button variant="outline" size="sm" className="mt-4">Back to Directory</Button>
        </Link>
      </div>
    );
  }

  const isVerified = astrologer.verification_status_name === 'Verified';

  return (
    <div>
      {/* Back link */}
      <Link
        href="/astrologers"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Astrologers
      </Link>

      {/* Profile Card */}
      <div className="rounded-2xl border border-border bg-card p-6 md:p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-start">
          <div className={`flex h-20 w-20 shrink-0 items-center justify-center rounded-full text-2xl font-bold text-white ${avatarColor(astrologer.professional_name)}`}>
            {astrologer.professional_name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="font-display text-xl font-semibold text-text-primary">
                {astrologer.professional_name}
              </h1>
              {isVerified && <BadgeCheck className="h-5 w-5 text-blue" />}
              {astrologer.is_featured && <Badge variant="default" className="text-xs">Featured</Badge>}
            </div>
            <div className="mt-1.5 flex items-center gap-2">
              <StarRating rating={astrologer.rating} />
              <span className="text-sm text-text-muted">
                {astrologer.rating.toFixed(1)} ({astrologer.total_reviews} reviews)
              </span>
            </div>
            {astrologer.bio && (
              <p className="mt-3 text-sm text-text-secondary leading-relaxed">{astrologer.bio}</p>
            )}
          </div>
          <Button
            size="lg"
            onClick={() => setShowBooking(true)}
            className="shrink-0 bg-[var(--gold)] hover:bg-[var(--gold-bright)] text-white font-semibold px-8"
          >
            Book Consultation
          </Button>
        </div>

        {/* Details Grid */}
        <div className="mt-6 grid grid-cols-2 gap-4 border-t border-border pt-6 sm:grid-cols-3 lg:grid-cols-4">
          <DetailItem icon={<Clock className="h-4 w-4" />} label="Experience" value={`${astrologer.years_experience} years`} />
          <DetailItem icon={<Users className="h-4 w-4" />} label="Consultations" value={String(astrologer.total_consultations)} />
          <DetailItem icon={<Globe className="h-4 w-4" />} label="Languages" value={astrologer.languages.join(', ')} />
          <DetailItem
            icon={<Star className="h-4 w-4" />}
            label="Rate"
            value={`${astrologer.currency === 'USD' ? '$' : astrologer.currency}${astrologer.hourly_rate}/hr`}
          />
        </div>

        {/* Specializations */}
        {specDisplay.length > 0 && (
          <div className="mt-5">
            <h3 className="mb-2 text-xs font-medium uppercase tracking-wider text-text-faint">Specializations</h3>
            <div className="flex flex-wrap gap-2">
              {specDisplay.map((spec) => (
                <Badge key={spec} variant="outline" className="text-xs px-3 py-1">{spec}</Badge>
              ))}
            </div>
          </div>
        )}

        {/* Consultation Types */}
        <div className="mt-5">
          <h3 className="mb-2 text-xs font-medium uppercase tracking-wider text-text-faint">Available Via</h3>
          <div className="flex flex-wrap gap-2">
            {TYPE_META.map(({ type, Icon }) => (
              <span key={type} className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs text-text-secondary">
                <Icon className="h-3.5 w-3.5" /> {type}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="mt-6">
        <h2 className="mb-4 font-display text-lg font-semibold text-text-primary">
          Reviews ({reviews.length})
        </h2>
        {reviews.length === 0 ? (
          <div className="rounded-2xl border border-border bg-card p-8 text-center">
            <p className="text-sm text-text-muted">No reviews yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {reviews.map((review) => (
              <div key={review.review_id} className="rounded-2xl border border-border bg-card p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <StarRating rating={review.rating} size={12} />
                      {review.is_verified && (
                        <Badge variant="outline" className="text-[10px] gap-1 px-1.5 py-0">
                          <CheckCircle className="h-2.5 w-2.5" /> Verified
                        </Badge>
                      )}
                    </div>
                    {review.title && (
                      <h4 className="mt-1 text-sm font-medium text-text-primary">{review.title}</h4>
                    )}
                  </div>
                  <span className="shrink-0 text-xs text-text-faint">{formatDate(review.created_at)}</span>
                </div>
                {review.review_text && (
                  <p className="mt-2 text-sm text-text-secondary leading-relaxed">{review.review_text}</p>
                )}
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-text-muted">
                  {review.accuracy_rating && <span>Accuracy: {review.accuracy_rating}/5</span>}
                  {review.communication_rating && <span>Communication: {review.communication_rating}/5</span>}
                  {review.empathy_rating && <span>Empathy: {review.empathy_rating}/5</span>}
                  {review.helpful_votes > 0 && (
                    <span className="flex items-center gap-1">
                      <ThumbsUp className="h-3 w-3" /> {review.helpful_votes}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Booking Modal */}
      {showBooking && (
        <BookingModal astrologer={astrologer} onClose={() => setShowBooking(false)} />
      )}
    </div>
  );
}
