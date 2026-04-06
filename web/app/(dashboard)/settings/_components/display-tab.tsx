'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { UserProfile } from './settings-types';
import { labelStyle, SaveButton, SuccessBanner } from './settings-shared';

export function DisplayTab({ profile }: { profile: UserProfile }) {
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
            color: 'var(--red)',
            background: 'var(--red-bg)',
            border: '1px solid var(--red-bg)',
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
