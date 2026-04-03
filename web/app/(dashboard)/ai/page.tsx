'use client';

import { useState, useRef, useEffect, useCallback, Fragment } from 'react';
import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { Sparkles, Send, User, PanelRightClose, PanelRightOpen, Sun, Moon, Star, ArrowUpRight, Clock } from 'lucide-react';

/* ---------- Types ---------- */

interface Message { role: 'user' | 'assistant'; content: string }
interface Chart {
  chart_id: string;
  chart_type: string;
  person_id: string;
  chart_data?: {
    planets?: Record<string, { sign?: string; longitude?: number; house?: number; is_retrograde?: boolean }>;
    ascendant?: { sign?: string; degree?: number };
    dasha?: {
      current_dasha?: {
        mahadasha?: { planet: string; start_date: string; end_date: string };
        antardasha?: { planet: string; start_date: string; end_date: string };
      };
    };
  };
}

interface DashaResponse {
  person_id: string;
  current_dasha: {
    mahadasha: { planet: string; start_date: string; end_date: string };
    antardasha?: { planet: string; start_date: string; end_date: string };
  } | null;
}

interface Transit {
  transiting_planet: string;
  aspect_type: string;
  natal_planet: string;
  intensity?: number | string;
  description?: string;
}

/* ---------- Constants ---------- */

const SUGGESTIONS = [
  'What does my current dasha mean?',
  'How are transits affecting me today?',
  'Tell me about my career prospects',
  'What remedies should I consider?',
  'Explain my birth chart',
  'What are my strongest placements?',
];

const STYLES = [
  { value: 1, label: 'Balanced' },
  { value: 2, label: 'Psychological' },
  { value: 3, label: 'Spiritual' },
  { value: 4, label: 'Practical' },
  { value: 5, label: 'Predictive' },
];

const S = {
  page: { display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)', overflow: 'hidden' } as React.CSSProperties,
  header: { padding: '20px 24px 16px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 } as React.CSSProperties,
  chatArea: { flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: 16 } as React.CSSProperties,
  inputBar: { padding: '16px 24px', borderTop: '1px solid var(--border)', background: 'var(--background)', display: 'flex', gap: 10, alignItems: 'center' } as React.CSSProperties,
  input: { flex: 1, padding: '12px 16px', fontSize: 14, color: 'var(--text-primary)', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, outline: 'none', transition: 'border-color 0.2s' } as React.CSSProperties,
  sendBtn: { width: 42, height: 42, borderRadius: 10, border: 'none', background: 'var(--gold)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', transition: 'opacity 0.2s', flexShrink: 0 } as React.CSSProperties,
  userBubble: { alignSelf: 'flex-end', maxWidth: '72%', padding: '12px 16px', borderRadius: '16px 16px 4px 16px', background: 'var(--gold-bg)', color: 'var(--text-primary)', fontSize: 14, lineHeight: 1.55 } as React.CSSProperties,
  aiBubble: { alignSelf: 'flex-start', maxWidth: '72%', padding: '12px 16px', borderRadius: '16px 16px 16px 4px', background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 14, lineHeight: 1.55 } as React.CSSProperties,
  avatar: { width: 28, height: 28, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 } as React.CSSProperties,
  chip: { padding: '8px 16px', borderRadius: 20, border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text-secondary)', fontSize: 13, cursor: 'pointer', transition: 'border-color 0.2s, color 0.2s' } as React.CSSProperties,
  select: { padding: '6px 10px', fontSize: 12, color: 'var(--text-secondary)', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, outline: 'none' } as React.CSSProperties,
  heading: { fontSize: 22, fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-heading, Georgia, serif)', margin: 0 } as React.CSSProperties,
};

/* ---------- Helpers ---------- */

function renderContent(text: string) {
  return text.split('\n').map((line, i, arr) => {
    const trimmed = line.trimStart();
    const isList = trimmed.startsWith('- ') || trimmed.startsWith('* ');
    const segments = parseInline(isList ? trimmed.slice(2) : line);
    return (
      <Fragment key={i}>
        {isList && <span style={{ paddingLeft: 12, display: 'inline-block' }}>{'\u2022 '}</span>}
        {segments}
        {i < arr.length - 1 && <br />}
      </Fragment>
    );
  });
}

function parseInline(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  const re = /(\*\*(.+?)\*\*|\*(.+?)\*)/g;
  let last = 0, match: RegExpExecArray | null, k = 0;
  while ((match = re.exec(text)) !== null) {
    if (match.index > last) nodes.push(text.slice(last, match.index));
    if (match[2]) nodes.push(<strong key={k++}>{match[2]}</strong>);
    else if (match[3]) nodes.push(<em key={k++}>{match[3]}</em>);
    last = match.index + match[0].length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

function TypingDot({ delay }: { delay: number }) {
  const [opacity, setOpacity] = useState(0.4);
  useEffect(() => {
    let frame: number;
    const start = performance.now();
    const tick = () => {
      const t = ((performance.now() - start + delay * 1000) % 1400) / 1400;
      setOpacity(t > 0.2 && t < 0.4 ? 1 : 0.4);
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [delay]);
  return <span style={{ opacity, transition: 'opacity 0.15s' }}>{'\u25CF'}</span>;
}

/* ---------- Chart Context Sidebar ---------- */

function ChartContextSidebar({
  personId,
  chartId,
  collapsed,
  onToggle,
}: {
  personId: string;
  chartId: string | undefined;
  collapsed: boolean;
  onToggle: () => void;
}) {
  // Fetch full chart data for sun/moon/ascendant
  const { data: chartRes } = useQuery({
    queryKey: ['chart-detail', chartId],
    queryFn: () => apiClient.get<Chart>(`/api/v1/charts/${chartId}`),
    enabled: !!chartId && !collapsed,
    staleTime: 60 * 60 * 1000,
  });

  // Fetch dasha data
  const { data: dashaRes } = useQuery({
    queryKey: ['dasha-sidebar', personId],
    queryFn: () => apiClient.get<DashaResponse>(`/api/v1/dasha/vimshottari/${personId}`),
    enabled: !!personId && !collapsed,
    staleTime: 60 * 60 * 1000,
  });

  // Fetch transits
  const { data: transitsRes } = useQuery({
    queryKey: ['transits-sidebar', personId],
    queryFn: () => apiClient.get<Transit[]>(`/api/v1/transits/current/${personId}`),
    enabled: !!personId && !collapsed,
    staleTime: 10 * 60 * 1000,
  });

  const chart = chartRes?.data;
  const planets = chart?.chart_data?.planets || {};
  const ascendant = chart?.chart_data?.ascendant;
  const sunSign = planets['Sun']?.sign || planets['sun']?.sign;
  const moonSign = planets['Moon']?.sign || planets['moon']?.sign;
  const ascSign = ascendant?.sign;
  const currentDasha = dashaRes?.data?.current_dasha || chart?.chart_data?.dasha?.current_dasha;
  const transits = (transitsRes?.data || []).slice(0, 3);

  const hasData = sunSign || moonSign || ascSign || currentDasha || transits.length > 0;

  if (collapsed) {
    return (
      <button
        onClick={onToggle}
        title="Show chart context"
        style={{
          position: 'absolute', right: 0, top: 72, zIndex: 10,
          width: 36, height: 36, borderRadius: '8px 0 0 8px',
          background: 'var(--surface)', border: '1px solid var(--border)', borderRight: 'none',
          color: 'var(--text-muted)', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <PanelRightOpen size={16} />
      </button>
    );
  }

  const sectionLabel: React.CSSProperties = {
    fontSize: 10, fontWeight: 600, textTransform: 'uppercase',
    letterSpacing: '1.2px', color: 'var(--text-faint)', marginBottom: 8,
  };

  const dataRow: React.CSSProperties = {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '6px 0', fontSize: 13,
  };

  return (
    <div style={{
      width: 260, flexShrink: 0, borderLeft: '1px solid var(--border)',
      background: 'var(--surface)', display: 'flex', flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Sidebar header */}
      <div style={{
        padding: '14px 16px', borderBottom: '1px solid var(--border)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
          Chart Context
        </span>
        <button
          onClick={onToggle}
          title="Hide chart context"
          style={{
            width: 28, height: 28, borderRadius: 6,
            background: 'transparent', border: '1px solid var(--border)',
            color: 'var(--text-muted)', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <PanelRightClose size={14} />
        </button>
      </div>

      {/* Sidebar content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {!personId ? (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Select a profile to see chart context.
          </p>
        ) : !hasData && !chartId ? (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            No chart data available. Calculate a chart first.
          </p>
        ) : (
          <>
            {/* Key Placements */}
            {(sunSign || moonSign || ascSign) && (
              <div style={{ marginBottom: 20 }}>
                <div style={sectionLabel}>Key Placements</div>
                {sunSign && (
                  <div style={dataRow}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
                      <Sun size={13} style={{ color: 'var(--gold)' }} /> Sun
                    </span>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{sunSign}</span>
                  </div>
                )}
                {moonSign && (
                  <div style={dataRow}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
                      <Moon size={13} style={{ color: '#a5b4fc' }} /> Moon
                    </span>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{moonSign}</span>
                  </div>
                )}
                {ascSign && (
                  <div style={dataRow}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
                      <Star size={13} style={{ color: '#f472b6' }} /> Ascendant
                    </span>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{ascSign}</span>
                  </div>
                )}
              </div>
            )}

            {/* Current Dasha */}
            {currentDasha && (
              <div style={{ marginBottom: 20 }}>
                <div style={sectionLabel}>Current Dasha</div>
                {currentDasha.mahadasha && (
                  <div style={{
                    padding: '10px 12px', borderRadius: 8,
                    background: 'rgba(245,166,35,0.06)', border: '1px solid rgba(245,166,35,0.15)',
                    marginBottom: 8,
                  }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 2 }}>Mahadasha</div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--gold)' }}>
                      {currentDasha.mahadasha.planet}
                    </div>
                    {currentDasha.mahadasha.end_date && (
                      <div style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 2 }}>
                        <Clock size={10} style={{ marginRight: 3, verticalAlign: -1 }} />
                        Until {new Date(currentDasha.mahadasha.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </div>
                    )}
                  </div>
                )}
                {currentDasha.antardasha && (
                  <div style={{
                    padding: '10px 12px', borderRadius: 8,
                    background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.15)',
                  }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 2 }}>Antardasha</div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: '#818cf8' }}>
                      {currentDasha.antardasha.planet}
                    </div>
                    {currentDasha.antardasha.end_date && (
                      <div style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 2 }}>
                        <Clock size={10} style={{ marginRight: 3, verticalAlign: -1 }} />
                        Until {new Date(currentDasha.antardasha.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Active Transits */}
            {transits.length > 0 && (
              <div>
                <div style={sectionLabel}>Active Transits</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {transits.map((t, i) => (
                    <div key={i} style={{
                      padding: '8px 10px', borderRadius: 8,
                      background: 'var(--background)', border: '1px solid var(--border)',
                    }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2, display: 'flex', alignItems: 'center', gap: 4 }}>
                        <ArrowUpRight size={11} style={{ color: 'var(--gold)' }} />
                        {t.transiting_planet} {t.aspect_type} {t.natal_planet}
                      </div>
                      {t.description && (
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                          {t.description.length > 80 ? t.description.slice(0, 80) + '...' : t.description}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/* ---------- Component ---------- */

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

  // Auto-expand sidebar on desktop when a profile is selected, collapse on mobile
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
      const res = await apiClient.post<any>('/api/v1/ai/interpret', { chart_id: chartId, question: q, style });
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
