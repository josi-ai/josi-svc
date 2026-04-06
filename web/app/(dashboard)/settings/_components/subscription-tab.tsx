'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import Link from 'next/link';
import type { SubscriptionInfo, UsageInfo } from './settings-types';

export function SubscriptionTab() {
  const { data: subData, isLoading: subLoading } = useQuery({
    queryKey: ['me-subscription'],
    queryFn: () => apiClient.get<SubscriptionInfo>('/api/v1/me/subscription'),
  });
  const { data: usageData, isLoading: usageLoading } = useQuery({
    queryKey: ['me-usage'],
    queryFn: () => apiClient.get<UsageInfo>('/api/v1/me/usage'),
  });

  const sub = subData?.data;
  const usage = usageData?.data;

  if (subLoading || usageLoading) {
    return <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading subscription info...</p>;
  }

  const tierName = sub?.subscription_tier_name || 'Free';
  const isActive = sub?.is_active ?? true;
  const limits = sub?.limits || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Current Plan */}
      <div
        style={{
          padding: '20px 24px',
          borderRadius: 12,
          background: 'linear-gradient(135deg, rgba(245,166,35,0.08), rgba(245,166,35,0.02))',
          border: '1px solid rgba(245,166,35,0.2)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--text-faint)' }}>Current Plan</div>
            <div style={{ fontSize: 22, fontWeight: 600, color: 'var(--gold)', marginTop: 4 }}>{tierName}</div>
          </div>
          <span
            style={{
              padding: '4px 12px',
              fontSize: 11,
              fontWeight: 600,
              color: isActive ? 'var(--green)' : 'var(--red)',
              background: isActive ? 'var(--green-bg)' : 'var(--red-bg)',
              borderRadius: 20,
            }}
          >
            {isActive ? 'Active' : 'Expired'}
          </span>
        </div>
        {sub?.subscription_end_date && (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8, marginBottom: 0 }}>
            Renews: {new Date(sub.subscription_end_date).toLocaleDateString()}
          </p>
        )}
      </div>

      {/* Usage */}
      <div>
        <h4 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginTop: 0, marginBottom: 12 }}>This Month&apos;s Usage</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
          {Object.entries(limits).map(([key, limit]) => {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
            const used = (usage as any)?.[key] ?? 0;
            const pct = (limit as number) <= 0 ? 0 : (limit as number) === -1 ? 5 : Math.min((used / (limit as number)) * 100, 100);
            const displayLimit = (limit as number) === -1 ? 'Unlimited' : String(limit);
            return (
              <div key={key} style={{ padding: '12px 16px', borderRadius: 10, background: 'var(--background)', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 1 }}>{label}</div>
                <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', marginTop: 4 }}>
                  {used} <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--text-muted)' }}>/ {displayLimit}</span>
                </div>
                <div style={{ height: 4, borderRadius: 2, background: 'var(--border)', marginTop: 8 }}>
                  <div style={{ width: `${pct}%`, height: '100%', borderRadius: 2, background: pct > 90 ? 'var(--red)' : 'var(--gold)', transition: 'width 0.3s' }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <Link
        href="/pricing"
        style={{
          display: 'inline-flex',
          alignSelf: 'flex-start',
          padding: '10px 24px',
          fontSize: 14,
          fontWeight: 600,
          color: 'var(--primary-foreground)',
          background: 'var(--gold)',
          border: 'none',
          borderRadius: 10,
          textDecoration: 'none',
          cursor: 'pointer',
        }}
      >
        {tierName === 'Free' ? 'Upgrade Plan' : 'Change Plan'}
      </Link>
    </div>
  );
}
