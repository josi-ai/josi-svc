'use client';

import { Star } from 'lucide-react';
import type { ChartDetail, ChartDetailHouseData } from '@/types';
import { formatDegree } from './chart-detail-helpers';
import { ComingSoonCard } from './coming-soon-card';

export function HousesTab({ chart }: { chart: ChartDetail }) {
  const houses = chart.chart_data?.houses;
  const cusps = chart.house_cusps;

  // Try to build house data from either format
  let houseRows: { num: number; sign: string; degree: string; lord: string }[] = [];

  const SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
  ];
  const LORDS: Record<string, string> = {
    Aries: 'Mars', Taurus: 'Venus', Gemini: 'Mercury', Cancer: 'Moon',
    Leo: 'Sun', Virgo: 'Mercury', Libra: 'Venus', Scorpio: 'Mars',
    Sagittarius: 'Jupiter', Capricorn: 'Saturn', Aquarius: 'Saturn', Pisces: 'Jupiter',
  };

  if (Array.isArray(houses) && houses.length > 0) {
    houseRows = (houses as number[]).map((deg: number, i: number) => {
      const sign = SIGNS[Math.floor(deg / 30) % 12];
      return { num: i + 1, sign, degree: formatDegree(deg % 30), lord: LORDS[sign] || '\u2014' };
    });
  } else if (Array.isArray(cusps) && cusps.length > 0) {
    houseRows = cusps.map((deg, i) => {
      const sign = SIGNS[Math.floor(deg / 30) % 12];
      return { num: i + 1, sign, degree: formatDegree(deg % 30), lord: LORDS[sign] || '\u2014' };
    });
  } else if (houses && typeof houses === 'object' && !Array.isArray(houses)) {
    // Record<string, HouseData> format
    const housesObj = houses as Record<string, ChartDetailHouseData>;
    houseRows = Object.entries(housesObj).map(([key, data]) => ({
      num: parseInt(key) || 0,
      sign: data.sign || '\u2014',
      degree: formatDegree(data.degree),
      lord: LORDS[data.sign] || '\u2014',
    })).sort((a, b) => a.num - b.num);
  }

  if (houseRows.length === 0) {
    return (
      <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
        <ComingSoonCard icon={<Star style={{ width: 20, height: 20, color: 'var(--blue)' }} />} bgColor="var(--blue-bg)" message="Houses data not available for this chart" />
      </div>
    );
  }

  const headerStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.8,
    color: 'var(--text-faint)', fontWeight: 600, textAlign: 'left', borderBottom: '1px solid var(--border)',
  };
  const cellStyle: React.CSSProperties = {
    padding: '10px 16px', fontSize: 13, color: 'var(--text-secondary)', borderBottom: '1px solid var(--border)',
  };

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      <div style={{ border: '1px solid var(--border)', borderRadius: 12, background: 'var(--bg-card)', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>House</th>
                <th style={headerStyle}>Sign</th>
                <th style={headerStyle}>Degree</th>
                <th style={headerStyle}>Lord</th>
              </tr>
            </thead>
            <tbody>
              {houseRows.map((h) => (
                <tr
                  key={h.num}
                  style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ ...cellStyle, fontWeight: 600, color: 'var(--text-primary)' }}>{h.num}</td>
                  <td style={cellStyle}>{h.sign}</td>
                  <td style={{ ...cellStyle, fontFamily: 'monospace', fontSize: 11 }}>{h.degree}</td>
                  <td style={cellStyle}>{h.lord}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
