/**
 * Types specific to the chart detail page.
 *
 * These represent the shape returned by `GET /api/v1/charts/:id` which differs
 * from the DB-model types in `api.ts` (e.g. `sign_degree` vs `degree_in_sign`).
 */

export interface ChartDetailPlanetData {
  longitude: number;
  sign: string;
  sign_degree: number;
  house: number;
  nakshatra?: string;
  nakshatra_pada?: number;
  pada?: number;
  is_retrograde: boolean;
  speed?: number;
  dignity?: string;
  navamsa_sign?: string;
}

export interface ChartDetailHouseData {
  sign: string;
  degree: number;
}

export interface ChartDetailPanchangItem {
  number?: number;
  name?: string;
  percent?: number;
  end_time?: string;
  paksha?: string;
  deity?: string;
  pada?: number;
  ruler?: string;
  quality?: string;
}

export interface ChartDetailDashaPeriod {
  planet: string;
  start_date: string;
  end_date: string;
  duration_years?: number;
  progress_percentage?: number;
  remaining_days?: number;
}

export interface ChartDetailCurrentDasha {
  mahadasha?: ChartDetailDashaPeriod;
  antardasha?: ChartDetailDashaPeriod;
  description?: string;
}

export interface ChartDetailDashaBirthBalance {
  planet?: string;
  years?: number;
  months?: number;
  days?: number;
}

export interface ChartDetailDashaBirthDetails {
  nakshatra_name?: string;
  nakshatra_number?: number;
  nakshatra_progress?: number;
  birth_dasha_lord?: string;
  elapsed_at_birth?: number;
}

/** Vargas / divisional chart: mapping of sign name to planet name arrays */
export type VargaChart = Record<string, string[]>;

export interface ChartDetailData {
  planets: Record<string, ChartDetailPlanetData>;
  houses: Record<string, ChartDetailHouseData> | number[];
  ascendant: { sign: string; degree: number; longitude?: number; nakshatra?: string };
  ayanamsa?: number;
  ayanamsa_name?: string;
  panchang?: {
    tithi?: ChartDetailPanchangItem;
    nakshatra?: ChartDetailPanchangItem;
    yoga?: ChartDetailPanchangItem;
    karana?: ChartDetailPanchangItem;
    vara?: { day?: string; ruler?: string };
    sunrise?: string;
    sunset?: string;
    ayanamsa?: number;
    [key: string]: unknown;
  };
  dasha?: {
    current_dasha?: ChartDetailCurrentDasha;
    birth_details?: ChartDetailDashaBirthDetails;
    birth_balance?: ChartDetailDashaBirthBalance;
    mahadashas?: ChartDetailDashaPeriod[];
    [key: string]: unknown;
  };
  vargas?: Record<string, VargaChart>;
  [key: string]: unknown;
}

export interface ChartDetail {
  chart_id: string;
  person_id: string;
  chart_type: string;
  house_system: string;
  ayanamsa: string;
  calculated_at: string;
  chart_data: ChartDetailData;
  planet_positions?: Record<string, ChartDetailPlanetData>;
  house_cusps?: number[];
  aspects?: ChartDetailAspectData[];
}

export interface ChartDetailAspectData {
  planet1: string;
  planet2: string;
  aspect: string;
  orb: number;
  angle?: number;
  applying?: boolean;
}

export interface ChartDetailPerson {
  person_id: string;
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  place_of_birth?: string;
}
