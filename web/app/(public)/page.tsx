'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';

const Observatory = dynamic(() => import('./page-observatory'));
const Mirror = dynamic(() => import('./page-mirror'));

const isDev = process.env.NODE_ENV === 'development';

export default function LandingPage() {
  const [variant, setVariant] = useState<'A' | 'B'>('A');

  return (
    <>
      {isDev && (
        <div
          className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[9999] flex items-center gap-1 rounded-full px-1 py-1 text-xs font-semibold"
          style={{
            background: 'rgba(10,15,30,0.85)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(200,145,58,0.25)',
          }}
        >
          <button
            onClick={() => setVariant('A')}
            className="px-4 py-1.5 rounded-full transition-all"
            style={{
              background: variant === 'A' ? '#C8913A' : 'transparent',
              color: variant === 'A' ? '#060A14' : '#7B8CA8',
            }}
          >
            A · Observatory
          </button>
          <button
            onClick={() => setVariant('B')}
            className="px-4 py-1.5 rounded-full transition-all"
            style={{
              background: variant === 'B' ? '#C8913A' : 'transparent',
              color: variant === 'B' ? '#060A14' : '#7B8CA8',
            }}
          >
            B · Mirror
          </button>
        </div>
      )}
      {variant === 'A' ? <Observatory /> : <Mirror />}
    </>
  );
}
