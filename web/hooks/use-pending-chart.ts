'use client';

import { useEffect, useState } from 'react';

interface PendingBirthData {
  name: string;
  dob: string;
  tob: string;
  place: string;
}

/**
 * Checks sessionStorage for birth data from the landing page form.
 * Returns the data if found, and provides a clear function.
 *
 * Usage in dashboard:
 * ```
 * const { pendingChart, clearPendingChart } = usePendingChart();
 * useEffect(() => {
 *   if (pendingChart) {
 *     // Create chart via API, then:
 *     clearPendingChart();
 *     router.push(`/charts/${newChartId}`);
 *   }
 * }, [pendingChart]);
 * ```
 */
export function usePendingChart() {
  const [pendingChart, setPendingChart] = useState<PendingBirthData | null>(null);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem('josi-birth-data');
      if (raw) {
        const data = JSON.parse(raw) as PendingBirthData;
        if (data.dob) {
          setPendingChart(data);
        }
      }
    } catch {
      // ignore
    }
  }, []);

  const clearPendingChart = () => {
    sessionStorage.removeItem('josi-birth-data');
    setPendingChart(null);
  };

  return { pendingChart, clearPendingChart };
}
