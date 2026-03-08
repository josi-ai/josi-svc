'use client';

import { SignIn } from '@clerk/nextjs';

export default function LoginPage() {
  return (
    <SignIn
      fallbackRedirectUrl="/dashboard"
      appearance={{
        elements: {
          rootBox: { width: '100%', maxWidth: 400 },
          headerTitle: { color: '#e2dff0' },
          headerSubtitle: { color: '#9b95b0' },
        },
      }}
    />
  );
}
