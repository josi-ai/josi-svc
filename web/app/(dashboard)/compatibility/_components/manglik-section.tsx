'use client';

import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import type { ManglikStatus } from './compatibility-types';

function ManglikPerson({ name, isManglik }: { name: string; isManglik: boolean }) {
  return (
    <div
      style={{
        padding: 12,
        borderRadius: 8,
        background: isManglik ? 'var(--red-bg)' : 'var(--green-bg)',
        display: 'flex', alignItems: 'center', gap: 8,
      }}
    >
      {isManglik
        ? <XCircle style={{ width: 14, height: 14, color: 'var(--red)', flexShrink: 0 }} />
        : <CheckCircle style={{ width: 14, height: 14, color: 'var(--green)', flexShrink: 0 }} />}
      <div>
        <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>{name}</p>
        <p style={{ fontSize: 11, color: isManglik ? 'var(--red)' : 'var(--green)' }}>
          {isManglik ? 'Manglik' : 'Non-Manglik'}
        </p>
      </div>
    </div>
  );
}

export function ManglikSection({ status, person1Name, person2Name }: {
  status: ManglikStatus;
  person1Name: string;
  person2Name: string;
}) {
  const match = status.manglik_match;

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        padding: 20,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <div
          style={{
            width: 32, height: 32, borderRadius: 10,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: match ? 'var(--green-bg)' : 'var(--red-bg)',
          }}
        >
          {match
            ? <CheckCircle style={{ width: 16, height: 16, color: 'var(--green)' }} />
            : <AlertTriangle style={{ width: 16, height: 16, color: 'var(--red)' }} />}
        </div>
        <div>
          <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
            Manglik Dosha
          </h4>
          <p style={{ fontSize: 11, color: match ? 'var(--green)' : 'var(--red)', fontWeight: 500 }}>
            {match ? 'Compatible' : 'Mismatch detected'}
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <ManglikPerson name={person1Name} isManglik={status.person1} />
        <ManglikPerson name={person2Name} isManglik={status.person2} />
      </div>

      {!match && (
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 14, lineHeight: 1.5 }}>
          One partner is Manglik while the other is not. Traditional Vedic astrology recommends
          specific remedies such as Kumbh Vivah or matching with another Manglik partner.
        </p>
      )}
    </div>
  );
}
