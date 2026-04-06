'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

import type { Person } from './_components/new-chart-types';
import { TRADITIONS, HOUSE_SYSTEMS, AYANAMSAS, NEW_PROFILE_VALUE } from './_components/new-chart-types';
import { extractTimeValue, formatTimeForApi, labelStyle, selectStyle, focusHandlers } from './_components/new-chart-helpers';
import { BirthDetailsForm } from './_components/birth-details-form';

export default function NewChartPage() {
  const router = useRouter();
  const { user } = useAuth();

  const { data: personsResponse, isLoading: personsLoading } = useQuery({
    queryKey: ['persons'],
    queryFn: () => apiClient.get<Person[]>('/api/v1/persons/'),
  });

  const persons = personsResponse?.data || [];

  const [selectedProfileId, setSelectedProfileId] = useState<string>('');
  const [name, setName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [timeOfBirth, setTimeOfBirth] = useState('');
  const [placeOfBirth, setPlaceOfBirth] = useState('');
  const [tradition, setTradition] = useState('vedic');
  const [houseSystem, setHouseSystem] = useState('whole_sign');
  const [ayanamsa, setAyanamsa] = useState('lahiri');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (persons.length > 0 && !selectedProfileId) {
      const def = persons.find((p) => p.is_default === true) || persons[0];
      if (def) {
        setSelectedProfileId(def.person_id);
        prefillFromProfile(def);
      }
    }
  }, [persons]); // eslint-disable-line react-hooks/exhaustive-deps

  const isExistingProfile = selectedProfileId && selectedProfileId !== NEW_PROFILE_VALUE;
  const selectedPerson = isExistingProfile ? persons.find((p) => p.person_id === selectedProfileId) : null;
  const isProfileComplete = !!(selectedPerson?.date_of_birth);

  function prefillFromProfile(person: Person) {
    setName(person.name);
    setDateOfBirth(person.date_of_birth || '');
    setTimeOfBirth(extractTimeValue(person.time_of_birth));
    setPlaceOfBirth(person.place_of_birth || '');
  }

  function clearForm() {
    setName('');
    setDateOfBirth('');
    setTimeOfBirth('');
    setPlaceOfBirth('');
  }

  const handleProfileChange = (value: string) => {
    setSelectedProfileId(value);
    setError('');
    if (value === NEW_PROFILE_VALUE) {
      clearForm();
      return;
    }
    const person = persons.find((p) => p.person_id === value);
    if (person) prefillFromProfile(person);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!isProfileComplete && !dateOfBirth) {
      setError('Date of birth is required.');
      return;
    }

    setIsSubmitting(true);

    try {
      let personId: string;

      if (isExistingProfile && isProfileComplete) {
        personId = selectedProfileId;
      } else if (isExistingProfile && !isProfileComplete) {
        await apiClient.put(`/api/v1/persons/${selectedProfileId}`, {
          name: name || selectedPerson?.name,
          date_of_birth: dateOfBirth,
          time_of_birth: formatTimeForApi(timeOfBirth, dateOfBirth),
          place_of_birth: placeOfBirth || null,
        });
        personId = selectedProfileId;
      } else {
        const personRes = await apiClient.post<{ person_id: string }>('/api/v1/persons/', {
          name: name || 'Unnamed',
          date_of_birth: dateOfBirth,
          time_of_birth: formatTimeForApi(timeOfBirth, dateOfBirth),
          place_of_birth: placeOfBirth || null,
        });
        personId = personRes.data!.person_id;
      }

      const params = new URLSearchParams({
        person_id: personId,
        systems: tradition,
        house_system: houseSystem,
      });
      if (tradition === 'vedic') params.set('ayanamsa', ayanamsa);

      const chartRes = await apiClient.post<any>(`/api/v1/charts/calculate?${params.toString()}`);
      const raw = chartRes.data;
      const charts = Array.isArray(raw) ? raw : [raw];
      const chartId = charts[0]?.chart_id || charts[0]?.id || charts[0]?.chartId;

      if (!chartId) {
        setError(`Chart was calculated but no chart ID was returned. Response keys: ${Object.keys(charts[0] || {}).join(', ')}`);
        setIsSubmitting(false);
        return;
      }

      router.push(`/charts/${chartId}`);
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: '32px 16px' }}>
      <Link
        href="/charts"
        style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 13, color: 'var(--gold)', textDecoration: 'none', marginBottom: 16 }}
      >
        &larr; Charts
      </Link>

      <h1 className="font-display" style={{ fontSize: 28, color: 'var(--text-primary)', marginBottom: 24, fontWeight: 400 }}>
        Calculate New Chart
      </h1>

      <form onSubmit={handleSubmit}>
        <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14, padding: 28 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Profile Selector */}
            <div>
              <label style={labelStyle}>Calculate For</label>
              <select
                value={selectedProfileId}
                onChange={(e) => handleProfileChange(e.target.value)}
                style={selectStyle}
                {...focusHandlers}
                disabled={personsLoading}
              >
                {personsLoading && <option value="">Loading profiles...</option>}
                {!personsLoading && persons.length === 0 && <option value="">No profiles found</option>}
                {persons.map((p) => (
                  <option key={p.person_id} value={p.person_id}>
                    {p.is_default ? `\u2605 ${p.name}` : p.name}
                  </option>
                ))}
                <option value={NEW_PROFILE_VALUE}>+ New Profile</option>
              </select>
            </div>

            <div style={{ borderTop: '1px solid var(--border)', margin: '0 -28px', padding: '0 28px' }} />

            {/* Birth details or summary */}
            <BirthDetailsForm
              name={name}
              setName={setName}
              dateOfBirth={dateOfBirth}
              setDateOfBirth={setDateOfBirth}
              timeOfBirth={timeOfBirth}
              setTimeOfBirth={setTimeOfBirth}
              placeOfBirth={placeOfBirth}
              setPlaceOfBirth={setPlaceOfBirth}
              isExistingProfile={isExistingProfile}
              isProfileComplete={isProfileComplete}
            />

            {/* Tradition */}
            <div>
              <label style={labelStyle}>Tradition</label>
              <select value={tradition} onChange={(e) => setTradition(e.target.value)} style={selectStyle} {...focusHandlers}>
                {TRADITIONS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>

            {/* House System */}
            <div>
              <label style={labelStyle}>House System</label>
              <select value={houseSystem} onChange={(e) => setHouseSystem(e.target.value)} style={selectStyle} {...focusHandlers}>
                {HOUSE_SYSTEMS.map((h) => <option key={h.value} value={h.value}>{h.label}</option>)}
              </select>
            </div>

            {/* Ayanamsa */}
            {tradition === 'vedic' && (
              <div>
                <label style={labelStyle}>Ayanamsa</label>
                <select value={ayanamsa} onChange={(e) => setAyanamsa(e.target.value)} style={selectStyle} {...focusHandlers}>
                  {AYANAMSAS.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
                </select>
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div style={{ marginTop: 20, padding: '10px 14px', borderRadius: 8, fontSize: 13, color: 'var(--red)', background: 'rgba(229,72,77,0.08)', border: '1px solid rgba(229,72,77,0.2)' }}>
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%', marginTop: 24, padding: '12px 24px', fontSize: 15, fontWeight: 600,
              color: 'var(--primary-foreground)', background: isSubmitting ? 'var(--gold-bright)' : 'var(--gold)',
              border: 'none', borderRadius: 10, cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.7 : 1, transition: 'opacity 0.2s, background 0.2s',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}
          >
            {isSubmitting ? (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: 'spin 1s linear infinite' }}>
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeDasharray="31.42 31.42" />
                </svg>
                Calculating...
              </>
            ) : (
              'Calculate Chart \u2192'
            )}
          </button>
        </div>
      </form>

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
