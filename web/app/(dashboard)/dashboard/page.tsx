'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { WidgetGrid } from '@/components/dashboard/widget-grid';
import { usePendingChart } from '@/hooks/use-pending-chart';
import { useAuth } from '@/contexts/AuthContext';

export default function DashboardPage() {
  const router = useRouter();
  const { pendingChart, clearPendingChart } = usePendingChart();
  const { getToken } = useAuth();
  const [creatingChart, setCreatingChart] = useState(false);

  useEffect(() => {
    if (!pendingChart || creatingChart) return;

    const chart = pendingChart; // capture non-null value for async closure
    async function createChart() {
      setCreatingChart(true);
      try {
        const token = await getToken();
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:1954';

        // First, create the person
        const personRes = await fetch(`${apiUrl}/api/v1/persons/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            name: chart.name || 'My Profile',
            date_of_birth: chart.dob,
            time_of_birth: chart.tob ? `${chart.dob} ${chart.tob.length === 5 ? chart.tob + ':00' : chart.tob}` : null,
            place_of_birth: chart.place || null,
          }),
        });

        if (!personRes.ok) throw new Error('Failed to create person');
        const personData = await personRes.json();
        const personId = personData?.data?.person_id;
        if (!personId) throw new Error('No person_id returned');

        // Then calculate charts (query params, not JSON body)
        const chartParams = new URLSearchParams({
          person_id: personId,
          systems: 'vedic,western',
          house_system: 'whole_sign',
          ayanamsa: 'lahiri',
        });
        const res = await fetch(`${apiUrl}/api/v1/charts/calculate?${chartParams}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (res.ok) {
          const data = await res.json();
          clearPendingChart();
          // Redirect to the new chart if we got an ID back
          if (data?.data?.chart_id) {
            router.push(`/charts/${data.data.chart_id}`);
            return;
          }
        }
      } catch (err) {
        console.error('Failed to auto-create chart:', err);
      }

      // Even if chart creation fails, clear the pending data so we don't retry endlessly
      clearPendingChart();
      setCreatingChart(false);
    }

    createChart();
  }, [pendingChart, creatingChart, getToken, clearPendingChart, router]);

  if (creatingChart) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center"
            style={{ background: 'var(--gold-bg)' }}>
            <span className="text-xl" style={{ color: 'var(--gold)' }}>&#10022;</span>
          </div>
          <h2 className="font-display text-xl mb-2" style={{ color: 'var(--text-primary)' }}>
            Creating your chart...
          </h2>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Calculating planetary positions across six traditions
          </p>
        </div>
      </div>
    );
  }

  return <WidgetGrid />;
}
