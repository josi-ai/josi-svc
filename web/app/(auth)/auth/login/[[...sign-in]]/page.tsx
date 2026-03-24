'use client';

import { useEffect, useState } from 'react';
import { SignIn, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const { isLoaded, isSignedIn, signOut } = useAuth();
  const router = useRouter();
  const [stale, setStale] = useState(false);

  useEffect(() => {
    if (!isLoaded) return;

    // If signed in and session is valid, redirect to dashboard
    if (isSignedIn) {
      router.replace('/dashboard');
      return;
    }

    // If Clerk is loaded but not signed in, the form should show.
    // But if the page stays blank for 3s, Clerk has a stale cookie —
    // force sign out to clear it.
    const timer = setTimeout(() => {
      const signInEl = document.querySelector('[data-clerk-component="SignIn"]');
      if (!signInEl || signInEl.children.length === 0) {
        setStale(true);
        signOut().catch(() => {});
      }
    }, 3000);

    return () => clearTimeout(timer);
  }, [isLoaded, isSignedIn, router, signOut]);

  if (stale) {
    return (
      <div style={{ textAlign: 'center', color: '#9b95b0' }}>
        <p>Session expired. Refreshing...</p>
      </div>
    );
  }

  return (
    <SignIn
      signUpUrl="/auth/sign-up"
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
