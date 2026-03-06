'use client';

import { AuthProvider } from '@descope/nextjs-sdk';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import { ConfigProvider } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
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
    <AuthProvider projectId={process.env.NEXT_PUBLIC_DESCOPE_PROJECT_ID || 'P3AXgK6L8OgCfFSKcrNaA99vVChw'}>
      <AntdRegistry>
        <ConfigProvider theme={themeConfig}>
          <QueryClientProvider client={queryClient}>
            <SubscriptionProvider>
              {children}
            </SubscriptionProvider>
          </QueryClientProvider>
        </ConfigProvider>
      </AntdRegistry>
    </AuthProvider>
  );
}
