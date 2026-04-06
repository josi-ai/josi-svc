'use client';

import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';
import { ThemeProvider, useTheme } from 'next-themes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthContextProvider } from '@/contexts/AuthContext';
import { CLERK_COLORS } from '@/config/clerk-theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function ClerkThemeWrapper({ children }: { children: React.ReactNode }) {
  const { resolvedTheme } = useTheme();
  return (
    <ClerkProvider
      appearance={{
        baseTheme: resolvedTheme === 'dark' ? dark : undefined,
        variables: {
          colorPrimary: CLERK_COLORS.primary,
        },
      }}
    >
      {children}
    </ClerkProvider>
  );
}

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <ClerkThemeWrapper>
        <QueryClientProvider client={queryClient}>
          <AuthContextProvider>
              {children}
          </AuthContextProvider>
        </QueryClientProvider>
      </ClerkThemeWrapper>
    </ThemeProvider>
  );
}
