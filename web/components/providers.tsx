'use client';

import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import { ConfigProvider } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthContextProvider } from '@/contexts/AuthContext';
import { SubscriptionProvider } from '@/contexts/SubscriptionContext';
import themeConfig from '@/theme/themeConfig';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: '#6b5ce7',
          colorBackground: '#1a1230',
        },
      }}
    >
      <AntdRegistry>
        <ConfigProvider theme={themeConfig}>
          <QueryClientProvider client={queryClient}>
            <AuthContextProvider>
              <SubscriptionProvider>
                {children}
              </SubscriptionProvider>
            </AuthContextProvider>
          </QueryClientProvider>
        </ConfigProvider>
      </AntdRegistry>
    </ClerkProvider>
  );
}
