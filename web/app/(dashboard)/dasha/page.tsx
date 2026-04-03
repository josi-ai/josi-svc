'use client';

import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';

/* ================================================================
   Types
   ================================================================ */

interface DashaPeriod {
  planet: string;
  start_date: string;
  end_date: string;
  duration_years: number;
  duration_days?: number;
  is_partial?: boolean;
  progress_percentage?: number;
  remaining_days?: number;
  antardashas?: DashaPeriod[];
}

interface CurrentDasha {
  mahadasha?: DashaPeriod;
  antardasha?: DashaPeriod;
  pratyantardasha?: DashaPeriod;
  description?: string;
}

interface DashaResponse {
  person_id: string;
  birth_nakshatra: string;
  current_dasha: CurrentDasha | null;
  dasha_sequence: DashaPeriod[];
  life_timeline: DashaPeriod[];
  detailed_periods?: {
    upcoming_changes?: { date: string; days_until: number; new_dasha: string; significance: string }[];
  };
}

/* ================================================================
   Constants & Helpers
   ================================================================ */

const PLANET_COLORS: Record<string, string> = {
  Sun: '#E5484D', Moon: '#6E7BD0', Mars: '#E5484D', Mercury: '#46A758',
  Jupiter: '#F5A623', Venus: '#C084FC', Saturn: '#6B7280', Rahu: '#9CA3AF', Ketu: '#78716C',
};
const pColor = (p: string) => PLANET_COLORS[p] || 'var(--text-muted)';

function parseDate(d: string | Date | undefined): Date | null {
  if (!d) return null;
  const dt = d instanceof Date ? d : new Date(d);
  return isNaN(dt.getTime()) ? null : dt;
}

function fmtDate(d: string | Date | undefined): string {
  const dt = parseDate(d);
  return dt ? dt.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '\u2014';
}

const HEADING: React.CSSProperties = { fontFamily: "'DM Serif Display', serif", fontSize: 16, color: 'var(--text-primary)', marginBottom: 16 };
const CARD: React.CSSProperties = { border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 20 };
const LABEL: React.CSSProperties = { fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 };

/* ================================================================
   Planet Interpretations
   ================================================================ */

interface PlanetInterpretation {
  theme: string;
  areas: string[];
  doAdvice: string[];
  dontAdvice: string[];
}

const PLANET_INTERPRETATIONS: Record<string, PlanetInterpretation> = {
  Sun: {
    theme: 'A period of authority, recognition, and self-expression. The soul seeks to shine and assert its identity in the world.',
    areas: ['Authority & leadership', 'Father & paternal figures', 'Government & politics', 'Career recognition', 'Vitality & health'],
    doAdvice: ['Take on leadership roles', 'Strengthen relationship with father', 'Pursue government-related matters', 'Focus on career advancement'],
    dontAdvice: ['Avoid ego conflicts', 'Don\'t be overly dominating', 'Avoid excessive sun exposure', 'Don\'t ignore heart health'],
  },
  Moon: {
    theme: 'An emotional and intuitive period focused on the mind, nurturing, and inner peace. Travel and changes of residence are common.',
    areas: ['Emotions & mental peace', 'Mother & maternal figures', 'Mind & intuition', 'Travel & relocation', 'Public dealings'],
    doAdvice: ['Nurture emotional well-being', 'Strengthen bond with mother', 'Practice meditation', 'Explore travel opportunities'],
    dontAdvice: ['Avoid emotional decisions', 'Don\'t neglect mental health', 'Avoid excessive worry', 'Don\'t suppress feelings'],
  },
  Mars: {
    theme: 'A dynamic period of energy, courage, and action. Property matters and sibling relationships come into focus.',
    areas: ['Energy & physical vitality', 'Courage & determination', 'Property & real estate', 'Siblings', 'Technical skills'],
    doAdvice: ['Channel energy into exercise', 'Pursue property investments', 'Take bold decisions', 'Develop technical skills'],
    dontAdvice: ['Avoid anger and aggression', 'Don\'t rush into conflicts', 'Avoid risky adventures', 'Don\'t neglect injuries'],
  },
  Mercury: {
    theme: 'A cerebral period emphasizing communication, business acumen, and intellectual growth. Education and trade flourish.',
    areas: ['Communication & speech', 'Business & commerce', 'Education & learning', 'Intellect & analysis', 'Writing & media'],
    doAdvice: ['Pursue education and certifications', 'Start business ventures', 'Improve communication skills', 'Write and publish'],
    dontAdvice: ['Avoid dishonesty', 'Don\'t overthink decisions', 'Avoid nervous exhaustion', 'Don\'t neglect details'],
  },
  Jupiter: {
    theme: 'An expansive period of wisdom, fortune, and spiritual growth. Children, teaching, and prosperity are highlighted.',
    areas: ['Wisdom & higher learning', 'Expansion & prosperity', 'Children & progeny', 'Spirituality & faith', 'Teaching & mentoring'],
    doAdvice: ['Pursue spiritual practices', 'Invest in education', 'Focus on family and children', 'Seek mentorship opportunities'],
    dontAdvice: ['Avoid overindulgence', 'Don\'t be overly optimistic financially', 'Avoid neglecting health through excess', 'Don\'t ignore practical matters'],
  },
  Venus: {
    theme: 'A period of love, beauty, creativity, and material comforts. Marriage, arts, and luxuries are emphasized.',
    areas: ['Love & relationships', 'Luxury & material comforts', 'Arts & creativity', 'Marriage & partnerships', 'Beauty & aesthetics'],
    doAdvice: ['Cultivate relationships', 'Pursue artistic interests', 'Invest in comforts', 'Attend to personal grooming'],
    dontAdvice: ['Avoid excessive spending', 'Don\'t overindulge in pleasures', 'Avoid superficial relationships', 'Don\'t neglect responsibilities for fun'],
  },
  Saturn: {
    theme: 'A period of discipline, hard work, and karmic lessons. Delays bring eventual rewards through persistent effort.',
    areas: ['Discipline & structure', 'Delays & obstacles', 'Hard work & perseverance', 'Karma & life lessons', 'Service & duty'],
    doAdvice: ['Embrace discipline and routine', 'Work diligently toward goals', 'Practice patience', 'Serve elders and underprivileged'],
    dontAdvice: ['Avoid shortcuts', 'Don\'t resist change or lessons', 'Avoid pessimism and despair', 'Don\'t neglect health and joints'],
  },
  Rahu: {
    theme: 'An unconventional period of ambition, foreign connections, and sudden transformations. Material desires intensify.',
    areas: ['Ambition & worldly desires', 'Foreign lands & travel', 'Unconventional paths', 'Sudden changes', 'Technology & innovation'],
    doAdvice: ['Explore foreign opportunities', 'Embrace technology', 'Think outside the box', 'Pursue ambitious goals'],
    dontAdvice: ['Avoid obsessive behavior', 'Don\'t fall for illusions', 'Avoid substance abuse', 'Don\'t chase shortcuts to success'],
  },
  Ketu: {
    theme: 'A deeply spiritual period of detachment, introspection, and liberation from past karma. Material focus diminishes.',
    areas: ['Spirituality & moksha', 'Detachment & letting go', 'Past-life karma', 'Liberation & enlightenment', 'Healing & alternative medicine'],
    doAdvice: ['Deepen spiritual practice', 'Let go of attachments', 'Explore meditation and yoga', 'Study esoteric subjects'],
    dontAdvice: ['Avoid clinging to material outcomes', 'Don\'t resist the process of release', 'Avoid isolation from loved ones', 'Don\'t ignore recurring patterns'],
  },
};

/* ================================================================
   Dasha Interpretation Panel
   ================================================================ */

function DashaInterpretationPanel({ planet, startDate, endDate, onClose }: {
  planet: string;
  startDate: string;
  endDate: string;
  onClose: () => void;
}) {
  const router = useRouter();
  const interp = PLANET_INTERPRETATIONS[planet];
  const panelRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    if (panelRef.current) {
      setHeight(panelRef.current.scrollHeight);
    }
  }, [planet]);

  if (!interp) return null;

  return (
    <div
      style={{
        overflow: 'hidden',
        maxHeight: height || 'none',
        transition: 'max-height 0.3s ease',
      }}
    >
      <div
        ref={panelRef}
        style={{
          ...CARD,
          borderColor: pColor(planet),
          borderWidth: 1,
          borderStyle: 'solid',
          marginTop: 8,
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 8,
              background: pColor(planet) + '22',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <div style={{ width: 14, height: 14, borderRadius: 4, background: pColor(planet) }} />
            </div>
            <div>
              <h4 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                {planet} Dasha
              </h4>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0 }}>
                {fmtDate(startDate)} &ndash; {fmtDate(endDate)}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); onClose(); }}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: 18, color: 'var(--text-muted)', padding: '2px 6px', lineHeight: 1,
            }}
          >
            &times;
          </button>
        </div>

        {/* Theme */}
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 16 }}>
          {interp.theme}
        </p>

        {/* Life Areas */}
        <div style={{ marginBottom: 16 }}>
          <p style={{ ...LABEL, marginBottom: 8 }}>Life Areas Affected</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {interp.areas.map((area) => (
              <span key={area} style={{
                fontSize: 11, padding: '4px 10px', borderRadius: 20,
                background: pColor(planet) + '15', color: pColor(planet),
                fontWeight: 500,
              }}>
                {area}
              </span>
            ))}
          </div>
        </div>

        {/* Do / Don't */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <div>
            <p style={{ ...LABEL, color: '#46A758', marginBottom: 8 }}>Do</p>
            {interp.doAdvice.map((item) => (
              <div key={item} style={{ display: 'flex', gap: 6, alignItems: 'flex-start', marginBottom: 6 }}>
                <span style={{ color: '#46A758', fontSize: 12, lineHeight: '18px' }}>+</span>
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: '18px' }}>{item}</span>
              </div>
            ))}
          </div>
          <div>
            <p style={{ ...LABEL, color: '#E5484D', marginBottom: 8 }}>Don&apos;t</p>
            {interp.dontAdvice.map((item) => (
              <div key={item} style={{ display: 'flex', gap: 6, alignItems: 'flex-start', marginBottom: 6 }}>
                <span style={{ color: '#E5484D', fontSize: 12, lineHeight: '18px' }}>&minus;</span>
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: '18px' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Ask AI */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            router.push(`/ai?q=${encodeURIComponent(`Tell me about my ${planet} dasha period`)}`);
          }}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '8px 16px', fontSize: 12, fontWeight: 600,
            color: 'var(--gold)', background: 'rgba(212,175,55,0.1)',
            border: '1px solid rgba(212,175,55,0.25)', borderRadius: 8,
            cursor: 'pointer', transition: 'background 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(212,175,55,0.18)')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(212,175,55,0.1)')}
        >
          Ask AI about this period
        </button>
      </div>
    </div>
  );
}

/* ================================================================
   Shared Sub-components
   ================================================================ */

function SkeletonBar({ width, height = 40 }: { width: string; height?: number }) {
  return <div style={{ width, height, borderRadius: 8, background: 'var(--border)', animation: 'pulse 1.5s ease-in-out infinite' }} />;
}

/** Renders one dasha period block (planet name, dates, remaining time). */
function PeriodBlock({ label, period }: { label: string; period: DashaPeriod }) {
  const remaining = period.remaining_days;
  const remLabel = remaining != null
    ? (remaining > 365 ? `${Math.round(remaining / 365.25 * 10) / 10} years remaining` : `${remaining} days remaining`)
    : null;

  return (
    <div style={{ flex: 1, minWidth: 160 }}>
      <p style={LABEL}>{label}</p>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{ width: 12, height: 12, borderRadius: 3, background: pColor(period.planet) }} />
        <span style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>{period.planet}</span>
      </div>
      <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>{fmtDate(period.start_date)} \u2013 {fmtDate(period.end_date)}</p>
      {remLabel && <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 4 }}>{remLabel}</p>}
    </div>
  );
}

/* ================================================================
   Mahadasha Timeline
   ================================================================ */

function MahadashaTimeline({ periods, currentPlanet, onPlanetClick }: { periods: DashaPeriod[]; currentPlanet?: string; onPlanetClick?: (period: DashaPeriod) => void }) {
  const firstStart = parseDate(periods[0]?.start_date);
  if (!firstStart || periods.length === 0) return null;

  const endMs = firstStart.getTime() + 120 * 365.25 * 86400000;
  const totalMs = endMs - firstStart.getTime();
  const visible = periods.filter((p) => { const s = parseDate(p.start_date); return s && s.getTime() < endMs; });

  // Decade ticks
  const ticks: { year: number; pct: number }[] = [];
  for (let y = Math.ceil(firstStart.getFullYear() / 10) * 10; y <= firstStart.getFullYear() + 120; y += 10) {
    const pct = ((new Date(y, 0, 1).getTime() - firstStart.getTime()) / totalMs) * 100;
    if (pct >= 0 && pct <= 100) ticks.push({ year: y, pct });
  }
  const nowPct = ((Date.now() - firstStart.getTime()) / totalMs) * 100;

  return (
    <div style={CARD}>
      <h3 style={HEADING}>Mahadasha Timeline</h3>
      {/* Bar */}
      <div style={{ position: 'relative', height: 44, borderRadius: 8, overflow: 'hidden', background: 'var(--background)', marginBottom: 8 }}>
        {visible.map((p, i) => {
          const s = parseDate(p.start_date)!.getTime();
          const e = Math.min(parseDate(p.end_date)!.getTime(), endMs);
          const left = ((s - firstStart.getTime()) / totalMs) * 100;
          const w = ((e - s) / totalMs) * 100;
          const cur = p.planet === currentPlanet;
          return (
            <div key={`${p.planet}-${i}`} title={`${p.planet}: ${fmtDate(p.start_date)} \u2013 ${fmtDate(p.end_date)}`}
              onClick={() => onPlanetClick?.(p)}
              style={{
              position: 'absolute', left: `${left}%`, width: `${w}%`, top: 0, bottom: 0,
              background: pColor(p.planet), opacity: cur ? 1 : 0.6,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderLeft: i > 0 ? '1px solid var(--background)' : 'none',
              cursor: 'pointer',
              ...(cur ? { outline: '2px solid var(--gold)', outlineOffset: -2, zIndex: 2 } : {}),
            }}>
              {w > 5 && <span style={{ fontSize: w > 8 ? 11 : 9, color: '#fff', fontWeight: 600, textShadow: '0 1px 2px rgba(0,0,0,0.5)', whiteSpace: 'nowrap', overflow: 'hidden' }}>{p.planet}</span>}
            </div>
          );
        })}
        {nowPct > 0 && nowPct < 100 && <div style={{ position: 'absolute', left: `${nowPct}%`, top: -4, bottom: -4, width: 2, background: 'var(--gold)', zIndex: 5 }} />}
      </div>
      {/* Ticks */}
      <div style={{ position: 'relative', height: 18 }}>
        {ticks.map((t) => <span key={t.year} style={{ position: 'absolute', left: `${t.pct}%`, transform: 'translateX(-50%)', fontSize: 9, color: 'var(--text-faint)' }}>{t.year}</span>)}
      </div>
      {/* Legend */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 12 }}>
        {visible.map((p, i) => (
          <div key={`l-${i}`} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <div style={{ width: 10, height: 10, borderRadius: 3, background: pColor(p.planet), opacity: p.planet === currentPlanet ? 1 : 0.6 }} />
            <span style={{ fontSize: 11, color: p.planet === currentPlanet ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: p.planet === currentPlanet ? 600 : 400 }}>
              {p.planet} ({Math.round(p.duration_years)}y)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ================================================================
   Current Period Detail
   ================================================================ */

function CurrentPeriodCard({ current, birthNakshatra }: { current: CurrentDasha; birthNakshatra?: string }) {
  const maha = current.mahadasha;
  return (
    <div style={CARD}>
      <h3 style={{ ...HEADING, marginBottom: 4 }}>Current Period</h3>
      {birthNakshatra && <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 16 }}>Birth Nakshatra: {birthNakshatra}</p>}
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginBottom: 20 }}>
        {maha && <PeriodBlock label="Mahadasha" period={maha} />}
        {current.antardasha && <PeriodBlock label="Antardasha" period={current.antardasha} />}
      </div>
      {maha?.progress_percentage != null && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-faint)', marginBottom: 4 }}>
            <span>Mahadasha Progress</span><span>{Math.round(maha.progress_percentage)}%</span>
          </div>
          <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${Math.min(100, maha.progress_percentage)}%`, background: pColor(maha.planet), borderRadius: 3, transition: 'width 0.5s ease-out' }} />
          </div>
        </div>
      )}
      {current.description && <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 16, lineHeight: 1.6, fontStyle: 'italic' }}>{current.description}</p>}
    </div>
  );
}

/* ================================================================
   Antardasha Sub-periods
   ================================================================ */

function AntardashaTimeline({ periods, currentAntar, onPlanetClick }: { periods: DashaPeriod[]; currentAntar?: string; onPlanetClick?: (period: DashaPeriod) => void }) {
  if (!periods.length) return null;
  const fStart = parseDate(periods[0].start_date);
  const fEnd = parseDate(periods[periods.length - 1].end_date);
  if (!fStart || !fEnd) return null;
  const totalMs = fEnd.getTime() - fStart.getTime();
  if (totalMs <= 0) return null;

  return (
    <div style={CARD}>
      <h3 style={HEADING}>Antardasha Sub-periods</h3>
      {/* Bar */}
      <div style={{ position: 'relative', height: 32, borderRadius: 6, overflow: 'hidden', background: 'var(--background)', marginBottom: 12 }}>
        {periods.map((p, i) => {
          const s = parseDate(p.start_date)!.getTime();
          const e = parseDate(p.end_date)!.getTime();
          const left = ((s - fStart.getTime()) / totalMs) * 100;
          const w = ((e - s) / totalMs) * 100;
          const cur = p.planet === currentAntar;
          return (
            <div key={`ad-${i}`} title={`${p.planet}: ${fmtDate(p.start_date)} \u2013 ${fmtDate(p.end_date)}`} style={{
              position: 'absolute', left: `${left}%`, width: `${w}%`, top: 0, bottom: 0,
              background: pColor(p.planet), opacity: cur ? 1 : 0.5,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderLeft: i > 0 ? '1px solid var(--background)' : 'none',
              ...(cur ? { outline: '2px solid var(--gold)', outlineOffset: -2, zIndex: 2 } : {}),
            }}>
              {w > 7 && <span style={{ fontSize: 10, color: '#fff', fontWeight: 600, textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}>{p.planet}</span>}
            </div>
          );
        })}
      </div>
      {/* Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
        {periods.map((p, i) => {
          const cur = p.planet === currentAntar;
          return (
            <div key={`al-${i}`}
              onClick={() => onPlanetClick?.(p)}
              style={{ padding: '10px 12px', borderRadius: 8, border: cur ? '1px solid var(--gold)' : '1px solid var(--border)', background: cur ? 'var(--gold-bg)' : 'transparent', cursor: 'pointer', transition: 'border-color 0.15s ease' }}
              onMouseEnter={(e) => { if (!cur) e.currentTarget.style.borderColor = pColor(p.planet); }}
              onMouseLeave={(e) => { if (!cur) e.currentTarget.style.borderColor = 'var(--border)'; }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                <div style={{ width: 8, height: 8, borderRadius: 2, background: pColor(p.planet) }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: cur ? 'var(--text-primary)' : 'var(--text-secondary)' }}>{p.planet}</span>
                {cur && <span style={{ fontSize: 9, color: 'var(--gold)', fontWeight: 700 }}>CURRENT</span>}
              </div>
              <p style={{ fontSize: 10, color: 'var(--text-faint)' }}>{fmtDate(p.start_date)} \u2013 {fmtDate(p.end_date)}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ================================================================
   Upcoming Transitions
   ================================================================ */

function UpcomingTransitions({ changes, antardashas }: {
  changes?: { date: string; new_dasha: string }[];
  antardashas?: DashaPeriod[];
}) {
  const now = Date.now();
  const items: { date: string; planet: string; level: string }[] = [];

  if (antardashas) {
    for (const ad of antardashas) {
      const s = parseDate(ad.start_date);
      if (s && s.getTime() > now) items.push({ date: ad.start_date, planet: ad.planet, level: 'Antardasha' });
    }
  }
  if (changes) {
    for (const c of changes) items.push({ date: c.date, planet: c.new_dasha, level: 'Mahadasha' });
  }

  items.sort((a, b) => (parseDate(a.date)?.getTime() || 0) - (parseDate(b.date)?.getTime() || 0));
  const top5 = items.slice(0, 5);
  if (!top5.length) return null;

  return (
    <div style={CARD}>
      <h3 style={HEADING}>Upcoming Transitions</h3>
      {top5.map((t, i) => {
        const daysUntil = parseDate(t.date) ? Math.ceil((parseDate(t.date)!.getTime() - now) / 86400000) : 0;
        return (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: i < top5.length - 1 ? '1px solid var(--border)' : 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 10, height: 10, borderRadius: 3, background: pColor(t.planet) }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{t.planet}</span>
              <span style={{ fontSize: 10, color: t.level === 'Mahadasha' ? 'var(--gold)' : 'var(--text-muted)', fontWeight: 500 }}>{t.level}</span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{fmtDate(t.date)}</p>
              <p style={{ fontSize: 10, color: 'var(--text-faint)' }}>in {daysUntil} days</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ================================================================
   Main Page
   ================================================================ */

export default function DashaPage() {
  const [personId, setPersonId] = useState<string | undefined>(undefined);
  const [selectedPeriod, setSelectedPeriod] = useState<DashaPeriod | null>(null);

  const { data: dashaResponse, isLoading, error } = useQuery({
    queryKey: ['dasha-vimshottari', personId],
    queryFn: () => apiClient.get<DashaResponse>(`/api/v1/dasha/vimshottari/${personId}`),
    enabled: !!personId,
  });

  const dasha = dashaResponse?.data || null;
  const currentMahaPlanet = dasha?.current_dasha?.mahadasha?.planet;
  const currentAntarPlanet = dasha?.current_dasha?.antardasha?.planet;
  const currentMahaFull = dasha?.dasha_sequence?.find((d) => d.planet === currentMahaPlanet && d.antardashas);
  const antardashas = currentMahaFull?.antardashas || [];

  const handlePlanetClick = (period: DashaPeriod) => {
    setSelectedPeriod((prev) =>
      prev?.planet === period.planet && prev?.start_date === period.start_date ? null : period
    );
  };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: 'var(--text-primary)', marginBottom: 4 }}>Dasha Timeline</h1>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Vimshottari Dasha periods showing the 120-year planetary time cycles.</p>
      </div>

      {/* Profile selector */}
      <div style={{ maxWidth: 320, marginBottom: 24 }}>
        <label style={LABEL}>Profile</label>
        <ProfileSelector value={personId} onChange={setPersonId} />
      </div>

      {/* Loading */}
      {isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <SkeletonBar width="100%" height={80} />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <SkeletonBar width="100%" height={200} />
            <SkeletonBar width="100%" height={200} />
          </div>
          <SkeletonBar width="100%" height={140} />
          <style>{`@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }`}</style>
        </div>
      )}

      {/* Error */}
      {error && !isLoading && (
        <div style={{ ...CARD, padding: 32, textAlign: 'center' as const }}>
          <p style={{ fontSize: 14, color: '#E5484D', marginBottom: 8 }}>Failed to load dasha data</p>
          <p style={{ fontSize: 12, color: 'var(--text-faint)' }}>{(error as Error).message}</p>
        </div>
      )}

      {/* No profile */}
      {!personId && !isLoading && (
        <div style={{ ...CARD, padding: 48, textAlign: 'center' as const }}>
          <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>Select a profile above to view dasha periods.</p>
        </div>
      )}

      {/* Content */}
      {dasha && !isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, animation: 'fadeIn 0.25s ease-out' }}>
          <MahadashaTimeline periods={dasha.life_timeline || dasha.dasha_sequence || []} currentPlanet={currentMahaPlanet} onPlanetClick={handlePlanetClick} />

          {/* Interpretation Panel */}
          {selectedPeriod && (
            <DashaInterpretationPanel
              planet={selectedPeriod.planet}
              startDate={selectedPeriod.start_date}
              endDate={selectedPeriod.end_date}
              onClose={() => setSelectedPeriod(null)}
            />
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {dasha.current_dasha && <CurrentPeriodCard current={dasha.current_dasha} birthNakshatra={dasha.birth_nakshatra} />}
            <UpcomingTransitions changes={dasha.detailed_periods?.upcoming_changes} antardashas={antardashas} />
          </div>
          {antardashas.length > 0 && <AntardashaTimeline periods={antardashas} currentAntar={currentAntarPlanet} onPlanetClick={handlePlanetClick} />}
          <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }`}</style>
        </div>
      )}
    </div>
  );
}
