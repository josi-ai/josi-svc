'use client';

import { Descope } from '@descope/nextjs-sdk';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at top, #1a1230 0%, #0f0a1e 50%)',
    }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <Descope
          flowId="sign-up-or-in"
          onSuccess={() => router.push('/dashboard')}
          onError={(e) => console.error('Auth error:', e)}
          theme="dark"
        />
      </div>
    </div>
  );
}
