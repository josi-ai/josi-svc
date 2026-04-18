'use client';

import { useState, useMemo } from 'react';
import { useQuery, useQueries } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { LocationPicker, LocationValue } from '@/components/ui/location-picker';
import { TimeframeSelector } from '@/components/ui/timeframe-selector';
import { useDefaultProfile } from '@/hooks/use-default-profile';

import type { PanchangData, PanchangTimeframe } from './_components/panchang-types';
import { PANCHANG_TIMEFRAMES } from './_components/panchang-types';
import { todayString, dateString, weekDates, monthCalendarDates } from './_components/panchang-helpers';
import { SkeletonCard } from './_components/panchang-shared';
import { FiveElementsCard } from './_components/five-elements-card';
import { SunMoonCard } from './_components/sun-moon-card';
import { TimingWindowsCard } from './_components/timing-windows-card';
import { QualitySummaryCard } from './_components/quality-summary-card';
import { WeeklyStrip } from './_components/weekly-strip';
import { MonthlyCalendar } from './_components/monthly-calendar';

export default function PanchangPage() {
  const { location: defaultLocation, isLoading: profileLoading } = useDefaultProfile();
  const [date, setDate] = useState(todayString);
  const [location, setLocation] = useState<LocationValue | undefined>(undefined);
  const [timeframe, setTimeframe] = useState<PanchangTimeframe>('Daily');

  // Resolve effective location
  const effectiveLocation = location || (profileLoading
    ? undefined
    : {
        latitude: defaultLocation.latitude,
        longitude: defaultLocation.longitude,
        timezone: defaultLocation.timezone,
        displayName: 'Default',
      });

  // --- Daily query ---
  const { data: panchangResponse, isLoading, error } = useQuery({
    queryKey: ['panchang', date, effectiveLocation?.latitude, effectiveLocation?.longitude, effectiveLocation?.timezone],
    queryFn: () =>
      apiClient.get<{ detailed_panchang: PanchangData }>(
        `/api/v1/panchang/?date=${date}T06:00:00&latitude=${effectiveLocation!.latitude}&longitude=${effectiveLocation!.longitude}&timezone=${effectiveLocation!.timezone}`,
      ),
    enabled: !!effectiveLocation,
  });

  const panchang: PanchangData | null = panchangResponse?.data?.detailed_panchang || panchangResponse?.data as unknown as PanchangData || null;

  // --- Weekly ---
  const weekDays = useMemo(() => weekDates(date), [date]);

  const weekQueries = useQueries({
    queries: weekDays.map((d) => ({
      queryKey: ['panchang', d, effectiveLocation?.latitude, effectiveLocation?.longitude, effectiveLocation?.timezone],
      queryFn: () =>
        apiClient.get<{ detailed_panchang: PanchangData }>(
          `/api/v1/panchang/?date=${d}T06:00:00&latitude=${effectiveLocation!.latitude}&longitude=${effectiveLocation!.longitude}&timezone=${effectiveLocation!.timezone}`,
        ),
      enabled: !!effectiveLocation && timeframe === 'Weekly',
      staleTime: 10 * 60 * 1000,
    })),
  });

  const weekPanchangByDate: Record<string, PanchangData | null> = {};
  weekDays.forEach((d, i) => {
    const res = weekQueries[i]?.data;
    weekPanchangByDate[d] = res?.data?.detailed_panchang || res?.data as unknown as PanchangData || null;
  });
  const weekLoading = weekQueries.some((q) => q.isLoading);

  // --- Monthly ---
  const { grid: monthGrid } = useMemo(() => monthCalendarDates(date), [date]);
  const monthInMonthDates = useMemo(() => monthGrid.filter((g) => g.inMonth).map((g) => g.date), [monthGrid]);

  const monthQueries = useQueries({
    queries: monthInMonthDates.map((d) => ({
      queryKey: ['panchang', d, effectiveLocation?.latitude, effectiveLocation?.longitude, effectiveLocation?.timezone],
      queryFn: () =>
        apiClient.get<{ detailed_panchang: PanchangData }>(
          `/api/v1/panchang/?date=${d}T06:00:00&latitude=${effectiveLocation!.latitude}&longitude=${effectiveLocation!.longitude}&timezone=${effectiveLocation!.timezone}`,
        ),
      enabled: !!effectiveLocation && timeframe === 'Monthly',
      staleTime: 10 * 60 * 1000,
    })),
  });

  const monthPanchangByDate: Record<string, PanchangData | null> = {};
  monthInMonthDates.forEach((d, i) => {
    const res = monthQueries[i]?.data;
    monthPanchangByDate[d] = res?.data?.detailed_panchang || res?.data as unknown as PanchangData || null;
  });
  const monthLoading = monthQueries.some((q) => q.isLoading);

  // --- Handlers ---
  const handleDayClick = (d: string) => {
    setDate(d);
    setTimeframe('Daily');
  };

  const handleMonthChange = (delta: number) => {
    const d = new Date(date + 'T12:00:00');
    d.setMonth(d.getMonth() + delta);
    d.setDate(1);
    setDate(dateString(d));
  };

  const handleTimeframeChange = (tf: string) => {
    setTimeframe(tf as PanchangTimeframe);
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: 'var(--text-primary)', marginBottom: 4 }}>
          Panchang
        </h1>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Hindu calendar with tithi, nakshatra, yoga, karana, and timing windows.
        </p>
      </div>

      {/* Timeframe selector */}
      <TimeframeSelector
        value={timeframe}
        onChange={handleTimeframeChange}
        options={[...PANCHANG_TIMEFRAMES]}
        style={{ marginBottom: 20 }}
      />

      {/* Controls */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', marginBottom: 24, flexWrap: 'wrap' }}>
        <div style={{ flexShrink: 0 }}>
          <label style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, display: 'block', marginBottom: 6 }}>
            Date
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={{
              padding: '9px 14px', fontSize: 14, color: 'var(--text-primary)',
              background: 'var(--background)', border: '1px solid var(--border)',
              borderRadius: 8, outline: 'none', colorScheme: 'dark',
            }}
          />
        </div>
        <div style={{ flex: 1, minWidth: 280 }}>
          <label style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, display: 'block', marginBottom: 6 }}>
            Location
          </label>
          <LocationPicker value={location} onChange={setLocation} />
        </div>
      </div>

      {/* Weekly View */}
      {timeframe === 'Weekly' && effectiveLocation && (
        <div style={{ marginBottom: 24 }}>
          <WeeklyStrip
            dates={weekDays}
            panchangByDate={weekPanchangByDate}
            isLoadingAny={weekLoading}
            onDayClick={handleDayClick}
            selectedDate={date}
          />
        </div>
      )}

      {/* Monthly View */}
      {timeframe === 'Monthly' && effectiveLocation && (
        <div style={{ marginBottom: 24 }}>
          <MonthlyCalendar
            dateStr={date}
            panchangByDate={monthPanchangByDate}
            isLoadingAny={monthLoading}
            onDayClick={handleDayClick}
            onMonthChange={handleMonthChange}
          />
        </div>
      )}

      {/* Daily View */}
      {timeframe === 'Daily' && (
        <>
          {(isLoading || profileLoading) && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <SkeletonCard height={360} />
              <SkeletonCard height={180} />
              <SkeletonCard height={260} />
              <SkeletonCard height={160} />
              <style>{`@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }`}</style>
            </div>
          )}

          {error && (
            <div style={{ border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 32, textAlign: 'center' }}>
              <p style={{ fontSize: 14, color: 'var(--red)', marginBottom: 8 }}>Failed to load panchang</p>
              <p style={{ fontSize: 12, color: 'var(--text-faint)' }}>{(error as Error).message}</p>
            </div>
          )}

          {panchang && !isLoading && (
            <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
              <div style={{ marginBottom: 20 }}>
                <QualitySummaryCard data={panchang} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                <FiveElementsCard data={panchang} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <SunMoonCard data={panchang} />
                  <TimingWindowsCard data={panchang} />
                </div>
              </div>
              <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }`}</style>
            </div>
          )}
        </>
      )}
    </div>
  );
}
