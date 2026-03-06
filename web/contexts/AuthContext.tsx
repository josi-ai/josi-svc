'use client';

import { createContext, useContext, useMemo, useEffect } from 'react';
import { useSession, useUser, useDescope } from '@descope/nextjs-sdk/client';
import { setTokenGetter } from '@/lib/api-client';
import { setGraphQLTokenGetter } from '@/lib/graphql-client';

interface AuthContextType {
  user: {
    id: string;
    descope_id: string;
    email: string;
    name: string;
    phone?: string;
    subscription_tier: string;
    roles: string[];
  } | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  sessionToken: string | undefined;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  sessionToken: undefined,
  logout: async () => {},
});

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isSessionLoading, sessionToken } = useSession();
  const { user: descopeUser, isUserLoading } = useUser();
  const { logout: descopeLogout } = useDescope();

  // Wire the session token into the API and GraphQL clients
  useEffect(() => {
    setTokenGetter(() => sessionToken);
    setGraphQLTokenGetter(() => sessionToken);
  }, [sessionToken]);

  const user = useMemo(() => {
    if (!isAuthenticated || !descopeUser) return null;

    // Read custom claims from the session token
    let claims: Record<string, any> = {};
    if (sessionToken) {
      try {
        const payload = JSON.parse(atob(sessionToken.split('.')[1]));
        claims = payload;
      } catch {
        // Token parse error — use defaults
      }
    }

    return {
      id: claims.josi_user_id || '',
      descope_id: descopeUser.userId || '',
      email: descopeUser.email || '',
      name: descopeUser.name || '',
      phone: descopeUser.phone || undefined,
      subscription_tier: claims.josi_subscription_tier || 'free',
      roles: claims.josi_roles || ['user'],
    };
  }, [isAuthenticated, descopeUser, sessionToken]);

  const logout = async () => {
    await descopeLogout();
    window.location.href = '/auth/login';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading: isSessionLoading || isUserLoading,
        isAuthenticated,
        sessionToken,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
