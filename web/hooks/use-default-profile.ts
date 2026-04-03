'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface Person {
  person_id: string;
  name: string;
  date_of_birth: string | null;
  time_of_birth: string | null;
  place_of_birth: string | null;
  latitude: string | number | null;
  longitude: string | number | null;
  timezone: string | null;
  is_default?: boolean;
}

export interface ProfileLocation {
  latitude: number;
  longitude: number;
  timezone: string;
}

/** Default fallback: Chennai, India */
const DEFAULT_LOCATION: ProfileLocation = {
  latitude: 13.0827,
  longitude: 80.2707,
  timezone: 'Asia/Kolkata',
};

/**
 * Fetches the user's persons list and returns the default profile.
 * Reuses the same ['persons'] query key as ProfileSelector for cache sharing.
 *
 * Also exposes a resolved `location` (lat/lng/tz) that falls back to Chennai
 * when the profile has no coordinates.
 */
export function useDefaultProfile() {
  const { data: personsResponse, isLoading } = useQuery({
    queryKey: ['persons'],
    queryFn: () => apiClient.get<Person[]>('/api/v1/persons/'),
  });

  const persons = personsResponse?.data || [];
  const defaultProfile = persons.find((p) => p.is_default === true) || persons[0] || null;

  // Resolve location from default profile or fall back
  const location: ProfileLocation = (() => {
    if (defaultProfile) {
      const lat = Number(defaultProfile.latitude);
      const lng = Number(defaultProfile.longitude);
      if (lat && lng && defaultProfile.timezone) {
        return { latitude: lat, longitude: lng, timezone: defaultProfile.timezone };
      }
    }
    return DEFAULT_LOCATION;
  })();

  return { defaultProfile, persons, location, isLoading };
}
