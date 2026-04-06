/**
 * Types and constants for the Transits page.
 */

/* ---------- Types ---------- */

export interface PlanetPosition {
  sign: string;
  degree: number;
  retrograde: boolean;
  speed?: number;
}

export interface MajorTransit {
  planet: string;
  current_sign: string;
  current_degree: number;
  natal_sign: string;
  natal_degree: number;
  aspect: string;
  orb: number;
  intensity: string;
  effects: string;
}

export interface ForecastEvent {
  date: string;
  planet: string;
  event_type: string;       // 'sign_change' | 'aspect' | 'retrograde' | 'direct'
  description: string;
  sign?: string;
  aspect_type?: string;
  target_planet?: string;
}

export interface ForecastData {
  person_id: string;
  events: ForecastEvent[];
  start_date: string;
  end_date: string;
}

export interface TransitData {
  person_id: string;
  current_date: string;
  major_transits: MajorTransit[];
  current_planetary_positions: Record<string, PlanetPosition>;
}
