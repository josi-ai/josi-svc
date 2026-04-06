'use client';

import type { PanchangData } from './panchang-types';
import { formatPercent, qualityColor } from './panchang-helpers';
import { ElementRow } from './panchang-shared';

export function FiveElementsCard({ data }: { data: PanchangData }) {
  const { tithi, nakshatra, yoga, karana, vara } = data;

  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 20 }}>
      <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, color: 'var(--text-primary)', marginBottom: 16 }}>
        Five Elements
      </h3>

      {/* Tithi */}
      <ElementRow label="Tithi" value={tithi?.name || '\u2014'} sub={tithi?.paksha ? `${tithi.paksha} Paksha` : undefined} />
      {tithi?.deity && (
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>Deity: {tithi.deity}</span>
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{formatPercent(tithi.percent)} elapsed</span>
        </div>
      )}

      {/* Nakshatra */}
      <ElementRow label="Nakshatra" value={nakshatra?.name || '\u2014'} sub={nakshatra?.pada ? `Pada ${nakshatra.pada}` : undefined} />
      {nakshatra?.ruler && (
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>Ruler: {nakshatra.ruler}</span>
          {nakshatra.deity && <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>Deity: {nakshatra.deity}</span>}
        </div>
      )}

      {/* Yoga */}
      <ElementRow label="Yoga" value={yoga?.name || '\u2014'} sub={yoga?.quality ? yoga.quality : undefined} />
      {yoga?.quality && (
        <div style={{ padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: qualityColor(yoga.quality), fontWeight: 600 }}>{yoga.quality}</span>
        </div>
      )}

      {/* Karana */}
      <ElementRow label="Karana" value={karana?.name || '\u2014'} sub={karana?.quality ? karana.quality : undefined} />
      {karana?.quality && (
        <div style={{ padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: qualityColor(karana.quality), fontWeight: 600 }}>{karana.quality}</span>
        </div>
      )}

      {/* Vara */}
      <ElementRow label="Vara" value={vara?.day || '\u2014'} sub={vara?.ruler ? `Ruler: ${vara.ruler}` : undefined} />
    </div>
  );
}
