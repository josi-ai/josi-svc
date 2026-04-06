'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { UserProfile } from './settings-types';
import { TRADITIONS, HOUSE_SYSTEMS, AYANAMSAS, CHART_FORMATS } from './settings-types';
import { labelStyle, selectStyle, focusHandlers, SaveButton, SuccessBanner } from './settings-shared';

export function ChartDefaultsTab({ profile }: { profile: UserProfile }) {
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
        <div style={{ padding: '10px 14px', borderRadius: 8, fontSize: 13, color: 'var(--red)', background: 'var(--red-bg)', border: '1px solid var(--red-bg)' }}>
          {(mutation.error as Error)?.message || 'Failed to save'}
        </div>
      )}

      <SaveButton onClick={() => mutation.mutate()} loading={mutation.isPending} />
    </div>
  );
}
