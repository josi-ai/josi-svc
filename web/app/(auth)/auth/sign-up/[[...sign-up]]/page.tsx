'use client';

import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at top, #1a1230 0%, #0f0a1e 50%)',
    }}>
      <SignUp
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
