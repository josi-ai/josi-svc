'use client';

import { useState, useRef, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  MessageBubble,
  StatusBanner,
  EmptyMessages,
  formatDateTime,
  type ChatMessage,
} from '@/components/consultations/chat-components';
import {
  ArrowLeft,
  Send,
  Video,
  MessageSquare,
  Phone,
  Mail,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

/* ---------- Types ---------- */

interface Consultation {
  consultation_id: string;
  user_id: string;
  astrologer_id: string;
  chart_id: string | null;
  consultation_type_id: number;
  consultation_type_name: string;
  status_id: number;
  status_name: string;
  user_questions: string[];
  focus_areas: string[];
  scheduled_at: string | null;
  duration_minutes: number;
  total_amount: number;
  currency: string;
  payment_status_id: number | null;
  payment_status_name: string | null;
  ai_summary: string | null;
  created_at: string;
  completed_at: string | null;
}

interface ConsultationDetailResponse {
  consultation: Consultation;
  messages: ChatMessage[];
  interpretation: Record<string, any> | null;
  recommendations: string[];
  video_room_id: string | null;
  ai_key_points: string[];
}

/* ---------- Constants ---------- */

const STATUS_CONFIG: Record<string, { color: string; icon: React.ElementType; label: string }> = {
  Pending:        { color: 'text-text-muted',    icon: Clock,        label: 'Pending' },
  Scheduled:      { color: 'text-blue',          icon: Calendar,     label: 'Scheduled' },
  'In Progress':  { color: 'text-[var(--gold)]', icon: MessageSquare, label: 'In Progress' },
  Completed:      { color: 'text-emerald-400',   icon: CheckCircle,  label: 'Completed' },
  Cancelled:      { color: 'text-red-400',       icon: XCircle,      label: 'Cancelled' },
  Refunded:       { color: 'text-text-muted',    icon: AlertCircle,  label: 'Refunded' },
};

const TYPE_ICONS: Record<string, React.ElementType> = {
  Video, Chat: MessageSquare, Voice: Phone, Email: Mail,
};

/* ---------- Main Page ---------- */

export default function ConsultationDetailPage() {
  const { consultationId } = useParams<{ consultationId: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const currentUserId = user?.user_id || '';

  const { data, isLoading, isError } = useQuery({
    queryKey: ['consultation-detail', consultationId],
    queryFn: () => apiClient.get<ConsultationDetailResponse>(`/api/v1/consultations/${consultationId}`),
    enabled: !!consultationId,
    refetchInterval: 5000,
  });

  const consultation = data?.data?.consultation;
  const messages = data?.data?.messages ?? [];
  const aiKeyPoints = data?.data?.ai_key_points ?? [];
  const aiSummary = consultation?.ai_summary;
  const isInProgress = consultation?.status_name === 'In Progress';

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMutation = useMutation({
    mutationFn: (content: string) =>
      apiClient.post(`/api/v1/consultations/${consultationId}/messages`, {
        consultation_id: consultationId,
        content,
        message_type: 'text',
      }),
    onSuccess: () => {
      setInput('');
      queryClient.invalidateQueries({ queryKey: ['consultation-detail', consultationId] });
      setTimeout(() => inputRef.current?.focus(), 100);
    },
  });

  const handleSend = () => {
    const text = input.trim();
    if (!text || sendMutation.isPending) return;
    sendMutation.mutate(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-5 w-32 rounded bg-border" />
        <div className="rounded-2xl border border-border bg-card p-6 space-y-3">
          <div className="h-5 w-48 rounded bg-border" />
          <div className="h-4 w-64 rounded bg-border" />
          <div className="h-40 w-full rounded bg-border" />
        </div>
      </div>
    );
  }

  if (isError || !consultation) {
    return (
      <div className="rounded-2xl border border-border bg-card p-12 text-center">
        <p className="text-sm text-text-muted">Consultation not found.</p>
        <Link href="/consultations"><Button variant="outline" size="sm" className="mt-4">Back to Consultations</Button></Link>
      </div>
    );
  }

  const statusConf = STATUS_CONFIG[consultation.status_name] ?? STATUS_CONFIG.Pending;
  const StatusIcon = statusConf.icon;
  const TypeIcon = TYPE_ICONS[consultation.consultation_type_name] ?? MessageSquare;

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div className="shrink-0 border-b border-border px-4 py-3 md:px-6">
        <Link href="/consultations" className="mb-2 inline-flex items-center gap-1.5 text-xs text-text-muted hover:text-text-primary transition-colors">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Consultations
        </Link>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--surface)] border border-border">
              <TypeIcon className="h-4 w-4 text-text-muted" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-semibold text-text-primary">{consultation.consultation_type_name} Consultation</h1>
                <Badge variant="outline" className={`text-[10px] ${statusConf.color}`}>
                  <StatusIcon className="mr-1 h-3 w-3" />{statusConf.label}
                </Badge>
              </div>
              <p className="text-xs text-text-muted">
                ID: {consultation.consultation_id.slice(0, 8)}...
                {consultation.scheduled_at && <> &middot; {formatDateTime(consultation.scheduled_at)?.date}</>}
              </p>
            </div>
          </div>
          <div className="text-right text-xs text-text-muted">
            <span className="font-medium text-text-primary">
              {consultation.currency === 'USD' ? '$' : consultation.currency}{consultation.total_amount}
            </span>
            <span> &middot; {consultation.duration_minutes} min</span>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex flex-1 overflow-hidden">
        <div className="flex flex-1 flex-col min-w-0">
          <div className="flex-1 overflow-y-auto px-4 py-4 md:px-6 space-y-4">
            <StatusBanner consultation={consultation} />

            {consultation.user_questions.length > 0 && (
              <div className="rounded-xl border border-border bg-[var(--surface)] p-4">
                <p className="mb-2 text-xs font-medium uppercase tracking-wider text-text-faint">Discussion Topics</p>
                <ul className="space-y-1">
                  {consultation.user_questions.map((q, i) => (
                    <li key={i} className="text-sm text-text-secondary">&bull; {q}</li>
                  ))}
                </ul>
              </div>
            )}

            {messages.length === 0 && isInProgress && <EmptyMessages />}

            {messages.map((msg) => (
              <MessageBubble key={msg.message_id} message={msg} isOwn={msg.sender_id === currentUserId} />
            ))}

            <div ref={chatEndRef} />
          </div>

          {/* Input / Read-only bar */}
          {isInProgress ? (
            <div className="shrink-0 border-t border-border bg-[var(--background)] px-4 py-3 md:px-6">
              <div className="flex items-center gap-2.5">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message..."
                  disabled={sendMutation.isPending}
                  className="flex-1 rounded-lg border border-border bg-input px-4 py-2.5 text-sm text-text-primary placeholder:text-text-faint focus:border-[var(--gold)]/60 focus:outline-none focus:ring-1 focus:ring-[var(--gold)]/50 disabled:opacity-50"
                />
                <button
                  onClick={handleSend}
                  disabled={sendMutation.isPending || !input.trim()}
                  className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--gold)] text-white transition-opacity disabled:opacity-40"
                  aria-label="Send message"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
              {sendMutation.isError && <p className="mt-1.5 text-xs text-red-400">Failed to send. Please try again.</p>}
            </div>
          ) : (
            <div className="shrink-0 border-t border-border bg-[var(--surface)] px-4 py-3 text-center">
              <p className="text-xs text-text-faint">
                {consultation.status_name === 'Completed'
                  ? 'This consultation has ended. Messages are read-only.'
                  : consultation.status_name === 'Cancelled' || consultation.status_name === 'Refunded'
                    ? 'This consultation was cancelled.'
                    : 'Messaging will be available when the consultation starts.'}
              </p>
            </div>
          )}
        </div>

        {/* AI Insights sidebar (desktop only) */}
        {(aiSummary || aiKeyPoints.length > 0) && (
          <div className="hidden w-72 shrink-0 flex-col border-l border-border bg-[var(--surface)] lg:flex">
            <div className="border-b border-border px-4 py-3">
              <span className="text-xs font-medium uppercase tracking-wider text-text-faint">AI Insights</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {aiSummary && (
                <div>
                  <p className="mb-1.5 text-xs font-medium text-text-muted">Summary</p>
                  <p className="text-sm text-text-secondary leading-relaxed">{aiSummary}</p>
                </div>
              )}
              {aiKeyPoints.length > 0 && (
                <div>
                  <p className="mb-1.5 text-xs font-medium text-text-muted">Key Points</p>
                  <ul className="space-y-1.5">
                    {aiKeyPoints.map((point, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                        <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--gold)]" />
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
