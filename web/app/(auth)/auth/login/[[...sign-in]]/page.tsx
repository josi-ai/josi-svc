'use client';

import { SignIn } from '@clerk/nextjs';
import { CLERK_COLORS } from '@/config/clerk-theme';

export default function LoginPage() {
  return (
    <SignIn
      signUpUrl="/auth/sign-up"
      fallbackRedirectUrl="/dashboard"
      appearance={{
        elements: {
          rootBox: { width: '100%', maxWidth: 400 },
          headerTitle: { color: CLERK_COLORS.headerTitle },
          headerSubtitle: { color: CLERK_COLORS.headerSubtitle },
        },
      }}
    />
  );
}
