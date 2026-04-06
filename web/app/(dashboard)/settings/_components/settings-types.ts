/**
 * Types and constants for the Settings page.
 */

export interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  phone: string | null;
  avatar_url: string | null;
  ethnicity: string[] | null;
  language_preference?: string | null;
  subscription_tier_id: number | null;
  subscription_tier_name: string | null;
  subscription_end_date: string | null;
  roles: string[];
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  preferences: Record<string, any>;
  notification_settings: Record<string, any>;
}

export interface SubscriptionInfo {
  subscription_tier_id: number;
  subscription_tier_name: string;
  subscription_end_date: string | null;
  is_active: boolean;
  has_premium: boolean;
  limits: Record<string, number>;
}

export interface UsageInfo {
  charts_calculated?: number;
  ai_interpretations?: number;
  consultations?: number;
  [key: string]: any;
}

export const TABS = ['Account', 'Subscription', 'Notifications', 'Chart Defaults', 'Display'] as const;
export type Tab = (typeof TABS)[number];

export const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'ta', label: 'Tamil' },
  { value: 'te', label: 'Telugu' },
  { value: 'kn', label: 'Kannada' },
  { value: 'hi', label: 'Hindi' },
  { value: 'ml', label: 'Malayalam' },
  { value: 'bn', label: 'Bengali' },
  { value: 'sa', label: 'Sanskrit' },
];

export const ETHNICITY_OPTIONS = [
  'Tamil Hindu', 'North Indian Hindu', 'Bengali Hindu', 'South Indian Christian',
  'Keralite Hindu', 'Maharashtrian Hindu', 'Gujarati Hindu', 'Punjabi Hindu',
  'Muslim', 'Buddhist', 'Sikh', 'Jain', 'Christian', 'Other',
];

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
export const CHART_FORMATS = [
  { value: 'South Indian', label: 'South Indian' },
  { value: 'North Indian', label: 'North Indian' },
  { value: 'Western Wheel', label: 'Western Wheel' },
];
