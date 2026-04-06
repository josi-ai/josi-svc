'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { Sparkles, Send, User } from 'lucide-react';

import type { Message, Chart } from './_components/ai-types';
import { SUGGESTIONS, STYLES } from './_components/ai-types';
import { S, renderContent, TypingDot } from './_components/ai-helpers';
import { ChartContextSidebar } from './_components/chart-context-sidebar';

export default function AIChatPage() {
  const searchParams = useSearchParams();
  const [personId, setPersonId] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [style, setStyle] = useState(1);
  const [initialSent, setInitialSent] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (personId && typeof window !== 'undefined' && window.innerWidth >= 1024) {
      setSidebarCollapsed(false);
    }
  }, [personId]);

  const { data: chartsRes } = useQuery({
    queryKey: ['charts', 'person', personId],
    queryFn: () => apiClient.get<Chart[]>(`/api/v1/charts/person/${personId}`),
    enabled: !!personId,
  });
  const charts = chartsRes?.data || [];
  const chartId = charts.find((c) => c.chart_type === 'vedic')?.chart_id || charts[0]?.chart_id;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = useCallback(async (text: string) => {
    const q = text.trim();
    if (!q || loading) return;
    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setInput('');
    setLoading(true);
    try {
      if (!chartId) {
        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: 'I need a calculated chart to work with. Please create a chart for your profile first, then come back to ask questions.',
        }]);
        return;
      }
      const res = await apiClient.post<{ interpretation?: string; content?: string; text?: string }>('/api/v1/ai/interpret', { chart_id: chartId, question: q, style });
      const answer = res.data?.interpretation || res.data?.content || res.data?.text
        || (typeof res.data === 'string' ? res.data : JSON.stringify(res.data));
      setMessages((prev) => [...prev, { role: 'assistant', content: answer }]);
    } catch {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: "I'm having trouble connecting. Please try again.",
      }]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [chartId, loading, style]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q && !initialSent && chartId) { setInitialSent(true); sendMessage(q); }
  }, [searchParams, chartId, initialSent, sendMessage]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  const showSuggestions = messages.length === 0 && !loading;

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 64px)', overflow: 'hidden', position: 'relative' }}>
      {/* Main chat column */}
      <div style={{ ...S.page, flex: 1, minWidth: 0 }}>
        {/* Header */}
        <div style={S.header}>
          <div>
            <h1 style={S.heading}>Ask Josi AI</h1>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '4px 0 0' }}>
              Your personal astrology assistant
            </p>
          </div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <select value={style} onChange={(e) => setStyle(Number(e.target.value))} style={S.select}>
              {STYLES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
            <ProfileSelector
              value={personId}
              onChange={setPersonId}
              style={{ ...S.select, width: 160, padding: '6px 28px 6px 10px' }}
            />
          </div>
        </div>

        {/* Chat area */}
        <div style={S.chatArea}>
          {showSuggestions && (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 24 }}>
              <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--gold-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Sparkles size={28} style={{ color: 'var(--gold)' }} />
              </div>
              <div style={{ textAlign: 'center' }}>
                <p style={{ ...S.heading, fontSize: 16, margin: '0 0 6px' }}>What would you like to explore?</p>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>
                  Ask anything about your chart, transits, dasha periods, or life themes.
                </p>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 520 }}>
                {SUGGESTIONS.map((text) => (
                  <button
                    key={text}
                    onClick={() => sendMessage(text)}
                    style={S.chip}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--gold)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
                  >{text}</button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', alignItems: 'flex-start' }}>
              {msg.role === 'assistant' && (
                <div style={{ ...S.avatar, background: 'var(--gold-bg)', marginTop: 2 }}>
                  <Sparkles size={14} style={{ color: 'var(--gold)' }} />
                </div>
              )}
              <div style={msg.role === 'user' ? S.userBubble : S.aiBubble}>
                {msg.role === 'assistant' ? renderContent(msg.content) : msg.content}
              </div>
              {msg.role === 'user' && (
                <div style={{ ...S.avatar, background: 'var(--gold-bg-subtle)', border: '1px solid var(--border)', marginTop: 2 }}>
                  <User size={14} style={{ color: 'var(--text-muted)' }} />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <div style={{ ...S.avatar, background: 'var(--gold-bg)', marginTop: 2 }}>
                <Sparkles size={14} style={{ color: 'var(--gold)' }} />
              </div>
              <div style={{ ...S.aiBubble, display: 'flex', gap: 4, alignItems: 'center' }}>
                <TypingDot delay={0} /><TypingDot delay={0.2} /><TypingDot delay={0.4} />
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input bar */}
        <div style={S.inputBar}>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your chart, dasha, transits..."
            disabled={loading}
            style={{ ...S.input, opacity: loading ? 0.6 : 1 }}
            onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
            onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim()}
            style={{ ...S.sendBtn, opacity: loading || !input.trim() ? 0.5 : 1 }}
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      {/* Chart context sidebar */}
      {personId && (
        <ChartContextSidebar
          personId={personId}
          chartId={chartId}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed((c) => !c)}
        />
      )}
    </div>
  );
}
