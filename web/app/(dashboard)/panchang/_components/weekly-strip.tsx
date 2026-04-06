'use client';

import type { PanchangData } from './panchang-types';
import { todayString, shortDay, dayNum, dayQualityColor } from './panchang-helpers';

export function WeeklyStrip({
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
