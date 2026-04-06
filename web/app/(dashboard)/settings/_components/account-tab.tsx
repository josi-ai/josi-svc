'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { UserProfile } from './settings-types';
import { ETHNICITY_OPTIONS, LANGUAGE_OPTIONS } from './settings-types';
import { labelStyle, inputStyle, selectStyle, focusHandlers, SaveButton, SuccessBanner } from './settings-shared';

const SUPPORTED_LANGS = ['ta', 'te', 'kn', 'hi', 'ml', 'bn', 'sa'];

function detectBrowserLang(): string {
  if (typeof navigator === 'undefined') return 'en';
  const bl = navigator.language?.split('-')[0];
  return SUPPORTED_LANGS.includes(bl) ? bl : 'en';
}

export function AccountTab({ profile }: { profile: UserProfile }) {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState(profile.full_name || '');
  const [phone, setPhone] = useState(profile.phone || '');
  const [ethnicity, setEthnicity] = useState<string[]>(profile.ethnicity || []);
  const [languagePreference, setLanguagePreference] = useState(profile.language_preference || detectBrowserLang());
  const [success, setSuccess] = useState('');

  useEffect(() => {
    setFullName(profile.full_name || '');
    setPhone(profile.phone || '');
    setEthnicity(profile.ethnicity || []);
    setLanguagePreference(profile.language_preference || detectBrowserLang());
  }, [profile]);

  const mutation = useMutation({
    mutationFn: () =>
      apiClient.put('/api/v1/me', {
        full_name: fullName,
        phone: phone || null,
        ethnicity: ethnicity.length > 0 ? ethnicity : null,
        language_preference: languagePreference || null,
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

      <div>
        <label style={labelStyle}>Language</label>
        <select
          value={languagePreference}
          onChange={(e) => setLanguagePreference(e.target.value)}
          style={selectStyle}
          {...focusHandlers}
        >
          {LANGUAGE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 4 }}>
          Astrological terms will show native-script translations alongside English
        </p>
      </div>

      {mutation.isError && (
        <div style={{ padding: '10px 14px', borderRadius: 8, fontSize: 13, color: 'var(--red)', background: 'var(--red-bg)', border: '1px solid var(--red-bg)' }}>
          {(mutation.error as Error)?.message || 'Failed to update'}
        </div>
      )}

      <SaveButton onClick={() => mutation.mutate()} loading={mutation.isPending} />
    </div>
  );
}
