'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { UserProfile } from './settings-types';
import { SaveButton, SuccessBanner } from './settings-shared';

export function NotificationsTab({ profile }: { profile: UserProfile }) {
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
        <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 8, fontSize: 13, color: 'var(--red)', background: 'var(--red-bg)', border: '1px solid var(--red-bg)' }}>
          {(mutation.error as Error)?.message || 'Failed to save'}
        </div>
      )}

      <SaveButton onClick={() => mutation.mutate()} loading={mutation.isPending} />
    </div>
  );
}
