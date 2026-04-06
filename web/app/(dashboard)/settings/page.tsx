'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

import type { UserProfile, Tab } from './_components/settings-types';
import { TABS } from './_components/settings-types';
import { cardStyle } from './_components/settings-shared';
import { AccountTab } from './_components/account-tab';
import { SubscriptionTab } from './_components/subscription-tab';
import { NotificationsTab } from './_components/notifications-tab';
import { ChartDefaultsTab } from './_components/chart-defaults-tab';
import { DisplayTab } from './_components/display-tab';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('Account');
  const { isAuthReady } = useAuth();

  const { data: profileData, isLoading } = useQuery({
    queryKey: ['me-profile'],
    queryFn: () => apiClient.get<UserProfile>('/api/v1/me'),
    enabled: isAuthReady,
  });

  const profile = profileData?.data;

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: '32px 16px' }}>
      {/* Header */}
      <h1
        className="font-display"
        style={{ fontSize: 28, color: 'var(--text-primary)', fontWeight: 400, marginBottom: 24 }}
      >
        Settings
      </h1>

      {/* Tabs */}
      <div
        style={{
          display: 'flex',
          gap: 0,
          borderBottom: '1px solid var(--border)',
          marginBottom: 24,
          overflowX: 'auto',
        }}
      >
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 16px',
              fontSize: 13,
              fontWeight: 500,
              color: activeTab === tab ? 'var(--gold)' : 'var(--text-muted)',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid var(--gold)' : '2px solid transparent',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'color 0.15s, border-color 0.15s',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={cardStyle}>
        {isLoading || !profile ? (
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading settings...</p>
        ) : (
          <>
            {activeTab === 'Account' && <AccountTab profile={profile} />}
            {activeTab === 'Subscription' && <SubscriptionTab />}
            {activeTab === 'Notifications' && <NotificationsTab profile={profile} />}
            {activeTab === 'Chart Defaults' && <ChartDefaultsTab profile={profile} />}
            {activeTab === 'Display' && <DisplayTab profile={profile} />}
          </>
        )}
      </div>
    </div>
  );
}
