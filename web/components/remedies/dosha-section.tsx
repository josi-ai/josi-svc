'use client';

import { AlertTriangle } from 'lucide-react';

export function DoshaSection({ doshas }: { doshas: { name: string; description: string }[] }) {
  if (!doshas.length) return null;

  return (
    <div
      style={{
        background: 'rgba(239,68,68,0.06)',
        border: '1px solid rgba(239,68,68,0.18)',
        borderRadius: 12,
        padding: 18,
        marginBottom: 20,
      }}
    >
      <h3
        style={{
          fontSize: 15,
          fontWeight: 600,
          color: 'var(--red)',
          marginBottom: 10,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}
      >
        <AlertTriangle size={16} />
        Detected Doshas
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {doshas.map((d, i) => (
          <div key={i} style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            <strong style={{ color: 'var(--text-primary)' }}>{d.name}</strong>
            {d.description && ` - ${d.description}`}
          </div>
        ))}
      </div>
    </div>
  );
}
