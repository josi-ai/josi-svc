'use client';

import type { PanchangData } from './panchang-types';
import { SectionHeading, TimingRow } from './panchang-shared';

export function TimingWindowsCard({ data }: { data: PanchangData }) {
  const auspicious = data.auspicious_times;
  const inauspicious = data.inauspicious_times;

  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 20 }}>
      <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, color: 'var(--text-primary)', marginBottom: 16 }}>
        Timing Windows
      </h3>

      <SectionHeading>Auspicious</SectionHeading>
      <TimingRow label="Brahma Muhurta" timeRange={auspicious?.brahma_muhurta} auspicious={true} />
      <TimingRow label="Abhijit Muhurta" timeRange={auspicious?.abhijit_muhurta} auspicious={true} />

      <div style={{ marginTop: 16 }}>
        <SectionHeading>Inauspicious</SectionHeading>
        <TimingRow label="Rahu Kaal" timeRange={inauspicious?.rahu_kaal} auspicious={false} />
        <TimingRow label="Gulika Kaal" timeRange={inauspicious?.gulika_kaal} auspicious={false} />
        <TimingRow label="Yamaganda" timeRange={inauspicious?.yamaganda} auspicious={false} />
      </div>
    </div>
  );
}
