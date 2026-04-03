'use client';

import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { LocationPicker, LocationValue } from '@/components/ui/location-picker';
import { ChevronLeft, ChevronRight } from 'lucide-react';

/* ---------- Types ---------- */

interface Activity {
  name: string;
  description: string;
  considerations: string[];
}

interface MuhurtaWindow {
  date?: string;
  start_time?: string;
  end_time?: string;
  score?: number;
  quality?: string;
  tithi?: string;
  nakshatra?: string;
  yoga?: string;
  reason?: string;
  explanation?: string;
  [key: string]: any;
}

interface TodaySummary {
  date: string;
  best_times: MuhurtaWindow[];
  rahu_kaal: { start: string; end: string } | string;
  general_advice: string;
}

interface MuhurtaResult {
  muhurtas: MuhurtaWindow[];
  search_criteria: { purpose: string; date_range: string; location: string; timezone: string };
  total_found: number;
}

/* ---------- Styles ---------- */

const cardStyle: React.CSSProperties = {
  background: 'var(--card)',
  border: '1px solid var(--border)',
  borderRadius: 14,
  padding: 24,
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 10,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '1.5px',
  color: 'var(--text-faint)',
  marginBottom: 6,
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  fontSize: 14,
  color: 'var(--text-primary)',
  background: 'var(--background)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  outline: 'none',
  transition: 'border-color 0.2s',
};

const focusHandlers = {
  onFocus: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.target.style.borderColor = 'var(--gold)';
  },
  onBlur: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.target.style.borderColor = 'var(--border)';
  },
};

/* ---------- Sub-components ---------- */

function TodayPanel({ location }: { location: LocationValue | undefined }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['muhurta-today', location?.latitude, location?.longitude, location?.timezone],
    queryFn: () =>
      apiClient.get<TodaySummary>(
        `/api/v1/muhurta/best-times-today?latitude=${location!.latitude}&longitude=${location!.longitude}&timezone=${encodeURIComponent(location!.timezone)}`
      ),
    enabled: !!location,
    retry: 1,
  });

  const summary = data?.data;

  if (!location) {
    return (
      <div style={cardStyle}>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Set your location to see today&apos;s summary.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Spinner />
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading today&apos;s times...</span>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div style={cardStyle}>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Could not load today&apos;s summary. Try searching for auspicious times below.
        </p>
      </div>
    );
  }

  const rahuKaal =
    typeof summary.rahu_kaal === 'string'
      ? summary.rahu_kaal
      : summary.rahu_kaal
        ? `${summary.rahu_kaal.start} - ${summary.rahu_kaal.end}`
        : 'N/A';

  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <span style={{ fontSize: 20 }}>{'\u2600'}</span>
        <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
          Today&apos;s Summary &mdash; {summary.date}
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
        {/* Rahu Kaal */}
        <div
          style={{
            padding: '12px 16px',
            borderRadius: 10,
            background: 'rgba(229,72,77,0.08)',
            border: '1px solid rgba(229,72,77,0.2)',
          }}
        >
          <div style={{ fontSize: 11, fontWeight: 600, color: '#E5484D', textTransform: 'uppercase', letterSpacing: 1 }}>
            Rahu Kaal (Avoid)
          </div>
          <div style={{ fontSize: 15, fontWeight: 500, color: '#E5484D', marginTop: 4 }}>{rahuKaal}</div>
        </div>

        {/* Best Times */}
        {summary.best_times?.slice(0, 2).map((t, i) => (
          <div
            key={i}
            style={{
              padding: '12px 16px',
              borderRadius: 10,
              background: 'rgba(48,164,108,0.08)',
              border: '1px solid rgba(48,164,108,0.2)',
            }}
          >
            <div style={{ fontSize: 11, fontWeight: 600, color: '#30A46C', textTransform: 'uppercase', letterSpacing: 1 }}>
              {t.quality || 'Good Period'}
            </div>
            <div style={{ fontSize: 15, fontWeight: 500, color: '#30A46C', marginTop: 4 }}>
              {t.start_time || t.date || 'See details'}
              {t.end_time ? ` - ${t.end_time}` : ''}
            </div>
            {t.nakshatra && (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>{t.nakshatra}</div>
            )}
          </div>
        ))}
      </div>

      {summary.general_advice && (
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 12, marginBottom: 0 }}>
          {summary.general_advice}
        </p>
      )}
    </div>
  );
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 80 ? '#30A46C' : score >= 60 ? '#F5A623' : score >= 40 ? '#E5884D' : '#E5484D';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ flex: 1, height: 6, borderRadius: 3, background: 'var(--border)' }}>
        <div style={{ width: `${Math.min(score, 100)}%`, height: '100%', borderRadius: 3, background: color, transition: 'width 0.3s' }} />
      </div>
      <span style={{ fontSize: 12, fontWeight: 600, color, minWidth: 28 }}>{score}</span>
    </div>
  );
}

function Spinner() {
  return (
    <>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: 'spin 1s linear infinite' }}>
        <circle cx="12" cy="12" r="10" stroke="var(--text-muted)" strokeWidth="3" strokeLinecap="round" strokeDasharray="31.42 31.42" />
      </svg>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </>
  );
}

/* ---------- Monthly Calendar Types ---------- */

interface DayQuality {
  date: string;
  quality: 'auspicious' | 'inauspicious' | 'mixed' | string;
  score?: number;
  tithi?: string;
  nakshatra?: string;
  note?: string;
}

interface MonthlyCalendarData {
  month: number;
  year: number;
  days: DayQuality[];
}

/* ---------- Monthly Calendar Component (T45) ---------- */

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const DAY_HEADERS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function qualityColor(quality: string): string {
  if (quality === 'auspicious') return '#30A46C';
  if (quality === 'inauspicious') return '#E5484D';
  if (quality === 'mixed') return '#F5A623';
  return 'var(--text-faint)';
}

function qualityBg(quality: string): string {
  if (quality === 'auspicious') return 'rgba(48,164,108,0.10)';
  if (quality === 'inauspicious') return 'rgba(229,72,77,0.10)';
  if (quality === 'mixed') return 'rgba(245,166,35,0.10)';
  return 'transparent';
}

function MuhurtaMonthlyCalendar({
  location,
  onSelectDate,
}: {
  location: LocationValue | undefined;
  onSelectDate: (startDate: string, endDate: string) => void;
}) {
  const [monthOffset, setMonthOffset] = useState(0);

  const now = new Date();
  const viewDate = new Date(now.getFullYear(), now.getMonth() + monthOffset, 1);
  const viewYear = viewDate.getFullYear();
  const viewMonth = viewDate.getMonth();
  const firstDay = new Date(viewYear, viewMonth, 1).getDay();
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();

  const today = new Date();
  const isCurrentMonth = today.getFullYear() === viewYear && today.getMonth() === viewMonth;

  // Fetch monthly calendar data
  const { data: calResponse, isLoading, isError } = useQuery({
    queryKey: ['muhurta-monthly', viewYear, viewMonth, location?.latitude, location?.longitude, location?.timezone],
    queryFn: () =>
      apiClient.post<MonthlyCalendarData>('/api/v1/muhurta/monthly-calendar', {
        year: viewYear,
        month: viewMonth + 1,
        latitude: location!.latitude,
        longitude: location!.longitude,
        timezone: location!.timezone,
      }),
    enabled: !!location,
    retry: false,
  });

  const dayMap = useMemo(() => {
    const map: Record<number, DayQuality> = {};
    const days = calResponse?.data?.days;
    if (days) {
      days.forEach((d) => {
        const dt = new Date(d.date);
        map[dt.getDate()] = d;
      });
    }
    return map;
  }, [calResponse]);

  const showFallback = isError;

  if (!location) {
    return (
      <div style={{ ...cardStyle, marginTop: 20, textAlign: 'center', padding: '32px 24px' }}>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>
          Set your location above to see the monthly auspicious calendar.
        </p>
      </div>
    );
  }

  return (
    <div style={{ ...cardStyle, marginTop: 20, padding: 0, overflow: 'hidden' }}>
      {/* Header with month nav */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
        <button
          onClick={() => setMonthOffset((p) => p - 1)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--text-secondary)', display: 'flex' }}
        >
          <ChevronLeft style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ textAlign: 'center' }}>
          <span style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
            {MONTH_NAMES[viewMonth]} {viewYear}
          </span>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '2px 0 0' }}>
            Auspicious Days Calendar
          </p>
        </div>
        <button
          onClick={() => setMonthOffset((p) => p + 1)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--text-secondary)', display: 'flex' }}
        >
          <ChevronRight style={{ width: 18, height: 18 }} />
        </button>
      </div>

      {showFallback ? (
        <div style={{ padding: '32px 24px', textAlign: 'center' }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>{'\uD83D\uDCC5'}</div>
          <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
            Monthly Calendar Coming Soon
          </p>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>
            The auspicious days calendar for each month is being developed. Use the search above to find specific times.
          </p>
        </div>
      ) : (
        <>
          {/* Day headers */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', borderBottom: '1px solid var(--border)' }}>
            {DAY_HEADERS.map((d) => (
              <div key={d} style={{ padding: '8px 4px', textAlign: 'center', fontSize: 10, fontWeight: 600, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8 }}>
                {d}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)' }}>
            {/* Empty offset cells */}
            {Array.from({ length: firstDay }).map((_, i) => (
              <div key={`e-${i}`} style={{ minHeight: 60, borderTop: '1px solid var(--border)' }} />
            ))}
            {/* Day cells */}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1;
              const isToday = isCurrentMonth && today.getDate() === day;
              const info = dayMap[day];
              const quality = info?.quality;
              const bg = quality ? qualityBg(quality) : 'transparent';
              const dotColor = quality ? qualityColor(quality) : undefined;

              const dateStr = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

              return (
                <div
                  key={day}
                  onClick={() => onSelectDate(dateStr, dateStr)}
                  title={info?.note || (quality ? `${quality.charAt(0).toUpperCase() + quality.slice(1)}${info?.tithi ? ' \u2014 ' + info.tithi : ''}` : '')}
                  style={{
                    minHeight: 60,
                    padding: '5px 6px',
                    borderTop: '1px solid var(--border)',
                    borderLeft: (firstDay + i) % 7 !== 0 ? '1px solid var(--border)' : 'none',
                    background: isToday ? 'var(--gold-bg)' : bg,
                    cursor: 'pointer',
                    transition: 'background 0.15s',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span style={{
                      fontSize: 12,
                      fontWeight: isToday ? 700 : 400,
                      color: isToday ? 'var(--gold)' : 'var(--text-secondary)',
                    }}>
                      {day}
                    </span>
                    {dotColor && (
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: dotColor }} />
                    )}
                  </div>
                  {info?.tithi && (
                    <div style={{ fontSize: 8, color: 'var(--text-faint)', marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {info.tithi}
                    </div>
                  )}
                  {info?.nakshatra && (
                    <div style={{ fontSize: 8, color: 'var(--text-faint)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {info.nakshatra}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Loading overlay */}
          {isLoading && (
            <div style={{ padding: '12px 20px', textAlign: 'center', borderTop: '1px solid var(--border)' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                <Spinner />
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Loading calendar data...</span>
              </div>
            </div>
          )}

          {/* Legend */}
          <div style={{ display: 'flex', gap: 16, padding: '10px 20px', borderTop: '1px solid var(--border)', flexWrap: 'wrap' }}>
            {[
              { color: '#30A46C', label: 'Auspicious' },
              { color: '#F5A623', label: 'Mixed' },
              { color: '#E5484D', label: 'Inauspicious' },
            ].map((l) => (
              <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <div style={{ width: 6, height: 6, borderRadius: '50%', background: l.color }} />
                <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{l.label}</span>
              </div>
            ))}
            <span style={{ fontSize: 10, color: 'var(--text-faint)', marginLeft: 'auto' }}>
              Click a day to search
            </span>
          </div>
        </>
      )}
    </div>
  );
}

/* ---------- Main Page ---------- */

export default function MuhurtaPage() {
  const [location, setLocation] = useState<LocationValue | undefined>();
  const [activity, setActivity] = useState('marriage');
  const [startDate, setStartDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split('T')[0];
  });

  // Fetch activities
  const { data: activitiesData } = useQuery({
    queryKey: ['muhurta-activities'],
    queryFn: () => apiClient.get<{ activities: Activity[]; note: string }>('/api/v1/muhurta/activities'),
  });
  const activities = activitiesData?.data?.activities || [];

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: () =>
      apiClient.post<MuhurtaResult>('/api/v1/muhurta/find-muhurta', {
        purpose: activity,
        start_date: `${startDate}T00:00:00`,
        end_date: `${endDate}T23:59:59`,
        latitude: location!.latitude,
        longitude: location!.longitude,
        timezone: location!.timezone,
        max_results: 20,
      }),
  });

  const handleSearch = useCallback(() => {
    if (!location) return;
    searchMutation.mutate();
  }, [location, searchMutation]);

  const results = searchMutation.data?.data;

  const selectStyle: React.CSSProperties = {
    ...inputStyle,
    appearance: 'none',
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235B6A8A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 12px center',
    paddingRight: 36,
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 16px' }}>
      {/* Header */}
      <h1
        className="font-display"
        style={{ fontSize: 28, color: 'var(--text-primary)', fontWeight: 400, marginBottom: 4 }}
      >
        Muhurta &mdash; Auspicious Timing
      </h1>
      <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 28 }}>
        Find the best times for important activities based on Vedic astrology
      </p>

      {/* Today's Summary */}
      <TodayPanel location={location} />

      {/* Search Form */}
      <div style={{ ...cardStyle, marginTop: 20 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginTop: 0, marginBottom: 20 }}>
          Find Auspicious Times
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          {/* Activity */}
          <div>
            <label style={labelStyle}>Activity</label>
            <select
              value={activity}
              onChange={(e) => setActivity(e.target.value)}
              style={selectStyle}
              {...focusHandlers}
            >
              {activities.length > 0
                ? activities.map((a) => (
                    <option key={a.name} value={a.name}>
                      {a.name.charAt(0).toUpperCase() + a.name.slice(1)}
                    </option>
                  ))
                : ['Marriage', 'Business', 'Travel', 'Education', 'Medical', 'Property'].map((a) => (
                    <option key={a} value={a.toLowerCase()}>
                      {a}
                    </option>
                  ))}
            </select>
            {activities.length > 0 && (
              <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 4, marginBottom: 0 }}>
                {activities.find((a) => a.name === activity)?.description || ''}
              </p>
            )}
          </div>

          {/* Start Date */}
          <div>
            <label style={labelStyle}>Start Date</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} style={inputStyle} {...focusHandlers} />
          </div>

          {/* End Date */}
          <div>
            <label style={labelStyle}>End Date</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} style={inputStyle} {...focusHandlers} />
          </div>
        </div>

        {/* Location */}
        <div style={{ marginTop: 16 }}>
          <label style={labelStyle}>Location</label>
          <LocationPicker value={location} onChange={setLocation} />
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          disabled={!location || searchMutation.isPending}
          style={{
            marginTop: 20,
            padding: '12px 32px',
            fontSize: 15,
            fontWeight: 600,
            color: '#060A14',
            background: !location ? 'var(--border)' : 'var(--gold)',
            border: 'none',
            borderRadius: 10,
            cursor: !location || searchMutation.isPending ? 'not-allowed' : 'pointer',
            opacity: !location ? 0.5 : 1,
            transition: 'opacity 0.2s, background 0.2s',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          {searchMutation.isPending ? (
            <>
              <Spinner />
              Searching...
            </>
          ) : (
            'Find Auspicious Times'
          )}
        </button>

        {/* Error */}
        {searchMutation.isError && (
          <div
            style={{
              marginTop: 16,
              padding: '10px 14px',
              borderRadius: 8,
              fontSize: 13,
              color: '#E5484D',
              background: 'rgba(229,72,77,0.08)',
              border: '1px solid rgba(229,72,77,0.2)',
            }}
          >
            {(searchMutation.error as Error)?.message || 'Failed to find auspicious times'}
          </div>
        )}
      </div>

      {/* Results */}
      {results && (
        <div style={{ ...cardStyle, marginTop: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
              Results &mdash; {results.total_found} time{results.total_found !== 1 ? 's' : ''} found
            </h3>
            <span style={{ fontSize: 12, color: 'var(--text-faint)' }}>
              {results.search_criteria.purpose} &middot; {results.search_criteria.date_range}
            </span>
          </div>

          {results.muhurtas.length === 0 ? (
            <p style={{ fontSize: 13, color: 'var(--text-muted)', padding: '20px 0', textAlign: 'center' }}>
              No auspicious times found for this period. Try expanding the date range.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {results.muhurtas.map((m, i) => (
                <div
                  key={i}
                  style={{
                    padding: '16px 20px',
                    borderRadius: 10,
                    background: 'var(--background)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>
                        {m.date || `Window ${i + 1}`}
                      </div>
                      {(m.start_time || m.end_time) && (
                        <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>
                          {m.start_time}{m.end_time ? ` - ${m.end_time}` : ''}
                        </div>
                      )}
                    </div>
                    {typeof m.score === 'number' && (
                      <div style={{ minWidth: 120 }}>
                        <ScoreBar score={m.score} />
                      </div>
                    )}
                  </div>

                  {/* Panchang elements */}
                  {(m.tithi || m.nakshatra || m.yoga) && (
                    <div style={{ display: 'flex', gap: 16, marginTop: 8, flexWrap: 'wrap' }}>
                      {m.tithi && (
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                          Tithi: <span style={{ color: 'var(--text-secondary)' }}>{m.tithi}</span>
                        </span>
                      )}
                      {m.nakshatra && (
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                          Nakshatra: <span style={{ color: 'var(--text-secondary)' }}>{m.nakshatra}</span>
                        </span>
                      )}
                      {m.yoga && (
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                          Yoga: <span style={{ color: 'var(--text-secondary)' }}>{m.yoga}</span>
                        </span>
                      )}
                    </div>
                  )}

                  {/* Reason / Explanation */}
                  {(m.reason || m.explanation) && (
                    <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8, marginBottom: 0, lineHeight: 1.5 }}>
                      {m.reason || m.explanation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty state when no search has been done */}
      {!results && !searchMutation.isPending && (
        <div
          style={{
            ...cardStyle,
            marginTop: 20,
            textAlign: 'center',
            padding: '40px 24px',
          }}
        >
          <div style={{ fontSize: 32, marginBottom: 12 }}>{'\u2728'}</div>
          <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: 0 }}>
            Select an activity, date range, and location, then click &quot;Find Auspicious Times&quot; to discover the best windows.
          </p>
        </div>
      )}

      {/* Monthly Auspicious Calendar (T45) */}
      <MuhurtaMonthlyCalendar
        location={location}
        onSelectDate={(start, end) => {
          setStartDate(start);
          setEndDate(end);
        }}
      />
    </div>
  );
}
