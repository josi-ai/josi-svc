'use client';

import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import PlaceAutocomplete from '@/components/ui/place-autocomplete';

/* ---------- Types ---------- */

export interface LocationValue {
  latitude: number;
  longitude: number;
  timezone: string;
  displayName: string;
}

interface Person {
  person_id: string;
  name: string;
  latitude: string | number | null;
  longitude: string | number | null;
  timezone: string | null;
  place_of_birth: string | null;
  is_default?: boolean;
}

export interface LocationPickerProps {
  value?: LocationValue;
  onChange: (location: LocationValue) => void;
  className?: string;
  style?: React.CSSProperties;
}

/* ---------- Styles ---------- */

const buttonStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '8px 14px',
  fontSize: 13,
  fontWeight: 500,
  color: 'var(--text-secondary)',
  background: 'var(--background)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  cursor: 'pointer',
  transition: 'border-color 0.2s, color 0.2s',
  whiteSpace: 'nowrap',
  flexShrink: 0,
};

const activeButtonStyle: React.CSSProperties = {
  ...buttonStyle,
  borderColor: 'var(--gold)',
  color: 'var(--text-primary)',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 14px',
  fontSize: 13,
  color: 'var(--text-primary)',
  background: 'var(--background)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  outline: 'none',
  transition: 'border-color 0.2s',
  minWidth: 0,
};

/* ---------- Helpers ---------- */

/** Guess timezone from coordinates using the Intl API as a fallback */
function guessLocalTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch {
    return 'UTC';
  }
}

/* ---------- Component ---------- */

export function LocationPicker({
  value,
  onChange,
  className = '',
  style,
}: LocationPickerProps) {
  const [searchText, setSearchText] = useState('');
  const [geoLoading, setGeoLoading] = useState(false);
  const [geoError, setGeoError] = useState('');
  const [activeMode, setActiveMode] = useState<'geo' | 'birth' | 'search' | null>(null);

  // Fetch default profile for birth location
  const { data: defaultProfileResponse } = useQuery({
    queryKey: ['default-profile'],
    queryFn: () => apiClient.get<Person>('/api/v1/persons/me'),
  });
  const defaultProfile = defaultProfileResponse?.data || null;

  // Default to birth location on mount if available and no value provided
  useEffect(() => {
    if (!value && defaultProfile) {
      const lat = Number(defaultProfile.latitude);
      const lng = Number(defaultProfile.longitude);
      if (lat && lng && defaultProfile.timezone) {
        onChange({
          latitude: lat,
          longitude: lng,
          timezone: defaultProfile.timezone,
          displayName: defaultProfile.place_of_birth || 'Birth location',
        });
        setActiveMode('birth');
      }
    }
  }, [defaultProfile]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleUseMyLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setGeoError('Geolocation not supported');
      return;
    }

    setGeoLoading(true);
    setGeoError('');
    setActiveMode('geo');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const timezone = guessLocalTimezone();
        onChange({
          latitude,
          longitude,
          timezone,
          displayName: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`,
        });
        setGeoLoading(false);
      },
      (err) => {
        setGeoError(err.message || 'Could not get location');
        setGeoLoading(false);
        setActiveMode(null);
      },
      { enableHighAccuracy: false, timeout: 10000 },
    );
  }, [onChange]);

  const handleUseBirthLocation = useCallback(() => {
    if (!defaultProfile) return;
    const lat = Number(defaultProfile.latitude);
    const lng = Number(defaultProfile.longitude);
    if (!lat || !lng) return;

    setActiveMode('birth');
    onChange({
      latitude: lat,
      longitude: lng,
      timezone: defaultProfile.timezone || guessLocalTimezone(),
      displayName: defaultProfile.place_of_birth || 'Birth location',
    });
  }, [defaultProfile, onChange]);

  const handlePlaceSelect = useCallback(
    (place: { name: string; lat: number; lng: number }) => {
      setActiveMode('search');
      // Use browser timezone as a reasonable default for the selected city
      onChange({
        latitude: place.lat,
        longitude: place.lng,
        timezone: guessLocalTimezone(),
        displayName: place.name,
      });
    },
    [onChange],
  );

  const birthLocationAvailable =
    defaultProfile &&
    Number(defaultProfile.latitude) !== 0 &&
    Number(defaultProfile.longitude) !== 0 &&
    defaultProfile.timezone;

  return (
    <div className={className} style={style}>
      {/* Button row + search input */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          flexWrap: 'wrap',
        }}
      >
        {/* My Location button */}
        <button
          type="button"
          onClick={handleUseMyLocation}
          disabled={geoLoading}
          style={activeMode === 'geo' ? activeButtonStyle : buttonStyle}
          onMouseEnter={(e) => {
            if (activeMode !== 'geo') e.currentTarget.style.borderColor = 'var(--gold)';
          }}
          onMouseLeave={(e) => {
            if (activeMode !== 'geo') e.currentTarget.style.borderColor = 'var(--border)';
          }}
        >
          {geoLoading ? (
            <>
              <svg
                width="14"
                height="14"
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
              Locating...
            </>
          ) : (
            <>{'\uD83D\uDCCD'} My Location</>
          )}
        </button>

        {/* Birth Location button */}
        {birthLocationAvailable && (
          <button
            type="button"
            onClick={handleUseBirthLocation}
            style={activeMode === 'birth' ? activeButtonStyle : buttonStyle}
            onMouseEnter={(e) => {
              if (activeMode !== 'birth') e.currentTarget.style.borderColor = 'var(--gold)';
            }}
            onMouseLeave={(e) => {
              if (activeMode !== 'birth') e.currentTarget.style.borderColor = 'var(--border)';
            }}
          >
            {'\uD83C\uDFE0'} Birth Location
          </button>
        )}

        {/* Search input */}
        <div style={{ flex: 1, minWidth: 160 }}>
          <PlaceAutocomplete
            value={searchText}
            onChange={setSearchText}
            onSelect={handlePlaceSelect}
            placeholder="Search city..."
            style={inputStyle}
          />
        </div>
      </div>

      {/* Error message */}
      {geoError && (
        <p
          style={{
            fontSize: 12,
            color: '#E5484D',
            marginTop: 6,
            marginBottom: 0,
          }}
        >
          {geoError}
        </p>
      )}

      {/* Current selection display */}
      {value && (
        <p
          style={{
            fontSize: 12,
            color: 'var(--text-muted)',
            marginTop: 8,
            marginBottom: 0,
          }}
        >
          Selected: <span style={{ color: 'var(--text-secondary)' }}>{value.displayName}</span>
          <span style={{ color: 'var(--text-faint)', marginLeft: 8 }}>
            ({value.latitude.toFixed(4)}, {value.longitude.toFixed(4)} &middot; {value.timezone})
          </span>
        </p>
      )}

      {/* Spinner keyframes */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
