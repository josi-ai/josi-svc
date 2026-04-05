'use client';

import type { ChartDetail } from '@/types';
import { getPlanets, safeStr } from './chart-detail-helpers';

export function QuickInfoPanel({ chart }: { chart: ChartDetail }) {
  const planets = getPlanets(chart);
  const sun = planets['Sun'];
  const moon = planets['Moon'];
  const asc = chart.chart_data?.ascendant;
  const isVedic = chart.chart_type === 'vedic';
  const panchang = chart.chart_data?.panchang;

  // Determine nakshatra value
  let nakshatraValue = '\u2014';
  if (isVedic && moon?.nakshatra) {
    nakshatraValue = moon.nakshatra;
  } else if (isVedic && panchang?.nakshatra) {
    nakshatraValue = safeStr(panchang.nakshatra?.name || panchang.nakshatra);
  }

  const items: { label: string; value: string }[] = [
    { label: 'Sun Sign', value: sun?.sign || '\u2014' },
    { label: 'Moon Sign', value: moon?.sign || '\u2014' },
    { label: 'Ascendant', value: asc?.sign || '\u2014' },
    { label: 'Nakshatra', value: nakshatraValue },
    { label: 'Ayanamsa', value: chart.ayanamsa ? chart.ayanamsa.charAt(0).toUpperCase() + chart.ayanamsa.slice(1) : '\u2014' },
    { label: 'House System', value: chart.house_system ? chart.house_system.charAt(0).toUpperCase() + chart.house_system.slice(1) : '\u2014' },
    { label: 'Chart Type', value: chart.chart_type ? chart.chart_type.charAt(0).toUpperCase() + chart.chart_type.slice(1) : '\u2014' },
    { label: 'Calculated Date', value: chart.calculated_at ? new Date(chart.calculated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '\u2014' },
  ];

  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '16px 24px',
        }}
      >
        {items.map((item) => (
          <div key={item.label}>
            <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 }}>
              {item.label}
            </p>
            <p style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 600 }}>{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
