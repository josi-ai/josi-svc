'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface AiHistoryItem {
  interpretation_id?: string
  question?: string
  snippet?: string
  summary?: string
  created_at?: string
}

/* ---------- Constants ---------- */

const SUGGESTIONS = ['Career outlook', 'Current transits', 'Relationship insights']

/* ---------- Component ---------- */

export default function AiChatAccess({ onRemove }: { onRemove: () => void }) {
  const router = useRouter()
  const [question, setQuestion] = useState('')

  // Try fetching the last AI history item — gracefully ignores 404/errors
  const { data: historyResponse } = useQuery({
    queryKey: ['ai', 'history', 'latest'],
    queryFn: () =>
      apiClient.get<AiHistoryItem[]>('/api/v1/ai/history?limit=1'),
    retry: false,
  })

  const lastItem = historyResponse?.data?.[0]
  const lastSnippet = lastItem?.snippet || lastItem?.summary || null

  function navigateToAi(q: string) {
    if (!q.trim()) return
    router.push(`/ai?q=${encodeURIComponent(q.trim())}`)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault()
      navigateToAi(question)
    }
  }

  return (
    <WidgetCard tradition="ai" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          AI Chat
        </div>

        {/* Avatar + label */}
        <div className="flex gap-3 items-center mb-3.5">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center text-xl flex-shrink-0"
            style={{
              background: 'var(--avatar-gradient)',
              color: 'var(--avatar-text)',
            }}
          >
            &#10022;
          </div>
          <div>
            <div className="text-[13px] font-semibold text-[var(--text-primary)] mb-0.5">
              Ask Josi AI
            </div>
            <div className="text-[11px] text-[var(--text-muted)]">
              {lastSnippet
                ? lastSnippet.length > 60
                  ? `${lastSnippet.slice(0, 60)}...`
                  : lastSnippet
                : 'About your chart, transits, or anything'}
            </div>
          </div>
        </div>

        {/* Functional input */}
        <div className="relative">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What would you like to explore?"
            className="w-full py-2 px-3.5 pr-9 rounded-lg text-xs border outline-none transition-colors"
            style={{
              background: 'var(--surface)',
              borderColor: 'var(--border)',
              color: 'var(--text-primary)',
            }}
            onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
            onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
          />
          {question.trim() && (
            <button
              onClick={() => navigateToAi(question)}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-5 h-5 flex items-center justify-center rounded text-[var(--text-muted)] hover:text-[var(--gold)] transition-colors"
              aria-label="Send"
            >
              &rarr;
            </button>
          )}
        </div>

        {/* Suggestion chips */}
        <div className="flex gap-1.5 mt-2.5 flex-wrap">
          {SUGGESTIONS.map((text) => (
            <span
              key={text}
              onClick={() => navigateToAi(text)}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-[11px] font-medium cursor-pointer transition-colors border hover:border-[var(--gold)]"
              style={{
                background: 'var(--surface)',
                borderColor: 'var(--border)',
                color: 'var(--text-secondary)',
              }}
            >
              {text}
            </span>
          ))}
        </div>
      </div>
    </WidgetCard>
  )
}
