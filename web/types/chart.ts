export interface PlanetPosition {
  planet: string;
  longitude: number;
  latitude: number;
  speed: number;
  sign: string;
  sign_index: number;
  degree_in_sign: number;
  nakshatra?: string;
  nakshatra_pada?: number;
  house: number;
  is_retrograde: boolean;
}

export interface HouseCusp {
  house: number;
  longitude: number;
  sign: string;
  degree_in_sign: number;
}

export interface Chart {
  chart_id: string;
  person_id: string;
  chart_type: string;
  calculation_system: string;
  ayanamsa: string;
  house_system: string;
  planet_positions: PlanetPosition[];
  house_cusps: HouseCusp[];
  ascendant: number;
  midheaven: number;
  created_at: string;
}

export interface CalculateChartRequest {
  name: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
  calculation_system?: string;
  ayanamsa?: string;
  house_system?: string;
}
