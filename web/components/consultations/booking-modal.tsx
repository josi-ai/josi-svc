'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { ProfileSelector } from '@/components/ui/profile-selector';
import {
  Video,
  MessageSquare,
  Phone,
  Mail,
  CheckCircle,
} from 'lucide-react';

/* ---------- Types ---------- */

interface Astrologer {
  astrologer_id: string;
  professional_name: string;
  hourly_rate: number;
  currency: string;
}

/* ---------- Constants ---------- */

const CONSULTATION_TYPES = ['Video', 'Chat', 'Voice', 'Email'];
const DURATION_OPTIONS = [30, 60];

const TYPE_ICONS: Record<string, React.ElementType> = {
  Video, Chat: MessageSquare, Voice: Phone, Email: Mail,
};

/* ---------- Component ---------- */

export function BookingModal({
  astrologer,
  onClose,
}: {
  astrologer: Astrologer;
  onClose: () => void;
}) {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [consultationType, setConsultationType] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [personId, setPersonId] = useState('');
  const [questions, setQuestions] = useState('');
  const [duration, setDuration] = useState(60);
  const [error, setError] = useState('');
  const [successId, setSuccessId] = useState('');

  const { data: chartsRes } = useQuery({
    queryKey: ['charts', 'person', personId],
    queryFn: () => apiClient.get<any[]>(`/api/v1/charts/person/${personId}`),
    enabled: !!personId,
  });
  const chartId = chartsRes?.data?.[0]?.chart_id || '';

  const bookMutation = useMutation({
    mutationFn: () =>
      apiClient.post('/api/v1/consultations/book', {
        astrologer_id: astrologer.astrologer_id,
        chart_id: chartId,
        consultation_type_name: consultationType,
        user_questions: questions.split('\n').filter(Boolean),
        duration_minutes: duration,
        preferred_times: scheduledAt ? [new Date(scheduledAt).toISOString()] : [],
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      }),
    onSuccess: (res) => {
      setSuccessId((res.data as { consultation_id?: string })?.consultation_id || '');
      setStep(5);
    },
    onError: (err: Error) => setError(err.message),
  });

  const canProceed = () => {
    if (step === 1) return !!consultationType;
    if (step === 2) return !!scheduledAt;
    if (step === 3) return !!personId && !!questions.trim();
    return true;
  };

  const totalCost = (astrologer.hourly_rate * duration) / 60;
  const currency = astrologer.currency === 'USD' ? '$' : astrologer.currency;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card shadow-xl" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="border-b border-border px-6 py-4">
          <h2 className="font-display text-lg font-semibold text-text-primary">
            {step === 5 ? 'Booking Confirmed' : 'Book Consultation'}
          </h2>
          {step < 5 && (
            <div className="mt-3 flex gap-1">
              {[1, 2, 3, 4].map((s) => (
                <div key={s} className={`h-1 flex-1 rounded-full transition-colors ${s <= step ? 'bg-[var(--gold)]' : 'bg-border'}`} />
              ))}
            </div>
          )}
        </div>

        {/* Body */}
        <div className="px-6 py-5">
          {step === 1 && (
            <div>
              <p className="mb-4 text-sm text-text-muted">Select your preferred consultation type</p>
              <div className="grid grid-cols-2 gap-3">
                {CONSULTATION_TYPES.map((type) => {
                  const Icon = TYPE_ICONS[type] || MessageSquare;
                  const selected = consultationType === type;
                  return (
                    <button
                      key={type}
                      onClick={() => setConsultationType(type)}
                      className={`flex flex-col items-center gap-2 rounded-xl border p-4 text-sm font-medium transition-colors ${
                        selected
                          ? 'border-[var(--gold)] bg-[var(--gold-bg)] text-text-primary'
                          : 'border-border bg-transparent text-text-muted hover:border-[var(--gold)]/30'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      {type}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <p className="mb-4 text-sm text-text-muted">Choose your preferred date and time</p>
              <input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
                min={new Date().toISOString().slice(0, 16)}
                className="w-full rounded-lg border border-border bg-input px-4 py-3 text-sm text-text-primary focus:border-[var(--gold)]/60 focus:outline-none focus:ring-1 focus:ring-[var(--gold)]/50"
              />
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-text-faint">Profile</label>
                <ProfileSelector value={personId} onChange={setPersonId} />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-text-faint">What would you like to discuss?</label>
                <textarea
                  value={questions}
                  onChange={(e) => setQuestions(e.target.value)}
                  rows={3}
                  placeholder="Enter your questions (one per line)..."
                  className="w-full rounded-lg border border-border bg-input px-4 py-3 text-sm text-text-primary placeholder:text-text-faint focus:border-[var(--gold)]/60 focus:outline-none focus:ring-1 focus:ring-[var(--gold)]/50"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-text-faint">Duration</label>
                <div className="flex gap-3">
                  {DURATION_OPTIONS.map((d) => (
                    <button
                      key={d}
                      onClick={() => setDuration(d)}
                      className={`flex-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors ${
                        duration === d
                          ? 'border-[var(--gold)] bg-[var(--gold-bg)] text-text-primary'
                          : 'border-border text-text-muted hover:border-[var(--gold)]/30'
                      }`}
                    >
                      {d} min
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-3">
              <p className="mb-4 text-sm text-text-muted">Review your booking details</p>
              <div className="rounded-xl border border-border bg-[var(--surface)] p-4 space-y-2.5 text-sm">
                <Row label="Astrologer" value={astrologer.professional_name} />
                <Row label="Type" value={consultationType} />
                <Row label="Date & Time" value={scheduledAt ? new Date(scheduledAt).toLocaleString() : 'Flexible'} />
                <Row label="Duration" value={`${duration} min`} />
                <div className="border-t border-border pt-2.5 flex justify-between">
                  <span className="font-medium text-text-primary">Total</span>
                  <span className="font-semibold text-[var(--gold)]">{currency}{totalCost.toFixed(2)}</span>
                </div>
              </div>
              {error && <p className="text-xs text-red-400">{error}</p>}
            </div>
          )}

          {step === 5 && (
            <div className="flex flex-col items-center gap-4 py-4 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10">
                <CheckCircle className="h-7 w-7 text-emerald-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-text-primary">Your consultation has been booked</p>
                <p className="mt-1 text-xs text-text-muted">Consultation ID: {successId.slice(0, 8)}...</p>
              </div>
              <Button size="sm" onClick={() => router.push('/consultations')} className="mt-2">View Consultations</Button>
            </div>
          )}
        </div>

        {/* Footer */}
        {step < 5 && (
          <div className="flex items-center justify-between border-t border-border px-6 py-4">
            <Button variant="outline" size="sm" onClick={step === 1 ? onClose : () => setStep(step - 1)}>
              {step === 1 ? 'Cancel' : 'Back'}
            </Button>
            {step < 4 ? (
              <Button size="sm" disabled={!canProceed()} onClick={() => setStep(step + 1)}>Continue</Button>
            ) : (
              <Button
                size="sm"
                disabled={bookMutation.isPending}
                onClick={() => bookMutation.mutate()}
                className="bg-[var(--gold)] hover:bg-[var(--gold-bright)] text-white"
              >
                {bookMutation.isPending ? 'Booking...' : 'Confirm Booking'}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-text-muted">{label}</span>
      <span className="font-medium text-text-primary">{value}</span>
    </div>
  );
}
