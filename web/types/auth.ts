export interface User {
  id: string;
  descope_id: string;
  email: string;
  name: string;
  phone?: string;
  avatar_url?: string;
  subscription_tier: 'free' | 'explorer' | 'mystic' | 'master';
  roles: string[];
  created_at: string;
}
