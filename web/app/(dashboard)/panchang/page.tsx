'use client';

import { useState, useMemo } from 'react';
import { useQuery, useQueries } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { LocationPicker, LocationValue } from '@/components/ui/location-picker';
import { TimeframeSelector } from '@/components/ui/timeframe-selector';
import { useDefaultProfile } from '@/hooks/use-default-profile';

/* ================================================================
   Types
   ================================================================ */

interface PanchangElement {
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

interface PanchangData {
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

/* ================================================================
   Helpers
   ================================================================ */

function todayString(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function formatPercent(val?: number): string {
  if (val == null) return '\u2014';
  return `${Math.round(val)}%`;
}

function qualityColor(quality?: string): string {
  if (!quality) return 'var(--text-muted)';
  const q = quality.toLowerCase();
  if (q === 'auspicious') return '#46A758';
  if (q === 'inauspicious') return '#E5484D';
  return 'var(--text-secondary)';
}

function overallDayQuality(tithi?: PanchangElement, nakshatra?: PanchangElement, yoga?: PanchangElement): { label: string; color: string } {
  const scores: number[] = [];
  const toScore = (q?: string) => {
    if (!q) return 0.5;
    const lower = q.toLowerCase();
    if (lower === 'auspicious') return 1;
    if (lower === 'inauspicious') return 0;
    return 0.5;
  };
  if (yoga?.quality) scores.push(toScore(yoga.quality));
  // Tithi doesn't have quality directly but paksha can hint
  if (tithi?.paksha) scores.push(tithi.paksha === 'Shukla' ? 0.7 : 0.4);
  if (nakshatra?.ruler) scores.push(0.5); // neutral default

  const avg = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0.5;
  if (avg >= 0.7) return { label: 'Auspicious Day', color: '#46A758' };
  if (avg <= 0.3) return { label: 'Challenging Day', color: '#E5484D' };
  return { label: 'Mixed Day', color: 'var(--gold)' };
}

/* ================================================================
   Sub-components
   ================================================================ */

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h4
      style={{
        fontSize: 10,
        textTransform: 'uppercase',
        letterSpacing: 1.2,
        color: 'var(--text-faint)',
        marginBottom: 10,
        paddingLeft: 2,
        fontWeight: 600,
      }}
    >
      {children}
    </h4>
  );
}

function SkeletonCard({ height = 120 }: { height?: number }) {
  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 14,
        background: 'var(--bg-card)',
        height,
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
  );
}

function ElementRow({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
      <span style={{ fontSize: 11, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.6 }}>{label}</span>
      <div style={{ textAlign: 'right' }}>
        <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 600 }}>{value}</span>
        {sub && <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 8 }}>{sub}</span>}
      </div>
    </div>
  );
}

function TimingRow({ label, timeRange, auspicious }: { label: string; timeRange?: string; auspicious: boolean }) {
  if (!timeRange) return null;
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 0',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: auspicious ? '#46A758' : '#E5484D',
            flexShrink: 0,
          }}
        />
        <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>{label}</span>
      </div>
      <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontFamily: 'monospace' }}>{timeRange}</span>
    </div>
  );
}

/* ================================================================
   Five Elements Card
   ================================================================ */

function FiveElementsCard({ data }: { data: PanchangData }) {
  const { tithi, nakshatra, yoga, karana, vara } = data;

  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 20 }}>
      <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, color: 'var(--text-primary)', marginBottom: 16 }}>
        Five Elements
      </h3>

      {/* Tithi */}
      <ElementRow label="Tithi" value={tithi?.name || '\u2014'} sub={tithi?.paksha ? `${tithi.paksha} Paksha` : undefined} />
      {tithi?.deity && (
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>Deity: {tithi.deity}</span>
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{formatPercent(tithi.percent)} elapsed</span>
        </div>
      )}

      {/* Nakshatra */}
      <ElementRow label="Nakshatra" value={nakshatra?.name || '\u2014'} sub={nakshatra?.pada ? `Pada ${nakshatra.pada}` : undefined} />
      {nakshatra?.ruler && (
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>Ruler: {nakshatra.ruler}</span>
          {nakshatra.deity && <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>Deity: {nakshatra.deity}</span>}
        </div>
      )}

      {/* Yoga */}
      <ElementRow label="Yoga" value={yoga?.name || '\u2014'} sub={yoga?.quality ? yoga.quality : undefined} />
      {yoga?.quality && (
        <div style={{ padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: qualityColor(yoga.quality), fontWeight: 600 }}>{yoga.quality}</span>
        </div>
      )}

      {/* Karana */}
      <ElementRow label="Karana" value={karana?.name || '\u2014'} sub={karana?.quality ? karana.quality : undefined} />
      {karana?.quality && (
        <div style={{ padding: '4px 0 8px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 10, color: qualityColor(karana.quality), fontWeight: 600 }}>{karana.quality}</span>
        </div>
      )}

      {/* Vara */}
      <ElementRow label="Vara" value={vara?.day || '\u2014'} sub={vara?.ruler ? `Ruler: ${vara.ruler}` : undefined} />
    </div>
  );
}

/* ================================================================
   Sun & Moon Card
   ================================================================ */

function SunMoonCard({ data }: { data: PanchangData }) {
  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 20 }}>
      <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, color: 'var(--text-primary)', marginBottom: 16 }}>
        Sun & Moon
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div style={{ textAlign: 'center', padding: 16, borderRadius: 10, background: 'var(--background)' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>{'\u2600\uFE0F'}</div>
          <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 }}>Sunrise</p>
          <p style={{ fontSize: 18, fontWeight: 700, color: 'var(--gold)', fontFamily: 'monospace' }}>{data.sunrise || '\u2014'}</p>
        </div>
        <div style={{ textAlign: 'center', padding: 16, borderRadius: 10, background: 'var(--background)' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>{'\uD83C\uDF05'}</div>
          <p style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 }}>Sunset</p>
          <p style={{ fontSize: 18, fontWeight: 700, color: '#E5484D', fontFamily: 'monospace' }}>{data.sunset || '\u2014'}</p>
        </div>
      </div>
      {data.ayanamsa != null && (
        <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 12, textAlign: 'center' }}>
          Ayanamsa (Lahiri): {data.ayanamsa.toFixed(4)}
        </p>
      )}
    </div>
  );
}

/* ================================================================
   Timing Windows Card
   ================================================================ */

function TimingWindowsCard({ data }: { data: PanchangData }) {
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

/* ================================================================
   Quality Summary Card
   ================================================================ */

function QualitySummaryCard({ data }: { data: PanchangData }) {
  const quality = overallDayQuality(data.tithi, data.nakshatra, data.yoga);

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 14,
        background: 'var(--bg-card)',
        padding: 20,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: '50%',
          margin: '0 auto 12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: quality.color + '18',
        }}
      >
        <div style={{ width: 20, height: 20, borderRadius: '50%', background: quality.color }} />
      </div>
      <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 18, color: quality.color, marginBottom: 8 }}>
        {quality.label}
      </h3>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: 300, margin: '0 auto' }}>
        Based on {data.tithi?.name || 'Tithi'} ({data.tithi?.paksha || ''}), {data.nakshatra?.name || 'Nakshatra'}, and {data.yoga?.name || 'Yoga'} ({data.yoga?.quality || 'mixed'}).
      </p>
    </div>
  );
}

/* ================================================================
   Date helpers for Weekly / Monthly views
   ================================================================ */

type PanchangTimeframe = 'Daily' | 'Weekly' | 'Monthly';
const PANCHANG_TIMEFRAMES: PanchangTimeframe[] = ['Daily', 'Weekly', 'Monthly'];

function dateString(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

/** Returns Monday of the week containing d */
function getMonday(d: Date): Date {
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const m = new Date(d);
  m.setDate(diff);
  m.setHours(0, 0, 0, 0);
  return m;
}

/** Returns 7 date strings starting from Monday of the week containing dateStr */
function weekDates(dateStr: string): string[] {
  const d = new Date(dateStr + 'T12:00:00');
  const mon = getMonday(d);
  const dates: string[] = [];
  for (let i = 0; i < 7; i++) {
    const day = new Date(mon);
    day.setDate(mon.getDate() + i);
    dates.push(dateString(day));
  }
  return dates;
}

/** Returns first day of month and all calendar grid dates (padded to full weeks) */
function monthCalendarDates(dateStr: string): { year: number; month: number; grid: { date: string; inMonth: boolean }[] } {
  const d = new Date(dateStr + 'T12:00:00');
  const year = d.getFullYear();
  const month = d.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  // Start from Monday before (or on) the 1st
  const startMon = getMonday(firstDay);
  // End on Sunday after (or on) the last day
  const endDate = new Date(lastDay);
  const endDow = endDate.getDay();
  if (endDow !== 0) endDate.setDate(endDate.getDate() + (7 - endDow));

  const grid: { date: string; inMonth: boolean }[] = [];
  const cursor = new Date(startMon);
  while (cursor <= endDate) {
    grid.push({
      date: dateString(cursor),
      inMonth: cursor.getMonth() === month,
    });
    cursor.setDate(cursor.getDate() + 1);
  }

  return { year, month, grid };
}

function shortDay(dateStr: string): string {
  return new Date(dateStr + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short' });
}

function dayNum(dateStr: string): number {
  return new Date(dateStr + 'T12:00:00').getDate();
}

function monthYearLabel(dateStr: string): string {
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

/** Abbreviated tithi: "Shukla Dvitiya" -> "S2" */
function tithiAbbrev(tithi?: PanchangElement): string {
  if (!tithi?.name) return '';
  const num = tithi.number;
  const paksha = tithi.paksha;
  const prefix = paksha === 'Shukla' ? 'S' : paksha === 'Krishna' ? 'K' : '';
  return num != null ? `${prefix}${num}` : tithi.name.slice(0, 3);
}

/** Quality dot color for a day */
function dayQualityColor(data: PanchangData | null | undefined): string {
  if (!data) return 'var(--border)';
  const q = overallDayQuality(data.tithi, data.nakshatra, data.yoga);
  return q.color;
}

/* ================================================================
   Weekly Strip View
   ================================================================ */

function WeeklyStrip({
  dates,
  panchangByDate,
  isLoadingAny,
  onDayClick,
  selectedDate,
}: {
  dates: string[];
  panchangByDate: Record<string, PanchangData | null>;
  isLoadingAny: boolean;
  onDayClick: (date: string) => void;
  selectedDate: string;
}) {
  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: 10,
        }}
      >
        {dates.map((d) => {
          const data = panchangByDate[d] || null;
          const isToday = d === todayString();
          const isSelected = d === selectedDate;
          const qualColor = dayQualityColor(data);

          return (
            <div
              key={d}
              onClick={() => onDayClick(d)}
              style={{
                border: isSelected ? '2px solid var(--gold)' : isToday ? '2px solid var(--text-muted)' : '1px solid var(--border)',
                borderRadius: 12,
                background: 'var(--bg-card)',
                padding: '14px 10px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'border-color 0.15s ease, transform 0.1s ease',
                minHeight: 130,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 6,
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              {/* Day name */}
              <span style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, fontWeight: 600 }}>
                {shortDay(d)}
              </span>
              {/* Day number */}
              <span style={{ fontSize: 20, fontWeight: 700, color: isToday ? 'var(--gold)' : 'var(--text-primary)' }}>
                {dayNum(d)}
              </span>
              {/* Quality dot */}
              <div style={{
                width: 10, height: 10, borderRadius: '50%',
                background: data ? qualColor : 'var(--border)',
                opacity: data ? 1 : 0.3,
              }} />
              {/* Tithi */}
              {data ? (
                <>
                  <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 500 }}>
                    {data.tithi?.name || '\u2014'}
                  </span>
                  <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>
                    {data.nakshatra?.name || ''}
                  </span>
                </>
              ) : isLoadingAny ? (
                <div style={{ width: '70%', height: 10, borderRadius: 4, background: 'var(--border)', animation: 'pulse 1.5s ease-in-out infinite' }} />
              ) : null}
            </div>
          );
        })}
      </div>
      <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }`}</style>
    </div>
  );
}

/* ================================================================
   Monthly Calendar View
   ================================================================ */

function MonthlyCalendar({
  dateStr,
  panchangByDate,
  isLoadingAny,
  onDayClick,
  onMonthChange,
}: {
  dateStr: string;
  panchangByDate: Record<string, PanchangData | null>;
  isLoadingAny: boolean;
  onDayClick: (date: string) => void;
  onMonthChange: (delta: number) => void;
}) {
  const { year, month, grid } = useMemo(() => monthCalendarDates(dateStr), [dateStr]);
  const today = todayString();
  const DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
      {/* Month navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20, marginBottom: 16 }}>
        <button
          type="button"
          onClick={() => onMonthChange(-1)}
          style={{
            background: 'none', border: '1px solid var(--border)', borderRadius: 8,
            padding: '6px 14px', cursor: 'pointer', color: 'var(--text-primary)', fontSize: 14,
          }}
        >
          &larr;
        </button>
        <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 18, color: 'var(--text-primary)', margin: 0, minWidth: 200, textAlign: 'center' }}>
          {new Date(year, month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </h3>
        <button
          type="button"
          onClick={() => onMonthChange(1)}
          style={{
            background: 'none', border: '1px solid var(--border)', borderRadius: 8,
            padding: '6px 14px', cursor: 'pointer', color: 'var(--text-primary)', fontSize: 14,
          }}
        >
          &rarr;
        </button>
      </div>

      {/* Day-of-week headers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, marginBottom: 4 }}>
        {DOW.map((d) => (
          <div key={d} style={{ textAlign: 'center', fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, fontWeight: 600, padding: '6px 0' }}>
            {d}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 }}>
        {grid.map(({ date, inMonth }) => {
          const data = panchangByDate[date] || null;
          const isToday = date === today;
          const qualColor = dayQualityColor(data);
          const bgTint = data
            ? qualColor === '#46A758' ? 'rgba(70,167,88,0.08)'
              : qualColor === '#E5484D' ? 'rgba(229,72,77,0.08)'
              : 'rgba(212,175,55,0.06)'
            : 'transparent';

          return (
            <div
              key={date}
              onClick={() => inMonth && onDayClick(date)}
              style={{
                border: isToday ? '1px solid var(--gold)' : '1px solid var(--border)',
                borderRadius: 8,
                background: inMonth ? bgTint : 'transparent',
                padding: '8px 6px',
                minHeight: 56,
                cursor: inMonth ? 'pointer' : 'default',
                opacity: inMonth ? 1 : 0.3,
                transition: 'background 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
                <span style={{ fontSize: 13, fontWeight: isToday ? 700 : 500, color: isToday ? 'var(--gold)' : 'var(--text-primary)' }}>
                  {dayNum(date)}
                </span>
                {data && (
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: qualColor }} />
                )}
              </div>
              {data && inMonth && (
                <span style={{ fontSize: 9, color: 'var(--text-muted)', fontWeight: 500 }}>
                  {tithiAbbrev(data.tithi)}
                </span>
              )}
              {!data && inMonth && isLoadingAny && (
                <div style={{ width: '60%', height: 6, borderRadius: 3, background: 'var(--border)', animation: 'pulse 1.5s ease-in-out infinite', marginTop: 2 }} />
              )}
            </div>
          );
        })}
      </div>
      <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }`}</style>
    </div>
  );
}

/* ================================================================
   Main Page
   ================================================================ */

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

  // --- Daily query (also used as the selected-day detail in weekly/monthly) ---
  const { data: panchangResponse, isLoading, error } = useQuery({
    queryKey: ['panchang', date, effectiveLocation?.latitude, effectiveLocation?.longitude, effectiveLocation?.timezone],
    queryFn: () =>
      apiClient.get<{ detailed_panchang: PanchangData }>(
        `/api/v1/panchang/?date=${date}T06:00:00&latitude=${effectiveLocation!.latitude}&longitude=${effectiveLocation!.longitude}&timezone=${effectiveLocation!.timezone}`,
      ),
    enabled: !!effectiveLocation,
  });

  const panchang: PanchangData | null = panchangResponse?.data?.detailed_panchang || panchangResponse?.data as unknown as PanchangData || null;

  // --- Weekly: compute the 7 dates for the current week ---
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

  // --- Monthly: fetch panchang for each day in the month ---
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
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
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
      <div
        style={{
          display: 'flex',
          gap: 12,
          alignItems: 'flex-start',
          marginBottom: 24,
          flexWrap: 'wrap',
        }}
      >
        {/* Date picker */}
        <div style={{ flexShrink: 0 }}>
          <label style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, display: 'block', marginBottom: 6 }}>
            Date
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={{
              padding: '9px 14px',
              fontSize: 14,
              color: 'var(--text-primary)',
              background: 'var(--background)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              outline: 'none',
              colorScheme: 'dark',
            }}
          />
        </div>

        {/* Location picker */}
        <div style={{ flex: 1, minWidth: 280 }}>
          <label style={{ fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, display: 'block', marginBottom: 6 }}>
            Location
          </label>
          <LocationPicker value={location} onChange={setLocation} />
        </div>
      </div>

      {/* ===== WEEKLY VIEW ===== */}
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

      {/* ===== MONTHLY VIEW ===== */}
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

      {/* ===== DAILY VIEW ===== */}
      {timeframe === 'Daily' && (
        <>
          {/* Loading */}
          {(isLoading || profileLoading) && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <SkeletonCard height={360} />
              <SkeletonCard height={180} />
              <SkeletonCard height={260} />
              <SkeletonCard height={160} />
              <style>{`@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }`}</style>
            </div>
          )}

          {/* Error */}
          {error && (
            <div
              style={{
                border: '1px solid var(--border)',
                borderRadius: 14,
                background: 'var(--bg-card)',
                padding: 32,
                textAlign: 'center',
              }}
            >
              <p style={{ fontSize: 14, color: '#E5484D', marginBottom: 8 }}>Failed to load panchang</p>
              <p style={{ fontSize: 12, color: 'var(--text-faint)' }}>{(error as Error).message}</p>
            </div>
          )}

          {/* Content */}
          {panchang && !isLoading && (
            <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
              {/* Quality Summary at top */}
              <div style={{ marginBottom: 20 }}>
                <QualitySummaryCard data={panchang} />
              </div>

              {/* Two-column layout */}
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
