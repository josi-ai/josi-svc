export interface Person {
  person_id: string;
  name: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
  latitude: number;
  longitude: number;
  timezone: string;
  organization_id?: string;
  user_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreatePersonRequest {
  name: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
}
