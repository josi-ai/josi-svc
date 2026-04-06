'use client';

import { useMemo } from 'react';
import type { PanchangData } from './panchang-types';
import { todayString, dayNum, dayQualityColor, tithiAbbrev, monthCalendarDates } from './panchang-helpers';

export function MonthlyCalendar({
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
            ? qualColor === 'var(--bar-good)' ? 'var(--green-bg)'
              : qualColor === 'var(--bar-avoid)' ? 'var(--red-bg)'
              : 'var(--gold-bg-subtle)'
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
