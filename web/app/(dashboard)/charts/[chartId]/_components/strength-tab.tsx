'use client';

import { Zap } from 'lucide-react';
import type { ChartDetail } from '@/types';
import { PLANET_ORDER } from './chart-detail-helpers';
import { ComingSoonCard } from './coming-soon-card';

/* ================================================================
   Shared styles (match planets-tab / houses-tab)
   ================================================================ */

const headerStyle: React.CSSProperties = {
  padding: '10px 14px',
  fontSize: 10,
  textTransform: 'uppercase',
  letterSpacing: 0.8,
  color: 'var(--text-faint)',
  fontWeight: 600,
  textAlign: 'left',
  borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap',
};

const cellStyle: React.CSSProperties = {
  padding: '10px 14px',
  fontSize: 12,
  color: 'var(--text-secondary)',
  borderBottom: '1px solid var(--border)',
  fontFamily: 'monospace',
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--text-primary)',
  marginBottom: 12,
  marginTop: 0,
};

const cardStyle: React.CSSProperties = {
  border: '1px solid var(--border)',
  borderRadius: 12,
  background: 'var(--bg-card)',
  overflow: 'hidden',
};

const SIGNS = [
  'Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
  'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis',
];

/* ================================================================
   Sub-components
   ================================================================ */

function ShadbalaSection({ shadbala }: { shadbala: Record<string, Record<string, number>> }) {
  const planets = PLANET_ORDER.filter((p) => shadbala[p]);
  if (planets.length === 0) return null;

  return (
    <div>
      <h3 style={sectionTitleStyle}>Shadbala (Six-fold Strength)</h3>
      <div style={cardStyle}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>Planet</th>
                <th style={headerStyle}>Sthana Bala</th>
                <th style={headerStyle}>Dig Bala</th>
                <th style={headerStyle}>Kala Bala</th>
                <th style={headerStyle}>Chesta Bala</th>
                <th style={headerStyle}>Naisargika Bala</th>
                <th style={headerStyle}>Drik Bala</th>
                <th style={{ ...headerStyle, color: 'var(--gold)', fontWeight: 700 }}>Total</th>
              </tr>
            </thead>
            <tbody>
              {planets.map((name) => {
                const s = shadbala[name];
                return (
                  <tr
                    key={name}
                    style={{ transition: 'background 0.15s' }}
                    onMouseEnter={(e) =>
                      (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')
                    }
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <td
                      style={{
                        ...cellStyle,
                        fontFamily: 'inherit',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        fontSize: 13,
                      }}
                    >
                      {name}
                    </td>
                    <td style={cellStyle}>{s.sthana_bala ?? '\u2014'}</td>
                    <td style={cellStyle}>{s.dig_bala ?? '\u2014'}</td>
                    <td style={cellStyle}>{s.kala_bala ?? '\u2014'}</td>
                    <td style={cellStyle}>{s.chesta_bala ?? '\u2014'}</td>
                    <td style={cellStyle}>{s.naisargika_bala ?? '\u2014'}</td>
                    <td style={cellStyle}>{s.drik_bala ?? '\u2014'}</td>
                    <td
                      style={{
                        ...cellStyle,
                        fontWeight: 700,
                        color: 'var(--gold)',
                      }}
                    >
                      {s.rupas ?? s.total ?? '\u2014'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function AshtakavargaSection({
  ashtakavarga,
  planetSigns,
}: {
  ashtakavarga: Record<string, unknown>;
  planetSigns: Record<string, number>;
}) {
  const bhinnashtak = ashtakavarga.bhinnashtak as
    | Record<string, number[]>
    | undefined;
  const sarva = ashtakavarga.sarva as number[] | undefined;

  if (!bhinnashtak || Object.keys(bhinnashtak).length === 0) return null;

  const planets = PLANET_ORDER.filter((p) => bhinnashtak[p]);

  return (
    <div>
      <h3 style={sectionTitleStyle}>Ashtakavarga (Bindu Points)</h3>
      <div style={cardStyle}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>Planet</th>
                {SIGNS.map((s) => (
                  <th key={s} style={{ ...headerStyle, textAlign: 'center' }}>
                    {s}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {planets.map((name) => {
                const bindus = bhinnashtak[name];
                if (!bindus) return null;
                const occupiedSign = planetSigns[name]; // 0-based sign index
                return (
                  <tr
                    key={name}
                    style={{ transition: 'background 0.15s' }}
                    onMouseEnter={(e) =>
                      (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')
                    }
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <td
                      style={{
                        ...cellStyle,
                        fontFamily: 'inherit',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        fontSize: 13,
                      }}
                    >
                      {name}
                    </td>
                    {SIGNS.map((_, idx) => {
                      const val = bindus[idx] ?? 0;
                      const isOccupied = occupiedSign === idx;
                      return (
                        <td
                          key={idx}
                          style={{
                            ...cellStyle,
                            textAlign: 'center',
                            fontWeight: isOccupied ? 700 : 400,
                            color: isOccupied ? 'var(--gold)' : cellStyle.color,
                            background: isOccupied
                              ? 'color-mix(in srgb, var(--gold) 8%, transparent)'
                              : undefined,
                          }}
                        >
                          {val}
                          {isOccupied ? '*' : ''}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
              {sarva && (
                <tr style={{ background: 'color-mix(in srgb, var(--gold) 4%, transparent)' }}>
                  <td
                    style={{
                      ...cellStyle,
                      fontFamily: 'inherit',
                      fontWeight: 700,
                      color: 'var(--gold)',
                      fontSize: 13,
                    }}
                  >
                    Sarva
                  </td>
                  {SIGNS.map((_, idx) => (
                    <td
                      key={idx}
                      style={{
                        ...cellStyle,
                        textAlign: 'center',
                        fontWeight: 700,
                        color: 'var(--gold)',
                      }}
                    >
                      {sarva[idx] ?? 0}
                    </td>
                  ))}
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function BhavaBalaSection({ bhavaBala }: { bhavaBala: Record<string, Record<string, number>> }) {
  const houseKeys = Object.keys(bhavaBala)
    .map(Number)
    .filter((n) => !isNaN(n))
    .sort((a, b) => a - b);
  if (houseKeys.length === 0) return null;

  return (
    <div>
      <h3 style={sectionTitleStyle}>Bhava Bala (House Strength)</h3>
      <div style={cardStyle}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={headerStyle}>House</th>
                <th style={headerStyle}>Dikbala</th>
                <th style={headerStyle}>Drishtibala</th>
                <th style={headerStyle}>Adipati</th>
                <th style={{ ...headerStyle, color: 'var(--gold)', fontWeight: 700 }}>Total</th>
              </tr>
            </thead>
            <tbody>
              {houseKeys.map((num) => {
                const h = bhavaBala[String(num)];
                return (
                  <tr
                    key={num}
                    style={{ transition: 'background 0.15s' }}
                    onMouseEnter={(e) =>
                      (e.currentTarget.style.background = 'var(--bg-card-hover, var(--border))')
                    }
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <td
                      style={{
                        ...cellStyle,
                        fontFamily: 'inherit',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        fontSize: 13,
                      }}
                    >
                      {num}
                    </td>
                    <td style={cellStyle}>{h.dikbala ?? h.dig_bala ?? '\u2014'}</td>
                    <td style={cellStyle}>{h.drishtibala ?? h.drishti_bala ?? '\u2014'}</td>
                    <td style={cellStyle}>{h.adipati ?? h.lord_strength ?? '\u2014'}</td>
                    <td style={{ ...cellStyle, fontWeight: 700, color: 'var(--gold)' }}>
                      {h.total ?? '\u2014'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   Main component
   ================================================================ */

export function StrengthTab({ chart }: { chart: ChartDetail }) {
  const chartData = chart.chart_data as Record<string, unknown> | undefined;
  const strengths = chartData?.strengths as Record<string, unknown> | undefined;
  const ashtakavarga = chartData?.ashtakavarga as Record<string, unknown> | undefined;

  const shadbala = (strengths?.shadbala ?? strengths) as
    | Record<string, Record<string, number>>
    | undefined;
  const bhavaBala = strengths?.bhava_bala as
    | Record<string, Record<string, number>>
    | undefined;

  const hasShadbala = shadbala && Object.keys(shadbala).some((k) => PLANET_ORDER.includes(k));
  const hasBhavaBala = bhavaBala && Object.keys(bhavaBala).length > 0;
  const hasAshtakavarga =
    ashtakavarga &&
    (ashtakavarga.bhinnashtak as Record<string, unknown> | undefined) &&
    Object.keys(ashtakavarga.bhinnashtak as Record<string, unknown>).length > 0;

  if (!hasShadbala && !hasBhavaBala && !hasAshtakavarga) {
    return (
      <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
        <ComingSoonCard
          icon={<Zap style={{ width: 20, height: 20, color: 'var(--blue)' }} />}
          bgColor="var(--blue-bg)"
          message="Strength data not available for this chart. Recalculate with the latest engine to include strength analysis."
        />
      </div>
    );
  }

  // Build a quick lookup of planet -> sign index (0-based) for ashtakavarga highlighting
  const planets = chartData?.planets as Record<string, { sign?: string }> | undefined;
  const SIGN_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
  ];
  const planetSigns: Record<string, number> = {};
  if (planets) {
    for (const [name, data] of Object.entries(planets)) {
      if (data?.sign) {
        const idx = SIGN_NAMES.indexOf(data.sign);
        if (idx !== -1) planetSigns[name] = idx;
      }
    }
  }

  return (
    <div style={{ animation: 'fadeIn 0.25s ease-out', display: 'flex', flexDirection: 'column', gap: 28 }}>
      {hasShadbala && <ShadbalaSection shadbala={shadbala!} />}
      {hasAshtakavarga && (
        <AshtakavargaSection
          ashtakavarga={ashtakavarga!}
          planetSigns={planetSigns}
        />
      )}
      {hasBhavaBala && <BhavaBalaSection bhavaBala={bhavaBala!} />}
    </div>
  );
}
