'use client';

import React, { useState } from 'react';
import AppSidebar from '@/components/layout/app-sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--background)' }}>
      {/* Sidebar */}
      <aside
        className="fixed inset-y-0 left-0 z-30 overflow-visible transition-[width] duration-200"
        style={{ width: collapsed ? 64 : 240 }}
      >
        <AppSidebar collapsed={collapsed} onToggleCollapse={() => setCollapsed(!collapsed)} />
      </aside>

      {/* Main area — no header, full content */}
      <div
        className="flex flex-1 flex-col transition-[margin-left] duration-200 min-w-0"
        style={{ marginLeft: collapsed ? 64 : 240 }}
      >
        <main className="flex-1 p-7">{children}</main>
      </div>
    </div>
  );
}
