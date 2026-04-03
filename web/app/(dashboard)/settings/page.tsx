'use client';

import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

/* ---------- Types ---------- */

interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  phone: string | null;
  avatar_url: string | null;
  ethnicity: string[] | null;
  subscription_tier_id: number | null;
  subscription_tier_name: string | null;
  subscription_end_date: string | null;
  roles: string[];
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  preferences: Record<string, any>;
  notification_settings: Record<string, any>;
}

interface SubscriptionInfo {
  subscription_tier_id: number;
  subscription_tier_name: string;
  subscription_end_date: string | null;
  is_active: boolean;
  has_premium: boolean;
  limits: Record<string, number>;
}

interface UsageInfo {
  charts_calculated?: number;
  ai_interpretations?: number;
  consultations?: number;
  [key: string]: any;
}

/* ---------- Constants ---------- */

const TABS = ['Account', 'Subscription', 'Notifications', 'Chart Defaults', 'Display'] as const;
type Tab = (typeof TABS)[number];

const ETHNICITY_OPTIONS = [
  'Tamil Hindu', 'North Indian Hindu', 'Bengali Hindu', 'South Indian Christian',
  'Keralite Hindu', 'Maharashtrian Hindu', 'Gujarati Hindu', 'Punjabi Hindu',
  'Muslim', 'Buddhist', 'Sikh', 'Jain', 'Christian', 'Other',
];

const TRADITIONS = [
  { value: 'vedic', label: 'Vedic' },
  { value: 'western', label: 'Western' },
  { value: 'chinese', label: 'Chinese' },
];
const HOUSE_SYSTEMS = [
  { value: 'whole_sign', label: 'Whole Sign' },
  { value: 'placidus', label: 'Placidus' },
  { value: 'koch', label: 'Koch' },
  { value: 'equal', label: 'Equal' },
];
const AYANAMSAS = [
  { value: 'lahiri', label: 'Lahiri' },
  { value: 'raman', label: 'Raman' },
  { value: 'kp', label: 'KP' },
];
const CHART_FORMATS = [
  { value: 'South Indian', label: 'South Indian' },
  { value: 'North Indian', label: 'North Indian' },
  { value: 'Western Wheel', label: 'Western Wheel' },
];

/* ---------- Styles ---------- */

const cardStyle: React.CSSProperties = {
  background: 'var(--card)',
  border: '1px solid var(--border)',
  borderRadius: 14,
  padding: 24,
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 10,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '1.5px',
  color: 'var(--text-faint)',
  marginBottom: 6,
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  fontSize: 14,
  color: 'var(--text-primary)',
  background: 'var(--background)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  outline: 'none',
  transition: 'border-color 0.2s',
  boxSizing: 'border-box',
};

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  appearance: 'none',
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235B6A8A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 12px center',
  paddingRight: 36,
};

const focusHandlers = {
  onFocus: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.target.style.borderColor = 'var(--gold)';
  },
  onBlur: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.target.style.borderColor = 'var(--border)';
  },
};

function SaveButton({ onClick, loading, disabled, label = 'Save Changes' }: { onClick: () => void; loading: boolean; disabled?: boolean; label?: string }) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      style={{
        marginTop: 20,
        padding: '10px 24px',
        fontSize: 14,
        fontWeight: 600,
        color: '#060A14',
        background: loading || disabled ? 'var(--border)' : 'var(--gold)',
        border: 'none',
        borderRadius: 10,
        cursor: loading || disabled ? 'not-allowed' : 'pointer',
        opacity: loading || disabled ? 0.6 : 1,
        transition: 'opacity 0.2s',
      }}
    >
      {loading ? 'Saving...' : label}
    </button>
  );
}

function SuccessBanner({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div
      style={{
        padding: '10px 14px',
        borderRadius: 8,
        fontSize: 13,
        color: '#30A46C',
        background: 'rgba(48,164,108,0.08)',
        border: '1px solid rgba(48,164,108,0.2)',
        marginBottom: 16,
      }}
    >
      {message}
    </div>
  );
}

/* ---------- Tab: Account ---------- */

function AccountTab({ profile }: { profile: UserProfile }) {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState(profile.full_name || '');
  const [phone, setPhone] = useState(profile.phone || '');
  const [ethnicity, setEthnicity] = useState<string[]>(profile.ethnicity || []);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    setFullName(profile.full_name || '');
    setPhone(profile.phone || '');
    setEthnicity(profile.ethnicity || []);
  }, [profile]);

  const mutation = useMutation({
    mutationFn: () =>
      apiClient.put('/api/v1/me', {
        full_name: fullName,
        phone: phone || null,
        ethnicity: ethnicity.length > 0 ? ethnicity : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me-profile'] });
      setSuccess('Account updated successfully');
      setTimeout(() => setSuccess(''), 3000);
    },
  });

  const toggleEthnicity = (val: string) => {
    setEthnicity((prev) => (prev.includes(val) ? prev.filter((e) => e !== val) : [...prev, val]));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <SuccessBanner message={success} />

      <div>
        <label style={labelStyle}>Full Name</label>
        <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} style={inputStyle} {...focusHandlers} />
      </div>

      <div>
        <label style={labelStyle}>Email</label>
        <input type="email" value={profile.email} readOnly style={{ ...inputStyle, opacity: 0.6, cursor: 'not-allowed' }} />
        <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 4 }}>Managed by your authentication provider</p>
      </div>

      <div>
        <label style={labelStyle}>Phone</label>
        <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+1 (555) 123-4567" style={inputStyle} {...focusHandlers} />
      </div>

      <div>
        <label style={labelStyle}>Ethnicity / Background</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {ETHNICITY_OPTIONS.map((opt) => {
            const selected = ethnicity.includes(opt);
            return (
              <button
                key={opt}
                type="button"
                onClick={() => toggleEthnicity(opt)}
                style={{
                  padding: '6px 12px',
                  fontSize: 12,
                  fontWeight: 500,
                  color: selected ? 'var(--gold)' : 'var(--text-secondary)',
                  background: selected ? 'rgba(245,166,35,0.1)' : 'var(--background)',
                  border: `1px solid ${selected ? 'var(--gold)' : 'var(--border)'}`,
                  borderRadius: 20,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                {opt}
              </button>
            );
          })}
        </div>
      </div>

      {mutation.isError && (
        <div style={{ padding: '10px 14px', borderRadius: 8, fontSize: 13, color: '#E5484D', background: 'rgba(229,72,77,0.08)', border: '1px solid rgba(229,72,77,0.2)' }}>
          {(mutation.error as Error)?.message || 'Failed to update'}
        </div>
      )}

      <SaveButton onClick={() => mutation.mutate()} loading={mutation.isPending} />
    </div>
  );
}

/* ---------- Tab: Subscription ---------- */

function SubscriptionTab() {
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
              color: isActive ? '#30A46C' : '#E5484D',
              background: isActive ? 'rgba(48,164,108,0.1)' : 'rgba(229,72,77,0.1)',
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
                  <div style={{ width: `${pct}%`, height: '100%', borderRadius: 2, background: pct > 90 ? '#E5484D' : 'var(--gold)', transition: 'width 0.3s' }} />
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
          color: '#060A14',
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

/* ---------- Tab: Notifications ---------- */

function NotificationsTab({ profile }: { profile: UserProfile }) {
  const queryClient = useQueryClient();
  const settings = profile.notification_settings || {};
  const [notifications, setNotifications] = useState({
    daily_predictions: settings.daily_predictions ?? false,
    transit_alerts: settings.transit_alerts ?? false,
    dasha_changes: settings.dasha_changes ?? false,
    consultation_reminders: settings.consultation_reminders ?? true,
  });
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const s = profile.notification_settings || {};
    setNotifications({
      daily_predictions: s.daily_predictions ?? false,
      transit_alerts: s.transit_alerts ?? false,
      dasha_changes: s.dasha_changes ?? false,
      consultation_reminders: s.consultation_reminders ?? true,
    });
  }, [profile]);

  const mutation = useMutation({
    mutationFn: () => apiClient.put('/api/v1/me', { notification_settings: notifications }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me-profile'] });
      setSuccess('Notification preferences saved');
      setTimeout(() => setSuccess(''), 3000);
    },
  });

  const toggleItems: { key: keyof typeof notifications; label: string; desc: string }[] = [
    { key: 'daily_predictions', label: 'Daily Predictions', desc: 'Receive daily astrological insights' },
    { key: 'transit_alerts', label: 'Transit Alerts', desc: 'Alerts when planets transit key positions' },
    { key: 'dasha_changes', label: 'Dasha Period Changes', desc: 'Notifications for dasha period transitions' },
    { key: 'consultation_reminders', label: 'Consultation Reminders', desc: 'Reminders for upcoming consultations' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      <SuccessBanner message={success} />
      {toggleItems.map((item, i) => (
        <div
          key={item.key}
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 0',
            borderBottom: i < toggleItems.length - 1 ? '1px solid var(--border)' : 'none',
          }}
        >
          <div>
            <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-primary)' }}>{item.label}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{item.desc}</div>
          </div>
          <button
            type="button"
            onClick={() => setNotifications((prev) => ({ ...prev, [item.key]: !prev[item.key] }))}
            style={{
              width: 44,
              height: 24,
              borderRadius: 12,
              border: 'none',
              background: notifications[item.key] ? 'var(--gold)' : 'var(--border)',
              cursor: 'pointer',
              position: 'relative',
              transition: 'background 0.2s',
              flexShrink: 0,
            }}
          >
            <span
              style={{
                position: 'absolute',
                top: 2,
                left: notifications[item.key] ? 22 : 2,
                width: 20,
                height: 20,
                borderRadius: '50%',
                background: '#fff',
                transition: 'left 0.2s',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
              }}
            />
          </button>
        </div>
      ))}

      {mutation.isError && (
        <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 8, fontSize: 13, color: '#E5484D', background: 'rgba(229,72,77,0.08)', border: '1px solid rgba(229,72,77,0.2)' }}>
          {(mutation.error as Error)?.message || 'Failed to save'}
        </div>
      )}

      <SaveButton onClick={() => mutation.mutate()} loading={mutation.isPending} />
    </div>
  );
}

/* ---------- Tab: Chart Defaults ---------- */

function ChartDefaultsTab({ profile }: { profile: UserProfile }) {
  const queryClient = useQueryClient();
  const prefs = profile.preferences?.chart || {};
  const [tradition, setTradition] = useState(prefs.default_tradition || 'vedic');
  const [houseSystem, setHouseSystem] = useState(prefs.default_house_system || 'whole_sign');
  const [ayanamsa, setAyanamsa] = useState(prefs.default_ayanamsa || 'lahiri');
  const [chartFormat, setChartFormat] = useState(prefs.default_format || 'South Indian');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const p = profile.preferences?.chart || {};
    setTradition(p.default_tradition || 'vedic');
    setHouseSystem(p.default_house_system || 'whole_sign');
    setAyanamsa(p.default_ayanamsa || 'lahiri');
    setChartFormat(p.default_format || 'South Indian');
  }, [profile]);

  const mutation = useMutation({
    mutationFn: () =>
      apiClient.put('/api/v1/me/preferences', {
        chart: {
          default_tradition: tradition,
          default_house_system: houseSystem,
          default_ayanamsa: ayanamsa,
          default_format: chartFormat,
        },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me-profile'] });
      queryClient.invalidateQueries({ queryKey: ['me-preferences'] });
      setSuccess('Chart defaults saved');
      setTimeout(() => setSuccess(''), 3000);
    },
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <SuccessBanner message={success} />

      <div>
        <label style={labelStyle}>Default Tradition</label>
        <select value={tradition} onChange={(e) => setTradition(e.target.value)} style={selectStyle} {...focusHandlers}>
          {TRADITIONS.map((t) => (<option key={t.value} value={t.value}>{t.label}</option>))}
        </select>
      </div>

      <div>
        <label style={labelStyle}>House System</label>
        <select value={houseSystem} onChange={(e) => setHouseSystem(e.target.value)} style={selectStyle} {...focusHandlers}>
          {HOUSE_SYSTEMS.map((h) => (<option key={h.value} value={h.value}>{h.label}</option>))}
        </select>
      </div>

      <div>
        <label style={labelStyle}>Ayanamsa</label>
        <select value={ayanamsa} onChange={(e) => setAyanamsa(e.target.value)} style={selectStyle} {...focusHandlers}>
          {AYANAMSAS.map((a) => (<option key={a.value} value={a.value}>{a.label}</option>))}
        </select>
      </div>

      <div>
        <label style={labelStyle}>Chart Format</label>
        <select value={chartFormat} onChange={(e) => setChartFormat(e.target.value)} style={selectStyle} {...focusHandlers}>
          {CHART_FORMATS.map((f) => (<option key={f.value} value={f.value}>{f.label}</option>))}
        </select>
      </div>

      {mutation.isError && (
        <div style={{ padding: '10px 14px', borderRadius: 8, fontSize: 13, color: '#E5484D', background: 'rgba(229,72,77,0.08)', border: '1px solid rgba(229,72,77,0.2)' }}>
          {(mutation.error as Error)?.message || 'Failed to save'}
        </div>
      )}

      <SaveButton onClick={() => mutation.mutate()} loading={mutation.isPending} />
    </div>
  );
}

/* ---------- Tab: Display ---------- */

function DisplayTab({ profile }: { profile: UserProfile }) {
  const queryClient = useQueryClient();
  const currentTheme = profile.preferences?.theme || 'dark';
  const [theme, setTheme] = useState(currentTheme);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    setTheme(profile.preferences?.theme || 'dark');
  }, [profile]);

  const themeMutation = useMutation({
    mutationFn: () => apiClient.put('/api/v1/me/preferences', { theme }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me-profile'] });
      queryClient.invalidateQueries({ queryKey: ['me-preferences'] });
      setSuccess('Display settings saved');
      setTimeout(() => setSuccess(''), 3000);
    },
  });

  const resetMutation = useMutation({
    mutationFn: () =>
      apiClient.put('/api/v1/me/preferences', {
        dashboard: { widget_layout: null, active_widgets: null },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me-profile'] });
      queryClient.invalidateQueries({ queryKey: ['me-preferences'] });
      queryClient.invalidateQueries({ queryKey: ['widget-layout'] });
      setSuccess('Widget layout reset to defaults');
      setTimeout(() => setSuccess(''), 3000);
    },
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <SuccessBanner message={success} />

      {/* Theme */}
      <div>
        <label style={labelStyle}>Theme</label>
        <div style={{ display: 'flex', gap: 12 }}>
          {(['dark', 'light'] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTheme(t)}
              style={{
                flex: 1,
                padding: '14px 20px',
                fontSize: 14,
                fontWeight: 500,
                color: theme === t ? 'var(--gold)' : 'var(--text-secondary)',
                background: theme === t ? 'rgba(245,166,35,0.08)' : 'var(--background)',
                border: `1px solid ${theme === t ? 'var(--gold)' : 'var(--border)'}`,
                borderRadius: 10,
                cursor: 'pointer',
                transition: 'all 0.15s',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: 20, marginBottom: 4 }}>{t === 'dark' ? '\u{1F319}' : '\u2600\uFE0F'}</div>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
        <SaveButton onClick={() => themeMutation.mutate()} loading={themeMutation.isPending} label="Save Theme" />
      </div>

      {/* Widget Reset */}
      <div style={{ borderTop: '1px solid var(--border)', paddingTop: 20 }}>
        <label style={labelStyle}>Dashboard Layout</label>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 0, marginBottom: 12 }}>
          Reset your dashboard widget layout to the default configuration.
        </p>
        <button
          onClick={() => resetMutation.mutate()}
          disabled={resetMutation.isPending}
          style={{
            padding: '10px 24px',
            fontSize: 14,
            fontWeight: 500,
            color: '#E5484D',
            background: 'rgba(229,72,77,0.08)',
            border: '1px solid rgba(229,72,77,0.2)',
            borderRadius: 10,
            cursor: resetMutation.isPending ? 'not-allowed' : 'pointer',
            transition: 'opacity 0.2s',
            opacity: resetMutation.isPending ? 0.6 : 1,
          }}
        >
          {resetMutation.isPending ? 'Resetting...' : 'Reset Widget Layout'}
        </button>
      </div>
    </div>
  );
}

/* ---------- Main Page ---------- */

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
