'use client';

import { useRef, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { pColor, fmtDate, CARD, LABEL, PLANET_INTERPRETATIONS } from './dasha-helpers';

export function DashaInterpretationPanel({ planet, startDate, endDate, onClose }: {
  planet: string;
  startDate: string;
  endDate: string;
  onClose: () => void;
}) {
  const router = useRouter();
  const interp = PLANET_INTERPRETATIONS[planet];
  const panelRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    if (panelRef.current) {
      setHeight(panelRef.current.scrollHeight);
    }
  }, [planet]);

  if (!interp) return null;

  return (
    <div
      style={{
        overflow: 'hidden',
        maxHeight: height || 'none',
        transition: 'max-height 0.3s ease',
      }}
    >
      <div
        ref={panelRef}
        style={{
          ...CARD,
          borderColor: pColor(planet),
          borderWidth: 1,
          borderStyle: 'solid',
          marginTop: 8,
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 8,
              background: pColor(planet) + '22',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <div style={{ width: 14, height: 14, borderRadius: 4, background: pColor(planet) }} />
            </div>
            <div>
              <h4 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                {planet} Dasha
              </h4>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0 }}>
                {fmtDate(startDate)} &ndash; {fmtDate(endDate)}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); onClose(); }}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: 18, color: 'var(--text-muted)', padding: '2px 6px', lineHeight: 1,
            }}
          >
            &times;
          </button>
        </div>

        {/* Theme */}
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 16 }}>
          {interp.theme}
        </p>

        {/* Life Areas */}
        <div style={{ marginBottom: 16 }}>
          <p style={{ ...LABEL, marginBottom: 8 }}>Life Areas Affected</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {interp.areas.map((area) => (
              <span key={area} style={{
                fontSize: 11, padding: '4px 10px', borderRadius: 20,
                background: pColor(planet) + '15', color: pColor(planet),
                fontWeight: 500,
              }}>
                {area}
              </span>
            ))}
          </div>
        </div>

        {/* Do / Don't */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <div>
            <p style={{ ...LABEL, color: 'var(--green)', marginBottom: 8 }}>Do</p>
            {interp.doAdvice.map((item) => (
              <div key={item} style={{ display: 'flex', gap: 6, alignItems: 'flex-start', marginBottom: 6 }}>
                <span style={{ color: 'var(--green)', fontSize: 12, lineHeight: '18px' }}>+</span>
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: '18px' }}>{item}</span>
              </div>
            ))}
          </div>
          <div>
            <p style={{ ...LABEL, color: 'var(--red)', marginBottom: 8 }}>Don&apos;t</p>
            {interp.dontAdvice.map((item) => (
              <div key={item} style={{ display: 'flex', gap: 6, alignItems: 'flex-start', marginBottom: 6 }}>
                <span style={{ color: 'var(--red)', fontSize: 12, lineHeight: '18px' }}>&minus;</span>
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: '18px' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Ask AI */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            router.push(`/ai?q=${encodeURIComponent(`Tell me about my ${planet} dasha period`)}`);
          }}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '8px 16px', fontSize: 12, fontWeight: 600,
            color: 'var(--gold)', background: 'rgba(212,175,55,0.1)',
            border: '1px solid rgba(212,175,55,0.25)', borderRadius: 8,
            cursor: 'pointer', transition: 'background 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(212,175,55,0.18)')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(212,175,55,0.1)')}
        >
          Ask AI about this period
        </button>
      </div>
    </div>
  );
}
