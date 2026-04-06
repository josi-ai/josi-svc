'use client';

import { Fragment, useState, useEffect } from 'react';
import React from 'react';

/* ---------- Style Constants ---------- */

export const S = {
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

/* ---------- Render Helpers ---------- */

export function renderContent(text: string) {
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
  let last = 0;
  let match: RegExpExecArray | null;
  let k = 0;
  while ((match = re.exec(text)) !== null) {
    if (match.index > last) nodes.push(text.slice(last, match.index));
    if (match[2]) nodes.push(<strong key={k++}>{match[2]}</strong>);
    else if (match[3]) nodes.push(<em key={k++}>{match[3]}</em>);
    last = match.index + match[0].length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

export function TypingDot({ delay }: { delay: number }) {
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
