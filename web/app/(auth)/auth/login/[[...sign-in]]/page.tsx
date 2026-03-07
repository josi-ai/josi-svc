'use client';

import { SignIn } from '@clerk/nextjs';

export default function LoginPage() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at top, #1a1230 0%, #0f0a1e 50%)',
    }}>
      <SignIn
        fallbackRedirectUrl="/dashboard"
        appearance={{
          elements: {
            rootBox: { width: '100%', maxWidth: 400 },
          },
        }}
      />
    </div>
  );
}
