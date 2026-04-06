/**
 * Types for the Dasha page.
 */

export interface DashaPeriod {
  planet: string;
  start_date: string;
  end_date: string;
  duration_years: number;
  duration_days?: number;
  is_partial?: boolean;
  progress_percentage?: number;
  remaining_days?: number;
  antardashas?: DashaPeriod[];
}

export interface CurrentDasha {
  mahadasha?: DashaPeriod;
  antardasha?: DashaPeriod;
  pratyantardasha?: DashaPeriod;
  description?: string;
}

export interface DashaResponse {
  person_id: string;
  birth_nakshatra: string;
  current_dasha: CurrentDasha | null;
  dasha_sequence: DashaPeriod[];
  life_timeline: DashaPeriod[];
  detailed_periods?: {
    upcoming_changes?: { date: string; days_until: number; new_dasha: string; significance: string }[];
  };
}
