'use client';

import { createContext, useContext, useMemo, useEffect, useCallback } from 'react';
import { useAuth as useClerkAuth, useUser as useClerkUser } from '@clerk/nextjs';
import { setAsyncTokenGetter, signalAuthReady, signalAuthReset } from '@/lib/api-client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UserProfile {
  user_id: string;
  auth_provider_id: string;
  email: string;
  full_name: string;
  phone?: string;
  language_preference?: string | null;
  subscription_tier_name?: string;
  subscription_tier_id?: number;
  roles: string[];
  is_active: boolean;
  is_verified: boolean;
}

interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  /** True once Clerk is loaded AND signed in — safe to fire authenticated API calls */
  isAuthReady: boolean;
  getToken: () => Promise<string | null>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  isAuthReady: false,
  getToken: async () => null,
  logout: async () => {},
  refreshUser: async () => {},
});

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn, getToken, signOut } = useClerkAuth();
  const { user: clerkUser, isLoaded: isUserLoaded } = useClerkUser();

  const isAuthReady = isLoaded && !!isSignedIn;

  // Wire the async token getter into the API client
  setAsyncTokenGetter(getToken);

  // Signal to apiClient that auth is ready (resolves the wait promise)
  useEffect(() => {
    if (isAuthReady) {
      signalAuthReady();
    } else if (isLoaded && !isSignedIn) {
      // Not signed in — release the gate so public API calls don't hang
      signalAuthReady();
    }
    return () => {
      signalAuthReset();
    };
  }, [isAuthReady, isLoaded, isSignedIn]);

  // Build user profile from Clerk user + publicMetadata (no API call needed)
  const user: UserProfile | null = useMemo(() => {
    if (!isSignedIn || !clerkUser) return null;

    const publicMetadata = (clerkUser.publicMetadata || {}) as Record<string, unknown>;

    return {
      user_id: (publicMetadata.josi_user_id as string) || '',
      auth_provider_id: clerkUser.id,
      email: clerkUser.primaryEmailAddress?.emailAddress || '',
      full_name: clerkUser.fullName || clerkUser.firstName || '',
      phone: clerkUser.primaryPhoneNumber?.phoneNumber,
      subscription_tier_name: (publicMetadata.josi_subscription_tier as string) || 'Free',
      subscription_tier_id: (publicMetadata.josi_subscription_tier_id as number) || 1,
      roles: (publicMetadata.josi_roles as string[]) || ['user'],
      language_preference: (publicMetadata.josi_language_preference as string) || null,
      is_active: (publicMetadata.josi_is_active as boolean) ?? true,
      is_verified: (publicMetadata.josi_is_verified as boolean) ?? false,
    };
  }, [isSignedIn, clerkUser]);

  const logout = useCallback(async () => {
    try {
      const token = await getToken();
      if (token) {
        await fetch(`${API_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch {
      // Non-fatal — proceed with sign-out regardless
    }
    await signOut();
    window.location.href = '/auth/login';
  }, [getToken, signOut]);

  const refreshUser = useCallback(async () => {
    // Clerk SDK automatically reflects updated publicMetadata after
    // the next token refresh. Calling clerkUser.reload() forces it.
    if (clerkUser) {
      await clerkUser.reload();
    }
  }, [clerkUser]);

  const value = useMemo(
    () => ({
      user,
      isLoading: !isLoaded || !isUserLoaded,
      isAuthenticated: !!isSignedIn,
      isAuthReady,
      getToken,
      logout,
      refreshUser,
    }),
    [user, isLoaded, isUserLoaded, isSignedIn, isAuthReady, getToken, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
