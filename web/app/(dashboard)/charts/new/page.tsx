'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import PlaceAutocomplete from '@/components/ui/place-autocomplete';

/* ---------- Types ---------- */

interface Person {
  person_id: string;
  name: string;
  date_of_birth: string;
  time_of_birth: string | null;
  place_of_birth: string | null;
  is_default?: boolean;
}

/* ---------- Constants ---------- */

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

const NEW_PROFILE_VALUE = '__new__';

/* ---------- Helpers ---------- */

function extractTimeValue(timeStr: string | null): string {
  if (!timeStr) return '';
  if (timeStr.includes('T')) {
    const d = new Date(timeStr);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  }
  return timeStr.substring(0, 5);
}

export default function NewChartPage() {
  const router = useRouter();
  const { user } = useAuth();

  // Fetch all profiles
  const { data: personsResponse, isLoading: personsLoading } = useQuery({
    queryKey: ['persons'],
    queryFn: () => apiClient.get<Person[]>('/api/v1/persons/'),
  });

  const persons = personsResponse?.data || [];

  // Find default profile
  const defaultProfile = persons.find((p) => p.is_default === true) || persons[0] || null;

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

  // Initialize selected profile when persons load
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

  /** Format time for API: "HH:MM" → "YYYY-MM-DD HH:MM:SS" using the DOB date */
  function formatTimeForApi(time: string, dob: string): string | null {
    if (!time) return null;
    const t = time.length === 5 ? `${time}:00` : time; // "12:12" → "12:12:00"
    const date = dob || '2000-01-01'; // fallback date if no DOB
    return `${date} ${t}`;
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
    if (person) {
      prefillFromProfile(person);
    }
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
        // Profile has birth data — use it directly
        personId = selectedProfileId;
      } else if (isExistingProfile && !isProfileComplete) {
        // Incomplete profile — update it with the form data, then use it
        await apiClient.put(`/api/v1/persons/${selectedProfileId}`, {
          name: name || selectedPerson?.name,
          date_of_birth: dateOfBirth,
          time_of_birth: formatTimeForApi(timeOfBirth, dateOfBirth),
          place_of_birth: placeOfBirth || null,
        });
        personId = selectedProfileId;
      } else {
        // Step 1: Create person
        const personRes = await apiClient.post<{ person_id: string }>('/api/v1/persons/', {
          name: name || 'Unnamed',
          date_of_birth: dateOfBirth,
          time_of_birth: formatTimeForApi(timeOfBirth, dateOfBirth),
          place_of_birth: placeOfBirth || null,
        });
        personId = personRes.data.person_id;
      }

      // Step 2: Calculate chart
      const params = new URLSearchParams({
        person_id: personId,
        systems: tradition,
        house_system: houseSystem,
      });
      if (tradition === 'vedic') {
        params.set('ayanamsa', ayanamsa);
      }

      const chartRes = await apiClient.post<any>(
        `/api/v1/charts/calculate?${params.toString()}`
      );

      // The API returns { success, message, data: [...charts] }
      // apiClient unwraps to ApiResponse<T>, so chartRes.data is the array
      const raw = chartRes.data;
      const charts = Array.isArray(raw) ? raw : [raw];
      const chartId = charts[0]?.chart_id || charts[0]?.id || charts[0]?.chartId;

      if (!chartId) {
        setError(`Chart was calculated but no chart ID was returned. Response keys: ${Object.keys(charts[0] || {}).join(', ')}`);
        setIsSubmitting(false);
        return;
      }

      // Step 3: Redirect to chart detail
      router.push(`/charts/${chartId}`);
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.');
      setIsSubmitting(false);
    }
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
  };

  const selectStyle: React.CSSProperties = {
    ...inputStyle,
    appearance: 'none',
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235B6A8A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 12px center',
    paddingRight: 36,
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: '32px 16px' }}>
      {/* Header */}
      <Link
        href="/charts"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 4,
          fontSize: 13,
          color: 'var(--gold)',
          textDecoration: 'none',
          marginBottom: 16,
        }}
      >
        &larr; Charts
      </Link>

      <h1
        className="font-display"
        style={{
          fontSize: 28,
          color: 'var(--text-primary)',
          marginBottom: 24,
          fontWeight: 400,
        }}
      >
        Calculate New Chart
      </h1>

      {/* Form Card */}
      <form onSubmit={handleSubmit}>
        <div
          style={{
            background: 'var(--card)',
            border: '1px solid var(--border)',
            borderRadius: 14,
            padding: 28,
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Profile Selector */}
            <div>
              <label style={labelStyle}>Calculate For</label>
              <select
                value={selectedProfileId}
                onChange={(e) => handleProfileChange(e.target.value)}
                style={selectStyle}
                onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
                disabled={personsLoading}
              >
                {personsLoading && (
                  <option value="">Loading profiles...</option>
                )}
                {!personsLoading && persons.length === 0 && (
                  <option value="">No profiles found</option>
                )}
                {persons.map((p) => (
                  <option key={p.person_id} value={p.person_id}>
                    {p.is_default ? `\u2605 ${p.name}` : p.name}
                  </option>
                ))}
                <option value={NEW_PROFILE_VALUE}>+ New Profile</option>
              </select>
            </div>

            {/* Divider */}
            <div style={{ borderTop: '1px solid var(--border)', margin: '0 -28px', padding: '0 28px' }} />

            {isExistingProfile && isProfileComplete ? (
              /* ---- Complete profile: show summary card ---- */
              <div
                style={{
                  background: 'var(--surface, var(--card))',
                  border: '1px solid var(--border)',
                  borderRadius: 10,
                  padding: '16px 20px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{name}</span>
                  <span
                    style={{
                      fontSize: 10,
                      color: 'var(--gold)',
                      cursor: 'pointer',
                      textDecoration: 'underline',
                      textUnderlineOffset: 2,
                    }}
                    onClick={() => {
                      setSelectedProfileId(NEW_PROFILE_VALUE);
                      clearForm();
                    }}
                  >
                    Use different details instead
                  </span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 20px', fontSize: 13, color: 'var(--text-secondary)' }}>
                  {dateOfBirth && (
                    <span>Born {new Date(dateOfBirth + 'T00:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
                  )}
                  {timeOfBirth && <span>at {timeOfBirth}</span>}
                  {placeOfBirth && <span>in {placeOfBirth}</span>}
                </div>
                {!dateOfBirth && (
                  <p style={{ fontSize: 12, color: 'var(--text-faint)', fontStyle: 'italic' }}>
                    Birth details incomplete — <span
                      style={{ color: 'var(--gold)', cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: 2 }}
                      onClick={() => router.push('/persons')}
                    >edit profile</span> to add them, or select &quot;+ New Profile&quot; above.
                  </p>
                )}
              </div>
            ) : (
              /* ---- New or incomplete profile: show full form ---- */
              <>
                {isExistingProfile && !isProfileComplete && (
                  <p style={{ fontSize: 12, color: 'var(--gold)', marginBottom: -8 }}>
                    Complete your birth details to calculate a chart
                  </p>
                )}

                {/* Name */}
                <div>
                  <label style={labelStyle}>Name</label>
                  <input
                    type="text"
                    placeholder="Enter name (e.g., John Doe)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                    onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
                  />
                </div>

                {/* Date of Birth */}
                <div>
                  <label style={labelStyle}>Date of Birth</label>
                  <input
                    type="date"
                    required
                    value={dateOfBirth}
                    onChange={(e) => setDateOfBirth(e.target.value)}
                    style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                    onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
                  />
                </div>

                {/* Time of Birth */}
                <div>
                  <label style={labelStyle}>Time of Birth</label>
                  <input
                    type="time"
                    value={timeOfBirth}
                    onChange={(e) => setTimeOfBirth(e.target.value)}
                    style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                    onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
                  />
                  <p style={{ fontSize: 12, color: 'var(--text-faint)', marginTop: 6, lineHeight: 1.4 }}>
                    Birth time affects house positions. If unknown, we&rsquo;ll use sunrise.
                  </p>
                </div>

                {/* Place of Birth */}
                <div>
                  <label style={labelStyle}>Place of Birth</label>
                  <PlaceAutocomplete
                    value={placeOfBirth}
                    onChange={setPlaceOfBirth}
                    placeholder="City, Country"
                    className=""
                    style={inputStyle}
                  />
                </div>
              </>
            )}

            {/* Tradition */}
            <div>
              <label style={labelStyle}>Tradition</label>
              <select
                value={tradition}
                onChange={(e) => setTradition(e.target.value)}
                style={selectStyle}
                onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              >
                {TRADITIONS.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            {/* House System */}
            <div>
              <label style={labelStyle}>House System</label>
              <select
                value={houseSystem}
                onChange={(e) => setHouseSystem(e.target.value)}
                style={selectStyle}
                onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              >
                {HOUSE_SYSTEMS.map((h) => (
                  <option key={h.value} value={h.value}>
                    {h.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Ayanamsa — only for Vedic */}
            {tradition === 'vedic' && (
              <div>
                <label style={labelStyle}>Ayanamsa</label>
                <select
                  value={ayanamsa}
                  onChange={(e) => setAyanamsa(e.target.value)}
                  style={selectStyle}
                  onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                  onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
                >
                  {AYANAMSAS.map((a) => (
                    <option key={a.value} value={a.value}>
                      {a.label}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div
              style={{
                marginTop: 20,
                padding: '10px 14px',
                borderRadius: 8,
                fontSize: 13,
                color: '#E5484D',
                background: 'rgba(229,72,77,0.08)',
                border: '1px solid rgba(229,72,77,0.2)',
              }}
            >
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              marginTop: 24,
              padding: '12px 24px',
              fontSize: 15,
              fontWeight: 600,
              color: '#060A14',
              background: isSubmitting ? 'var(--gold-bright)' : 'var(--gold)',
              border: 'none',
              borderRadius: 10,
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.7 : 1,
              transition: 'opacity 0.2s, background 0.2s',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
          >
            {isSubmitting ? (
              <>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  style={{ animation: 'spin 1s linear infinite' }}
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeDasharray="31.42 31.42"
                  />
                </svg>
                Calculating...
              </>
            ) : (
              'Calculate Chart \u2192'
            )}
          </button>
        </div>
      </form>

      {/* Spinner keyframes */}
      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}
