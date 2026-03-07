'use client';

import { createContext, useContext, useMemo, useEffect } from 'react';
import { useAuth as useClerkAuth, useUser as useClerkUser } from '@clerk/nextjs';
import { setAsyncTokenGetter } from '@/lib/api-client';
import { setAsyncGraphQLTokenGetter } from '@/lib/graphql-client';

interface AuthContextType {
  user: {
    id: string;
    auth_provider_id: string;
    email: string;
    name: string;
    phone?: string;
    subscription_tier: string;
    roles: string[];
  } | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  getToken: () => Promise<string | null>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  getToken: async () => null,
  logout: async () => {},
});

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn, getToken, signOut } = useClerkAuth();
  const { user: clerkUser, isLoaded: isUserLoaded } = useClerkUser();

  // Wire the async token getter into the API and GraphQL clients
  useEffect(() => {
    setAsyncTokenGetter(getToken);
    setAsyncGraphQLTokenGetter(getToken);
  }, [getToken]);

  const user = useMemo(() => {
    if (!isSignedIn || !clerkUser) return null;

    const publicMetadata = (clerkUser.publicMetadata as Record<string, any>) || {};

    return {
      id: publicMetadata.josi_user_id || '',
      auth_provider_id: clerkUser.id,
      email: clerkUser.primaryEmailAddress?.emailAddress || '',
      name: clerkUser.fullName || clerkUser.firstName || '',
      phone: clerkUser.primaryPhoneNumber?.phoneNumber || undefined,
      subscription_tier: publicMetadata.josi_subscription_tier || 'Free',
      roles: publicMetadata.josi_roles || ['user'],
    };
  }, [isSignedIn, clerkUser]);

  const logout = async () => {
    await signOut();
    window.location.href = '/auth/login';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading: !isLoaded || !isUserLoaded,
        isAuthenticated: !!isSignedIn,
        getToken,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
