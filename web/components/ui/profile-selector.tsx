'use client';

import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

/* ---------- Types ---------- */

interface Person {
  person_id: string;
  name: string;
  date_of_birth: string | null;
  time_of_birth: string | null;
  place_of_birth: string | null;
  is_default?: boolean;
}

export interface ProfileSelectorProps {
  value?: string;
  onChange: (personId: string) => void;
  showDefault?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

/* ---------- Styles ---------- */

const selectStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  fontSize: 14,
  color: 'var(--text-primary)',
  background: 'var(--background)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  outline: 'none',
  transition: 'border-color 0.2s',
  appearance: 'none',
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235B6A8A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 12px center',
  paddingRight: 36,
};

/* ---------- Component ---------- */

export function ProfileSelector({
  value,
  onChange,
  showDefault = true,
  className = '',
  style,
}: ProfileSelectorProps) {
  const {
    data: personsResponse,
    isLoading,
  } = useQuery({
    queryKey: ['persons'],
    queryFn: () => apiClient.get<Person[]>('/api/v1/persons/'),
  });

  const persons = personsResponse?.data || [];

  // Auto-select default profile on mount when no value is provided
  useEffect(() => {
    if (persons.length > 0 && !value) {
      const defaultPerson = persons.find((p) => p.is_default === true) || persons[0];
      if (defaultPerson) {
        onChange(defaultPerson.person_id);
      }
    }
  }, [persons]); // eslint-disable-line react-hooks/exhaustive-deps

  const mergedStyle: React.CSSProperties = { ...selectStyle, ...style };

  return (
    <select
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className={className}
      style={mergedStyle}
      onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
      onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
      disabled={isLoading}
    >
      {isLoading && (
        <option value="">Loading profiles...</option>
      )}
      {!isLoading && persons.length === 0 && (
        <option value="">No profiles found</option>
      )}
      {persons.map((p) => (
        <option key={p.person_id} value={p.person_id}>
          {showDefault && p.is_default ? `\u2605 ${p.name}` : p.name}
        </option>
      ))}
    </select>
  );
}
