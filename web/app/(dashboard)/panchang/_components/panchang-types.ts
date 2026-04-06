/**
 * Types for the Panchang page.
 */

export interface PanchangElement {
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

export interface PanchangData {
  date?: string;
  sunrise?: string;
  sunset?: string;
  ayanamsa?: number;
  tithi?: PanchangElement;
  nakshatra?: PanchangElement;
  yoga?: PanchangElement;
  karana?: PanchangElement;
  vara?: { day?: string; ruler?: string };
  auspicious_times?: { abhijit_muhurta?: string; brahma_muhurta?: string };
  inauspicious_times?: { rahu_kaal?: string; gulika_kaal?: string; yamaganda?: string };
}

export type PanchangTimeframe = 'Daily' | 'Weekly' | 'Monthly';
export const PANCHANG_TIMEFRAMES: PanchangTimeframe[] = ['Daily', 'Weekly', 'Monthly'];
