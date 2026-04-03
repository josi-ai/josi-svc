'use client';

import {
  Calendar,
  CheckCircle,
  XCircle,
  AlertCircle,
  MessageSquare,
  User,
} from 'lucide-react';

/* ---------- Types ---------- */

export interface ConsultationBase {
  consultation_id: string;
  status_name: string;
  scheduled_at: string | null;
  completed_at: string | null;
}

export interface ChatMessage {
  message_id: string;
  consultation_id: string;
  sender_id: string;
  message_type: string;
  content: string;
  attachment_url: string | null;
  is_read: boolean;
  created_at: string;
}

/* ---------- Helpers ---------- */

export function formatDateTime(dateStr: string | null) {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return null;
  return {
    date: d.toLocaleDateString('en-US', {
      weekday: 'short', month: 'short', day: 'numeric', year: 'numeric',
    }),
    time: d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
  };
}

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

/* ---------- Message Bubble ---------- */

export function MessageBubble({
  message,
  isOwn,
}: {
  message: ChatMessage;
  isOwn: boolean;
}) {
  return (
    <div className={`flex gap-2.5 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
          isOwn ? 'bg-[var(--gold-bg-subtle)] border border-border' : 'bg-indigo-500/10'
        }`}
      >
        <User className={`h-3.5 w-3.5 ${isOwn ? 'text-text-muted' : 'text-indigo-400'}`} />
      </div>
      <div className={`max-w-[72%] ${isOwn ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isOwn
              ? 'rounded-tr-sm bg-[var(--gold-bg)] text-text-primary'
              : 'rounded-tl-sm border border-border bg-[var(--surface)] text-text-primary'
          }`}
        >
          {message.content}
        </div>
        <p className={`mt-1 text-[10px] text-text-faint ${isOwn ? 'text-right' : 'text-left'}`}>
          {formatTime(message.created_at)}
        </p>
      </div>
    </div>
  );
}

/* ---------- Status Banners ---------- */

export function StatusBanner({ consultation }: { consultation: ConsultationBase }) {
  const dt = formatDateTime(consultation.scheduled_at);
  const status = consultation.status_name;

  if (status === 'Scheduled' || status === 'Pending') {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-blue/20 bg-blue/5 px-4 py-3">
        <Calendar className="h-5 w-5 text-blue" />
        <div>
          <p className="text-sm font-medium text-text-primary">
            {status === 'Pending'
              ? 'Consultation is pending confirmation'
              : 'Consultation hasn\'t started yet'}
          </p>
          {dt && (
            <p className="text-xs text-text-muted">
              Scheduled for {dt.date} at {dt.time}
            </p>
          )}
        </div>
      </div>
    );
  }

  if (status === 'Completed') {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/5 px-4 py-3">
        <CheckCircle className="h-5 w-5 text-emerald-400" />
        <div>
          <p className="text-sm font-medium text-text-primary">Consultation completed</p>
          {consultation.completed_at && (
            <p className="text-xs text-text-muted">
              Ended {formatDateTime(consultation.completed_at)?.date}
            </p>
          )}
        </div>
      </div>
    );
  }

  if (status === 'Cancelled' || status === 'Refunded') {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-red-400/20 bg-red-400/5 px-4 py-3">
        <XCircle className="h-5 w-5 text-red-400" />
        <p className="text-sm font-medium text-text-primary">
          This consultation was {status.toLowerCase()}
        </p>
      </div>
    );
  }

  return null;
}

/* ---------- Empty State ---------- */

export function EmptyMessages() {
  return (
    <div className="flex flex-col items-center gap-2 py-8 text-center">
      <MessageSquare className="h-8 w-8 text-text-faint" />
      <p className="text-sm text-text-muted">No messages yet. Start the conversation.</p>
    </div>
  );
}
