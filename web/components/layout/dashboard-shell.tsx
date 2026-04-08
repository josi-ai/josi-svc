'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import AppSidebar from '@/components/layout/app-sidebar';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api-client';

interface PersonCheck {
  person_id: string;
  date_of_birth: string | null;
  time_of_birth: string | null;
  place_of_birth: string | null;
  is_default?: boolean;
}

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  const { user, isAuthReady } = useAuth();

  useEffect(() => setMounted(true), []);

  // Fetch the user's profiles to check if onboarding is needed
  const { data: personsResponse, isLoading: personsLoading } = useQuery({
    queryKey: ['persons'],
    queryFn: () => apiClient.get<PersonCheck[]>('/api/v1/persons/'),
    enabled: isAuthReady && !!user,
  });

  // Check if user needs onboarding
  useEffect(() => {
    if (!mounted || !isAuthReady || !user || personsLoading) return;
    if (!personsResponse) return;

    const persons = personsResponse.data || [];
    const defaultProfile = persons.find((p) => p.is_default) || persons[0];
    const needsOnboarding =
      !defaultProfile ||
      !defaultProfile.date_of_birth ||
      !defaultProfile.time_of_birth ||
      !defaultProfile.place_of_birth;

    if (needsOnboarding) {
      router.push('/onboarding');
    }
  }, [mounted, isAuthReady, user, personsResponse, personsLoading, router]);

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
