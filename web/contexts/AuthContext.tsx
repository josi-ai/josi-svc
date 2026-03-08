'use client';

import { createContext, useContext, useMemo, useEffect, useState, useCallback } from 'react';
import { useAuth as useClerkAuth } from '@clerk/nextjs';
import { setAsyncTokenGetter } from '@/lib/api-client';
import { setAsyncGraphQLTokenGetter } from '@/lib/graphql-client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  phone?: string;
  subscription_tier_id?: number;
  subscription_tier_name?: string;
  roles: string[];
  is_active: boolean;
  is_verified: boolean;
}

interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  getToken: () => Promise<string | null>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  getToken: async () => null,
  logout: async () => {},
  refreshUser: async () => {},
});

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn, getToken, signOut } = useClerkAuth();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isFetching, setIsFetching] = useState(false);

  // Wire the async token getter into the API and GraphQL clients
  useEffect(() => {
    setAsyncTokenGetter(getToken);
    setAsyncGraphQLTokenGetter(getToken);
  }, [getToken]);

  const fetchProfile = useCallback(async () => {
    if (!isSignedIn) return;
    setIsFetching(true);
    try {
      const token = await getToken();
      if (!token) return;
      const res = await fetch(`${API_URL}/api/v1/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      }
    } catch (err) {
      console.warn('Failed to fetch user profile:', err);
    } finally {
      setIsFetching(false);
    }
  }, [isSignedIn, getToken]);

  useEffect(() => {
    if (isSignedIn) {
      fetchProfile();
    } else {
      setUser(null);
    }
  }, [isSignedIn, fetchProfile]);

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

  const value = useMemo(
    () => ({
      user,
      isLoading: !isLoaded || isFetching,
      isAuthenticated: !!isSignedIn,
      getToken,
      logout,
      refreshUser: fetchProfile,
    }),
    [user, isLoaded, isFetching, isSignedIn, getToken, logout, fetchProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
