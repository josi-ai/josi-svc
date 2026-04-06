'use client';

import React from 'react';
import Link from 'next/link';
import { type CulturalEvent, getTraditionStyle, formatDateRange } from './event-types';

export function SkeletonCards() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {[1, 2, 3].map((i) => (
        <div key={i} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 24 }}>
          <div style={{ height: 18, width: '40%', background: 'var(--border)', borderRadius: 6, marginBottom: 12 }} />
          <div style={{ height: 12, width: '25%', background: 'var(--border)', borderRadius: 4, marginBottom: 16 }} />
          <div style={{ height: 12, width: '90%', background: 'var(--border)', borderRadius: 4, marginBottom: 8 }} />
          <div style={{ height: 12, width: '70%', background: 'var(--border)', borderRadius: 4 }} />
        </div>
      ))}
    </div>
  );
}

export function EmptyState() {
  return (
    <div style={{ textAlign: 'center', padding: '60px 24px', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14 }}>
      <div style={{ fontSize: 40, marginBottom: 16 }}>&#x1F3AA;</div>
      <h3 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 8px' }}>No events to display</h3>
      <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: '0 0 20px', maxWidth: 400, marginInline: 'auto' }}>
        Set your ethnicity in Settings to see cultural events relevant to your background.
      </p>
      <Link href="/settings" style={{ display: 'inline-block', padding: '10px 24px', fontSize: 14, fontWeight: 600, color: 'var(--primary-foreground)', background: 'var(--gold)', borderRadius: 10, textDecoration: 'none' }}>
        Go to Settings
      </Link>
    </div>
  );
}

export function EventCard({ event }: { event: CulturalEvent }) {
  const style = getTraditionStyle(event.tradition);
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 24, transition: 'border-color 0.15s' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontSize: 17, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{event.name}</h3>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '4px 0 0' }}>{formatDateRange(event.date_2026, event.end_date_2026)}</p>
        </div>
        <span style={{ padding: '4px 10px', fontSize: 11, fontWeight: 600, borderRadius: 20, background: style.bg, color: style.text, whiteSpace: 'nowrap', flexShrink: 0 }}>{event.tradition}</span>
      </div>
      <p style={{ fontSize: 14, color: 'var(--text-secondary)', margin: '12px 0 0', lineHeight: 1.5 }}>{event.description}</p>
      {event.significance && (
        <div style={{ margin: '14px 0 0', padding: '12px 14px', borderRadius: 10, background: 'var(--background)', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.2px', color: 'var(--text-faint)', marginBottom: 6 }}>Significance</div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.55 }}>{event.significance}</p>
        </div>
      )}
      {event.rituals && event.rituals.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.2px', color: 'var(--text-faint)', marginBottom: 8 }}>Rituals &amp; Observances</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {event.rituals.map((r) => (
              <span key={r} style={{ padding: '4px 10px', fontSize: 12, color: 'var(--text-secondary)', background: 'var(--background)', border: '1px solid var(--border)', borderRadius: 16 }}>{r}</span>
            ))}
          </div>
        </div>
      )}
      {event.astrological_significance && (
        <div style={{ marginTop: 14, display: 'flex', alignItems: 'flex-start', gap: 8 }}>
          <span style={{ fontSize: 14, flexShrink: 0, marginTop: 1 }}>&#x2728;</span>
          <p style={{ fontSize: 12, color: 'var(--gold)', margin: 0, lineHeight: 1.5, fontStyle: 'italic' }}>{event.astrological_significance}</p>
        </div>
      )}
    </div>
  );
}
