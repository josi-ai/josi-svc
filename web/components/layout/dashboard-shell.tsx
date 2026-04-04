'use client';

import React, { useState, useEffect } from 'react';
import AppSidebar from '@/components/layout/app-sidebar';

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  // Don't render anything until client-side mount — eliminates all hydration mismatches
  if (!mounted) {
    return (
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
    );
  }

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
