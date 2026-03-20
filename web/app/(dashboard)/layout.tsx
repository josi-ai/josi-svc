'use client';

import React, { useState } from 'react';
import AppSidebar from '@/components/layout/app-sidebar';
import UserDropdown from '@/components/layout/user-dropdown';
import { useAuth } from '@/contexts/AuthContext';
import { PanelLeftClose, PanelLeftOpen, Plus } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const { user } = useAuth();

  const displayName = user?.full_name || user?.email || 'User';
  const initials = displayName.charAt(0).toUpperCase();

  const now = new Date();
  const hour = now.getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside
        className="fixed inset-y-0 left-0 z-30 overflow-y-auto transition-[width] duration-200"
        style={{ width: collapsed ? 64 : 240 }}
      >
        <AppSidebar collapsed={collapsed} />
      </aside>

      {/* Main area */}
      <div
        className="flex flex-1 flex-col transition-[margin-left] duration-200"
        style={{ marginLeft: collapsed ? 64 : 240 }}
      >
        {/* Header */}
        <header className="sticky top-0 z-20 flex items-center justify-between border-b border-subtle bg-surface px-7 py-3">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="flex h-8 w-8 items-center justify-center rounded-md text-text-muted hover:bg-card hover:text-text-secondary transition-colors"
            >
              {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
            </button>
            <div className="text-sm text-text-muted">
              {greeting}, <strong className="text-text-primary font-semibold">{displayName}</strong>
              <span className="ml-3 text-text-faint">{dateStr}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="bg-[var(--gold)] text-[var(--btn-add-text)] px-4 py-2 rounded-lg font-semibold text-sm flex items-center gap-1.5 hover:opacity-90 transition-opacity">
              <Plus className="h-3.5 w-3.5" /> Add Widget
            </button>
            <UserDropdown initials={initials} />
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-7">{children}</main>
      </div>
    </div>
  );
}
