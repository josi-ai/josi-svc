/**
 * Types and constants for the New Chart page.
 */

export interface Person {
  person_id: string;
  name: string;
  date_of_birth: string;
  time_of_birth: string | null;
  place_of_birth: string | null;
  is_default?: boolean;
}

export const TRADITIONS = [
  { value: 'vedic', label: 'Vedic' },
  { value: 'western', label: 'Western' },
  { value: 'chinese', label: 'Chinese' },
];

export const HOUSE_SYSTEMS = [
  { value: 'whole_sign', label: 'Whole Sign' },
  { value: 'placidus', label: 'Placidus' },
  { value: 'koch', label: 'Koch' },
  { value: 'equal', label: 'Equal' },
];

export const AYANAMSAS = [
  { value: 'lahiri', label: 'Lahiri' },
  { value: 'raman', label: 'Raman' },
  { value: 'kp', label: 'KP' },
];

export const NEW_PROFILE_VALUE = '__new__';
