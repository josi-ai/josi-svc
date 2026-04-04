'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';

// The entire dashboard is client-only rendered. Every page behind auth uses
// useAuth/usePathname/useRouter/useQuery — all client hooks. There's zero SEO
// value (authenticated pages aren't crawlable). SSR just renders empty shells
// then hydration re-renders everything anyway, causing mismatches.
// Public pages (landing, pricing, chart-calculator) are in separate layout groups.
const AppSidebar = dynamic(() => import('@/components/layout/app-sidebar'), { ssr: false });

function DashboardShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--background)' }}>
      <aside
        className="fixed inset-y-0 left-0 z-30 overflow-visible transition-[width] duration-200"
        style={{ width: collapsed ? 64 : 240 }}
      >
        <AppSidebar collapsed={collapsed} onToggleCollapse={() => setCollapsed(!collapsed)} />
      </aside>
      <div
        className="flex flex-1 flex-col transition-[margin-left] duration-200 min-w-0"
        style={{ marginLeft: collapsed ? 64 : 240 }}
      >
        <main className="flex-1 p-7">{children}</main>
      </div>
    </div>
  );
}

// Wrap the entire dashboard layout in dynamic with ssr:false
const ClientDashboard = dynamic(
  () => Promise.resolve(DashboardShell),
  {
    ssr: false,
    loading: () => (
      <div
        style={{
          minHeight: '100vh',
          background: 'var(--background, #060a14)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div style={{ color: 'var(--text-muted, #5b6a8a)', fontSize: 14 }}>Loading...</div>
      </div>
    ),
  },
);

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <ClientDashboard>{children}</ClientDashboard>;
}
