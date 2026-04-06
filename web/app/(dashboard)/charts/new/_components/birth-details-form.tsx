'use client';

import { useRouter } from 'next/navigation';
import PlaceAutocomplete from '@/components/ui/place-autocomplete';
import { labelStyle, inputStyle, focusHandlers } from './new-chart-helpers';

export function BirthDetailsForm({
  name,
  setName,
  dateOfBirth,
  setDateOfBirth,
  timeOfBirth,
  setTimeOfBirth,
  placeOfBirth,
  setPlaceOfBirth,
  isExistingProfile,
  isProfileComplete,
}: {
  name: string;
  setName: (v: string) => void;
  dateOfBirth: string;
  setDateOfBirth: (v: string) => void;
  timeOfBirth: string;
  setTimeOfBirth: (v: string) => void;
  placeOfBirth: string;
  setPlaceOfBirth: (v: string) => void;
  isExistingProfile: boolean | string;
  isProfileComplete: boolean;
}) {
  const router = useRouter();

  if (isExistingProfile && isProfileComplete) {
    return (
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
              // Signal parent to switch to new profile mode
              setName('');
              setDateOfBirth('');
              setTimeOfBirth('');
              setPlaceOfBirth('');
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
    );
  }

  return (
    <>
      {isExistingProfile && !isProfileComplete && (
        <p style={{ fontSize: 12, color: 'var(--gold)', marginBottom: -8 }}>
          Complete your birth details to calculate a chart
        </p>
      )}

      <div>
        <label style={labelStyle}>Name</label>
        <input
          type="text"
          placeholder="Enter name (e.g., John Doe)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={inputStyle}
          {...focusHandlers}
        />
      </div>

      <div>
        <label style={labelStyle}>Date of Birth</label>
        <input
          type="date"
          required
          value={dateOfBirth}
          onChange={(e) => setDateOfBirth(e.target.value)}
          style={inputStyle}
          {...focusHandlers}
        />
      </div>

      <div>
        <label style={labelStyle}>Time of Birth</label>
        <input
          type="time"
          value={timeOfBirth}
          onChange={(e) => setTimeOfBirth(e.target.value)}
          style={inputStyle}
          {...focusHandlers}
        />
        <p style={{ fontSize: 12, color: 'var(--text-faint)', marginTop: 6, lineHeight: 1.4 }}>
          Birth time affects house positions. If unknown, we&rsquo;ll use sunrise.
        </p>
      </div>

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
  );
}
