'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { Heart, Shield, Star, AlertTriangle, CheckCircle, XCircle, ChevronDown } from 'lucide-react';

/* ================================================================
   Types
   ================================================================ */

interface GunaResult {
  points: number;
  max_points: number;
  description?: string;
  [key: string]: unknown;
}

interface ManglikStatus {
  person1: boolean;
  person2: boolean;
  manglik_match: boolean;
}

interface CompatibilityData {
  person1: { id: string; name: string };
  person2: { id: string; name: string };
  total_score: number;
  max_score: number;
  compatibility_percentage: number;
  gunas: Record<string, GunaResult>;
  manglik_status: ManglikStatus;
  recommendations: string[];
  detailed_analysis: string;
  compatibility_level: string;
  doshas: unknown;
}

/* ================================================================
   Constants
   ================================================================ */

interface GunaDetail {
  label: string;
  description: string;
  measures: string;
  lowScore: string;
  highScore: string;
}

const GUNA_INFO: Record<string, GunaDetail> = {
  varna: {
    label: 'Varna',
    description: 'Spiritual compatibility and ego level',
    measures: 'Varna reflects the spiritual and intellectual compatibility between partners. It classifies individuals into four categories (Brahmin, Kshatriya, Vaishya, Shudra) based on their Moon sign, representing their innate spiritual development and ego alignment.',
    lowScore: 'A low Varna score suggests differing spiritual wavelengths. Partners may struggle to understand each other\'s core values, life priorities, and approach to personal growth. Mutual respect and conscious effort to appreciate different perspectives are key.',
    highScore: 'A high Varna score indicates natural alignment in spiritual outlook and ego compatibility. Partners share similar values around duty, purpose, and self-development, creating an effortless understanding at the deepest level.',
  },
  vashya: {
    label: 'Vashya',
    description: 'Mutual attraction and dominance',
    measures: 'Vashya evaluates the power dynamics and mutual magnetic attraction between partners. It measures who holds influence in the relationship and whether the dominance balance is harmonious, assessing natural affinity and willingness to accommodate each other.',
    lowScore: 'A low Vashya score can indicate power struggles or a lack of natural attraction. One partner may feel dominated or unheard. Conscious balance of give-and-take is essential to maintain harmony.',
    highScore: 'A high Vashya score shows strong mutual attraction and a healthy balance of influence. Both partners naturally gravitate toward each other and willingly accommodate, creating a relationship of equals.',
  },
  tara: {
    label: 'Tara',
    description: 'Birth star compatibility and destiny',
    measures: 'Tara (Dina) compatibility examines the destiny alignment between two birth stars (nakshatras). It calculates the wellness and health implications of the pairing, revealing whether the cosmic rhythms of both individuals are in sync.',
    lowScore: 'A low Tara score warns of potential health concerns or a sense of fatigue in the relationship. The partners\' cosmic rhythms may clash, leading to periodic friction or a general feeling of unease together.',
    highScore: 'A high Tara score indicates excellent destiny alignment. Partners feel energized and uplifted in each other\'s presence. Their birth stars create a harmonious cosmic rhythm that supports mutual well-being.',
  },
  yoni: {
    label: 'Yoni',
    description: 'Physical and sexual compatibility',
    measures: 'Yoni kuta assesses physical and sexual compatibility by mapping each nakshatra to an animal nature (14 animal types). It evaluates the instinctive physical connection, intimacy potential, and sexual harmony between partners.',
    lowScore: 'A low Yoni score suggests potential mismatches in physical needs and intimacy styles. Partners may have different expectations around closeness, affection, and sexual expression. Open communication about needs is important.',
    highScore: 'A high Yoni score indicates excellent physical chemistry and natural intimacy. Partners share compatible instinctive drives, leading to a deeply satisfying physical connection and mutual comfort.',
  },
  graha_maitri: {
    label: 'Graha Maitri',
    description: 'Mental wavelength and friendship',
    measures: 'Graha Maitri (planetary friendship) measures the mental and intellectual compatibility between partners. It compares the lords of each person\'s Moon sign to determine if their thought patterns, communication styles, and decision-making approaches align.',
    lowScore: 'A low Graha Maitri score indicates different mental wavelengths. Partners may frequently misunderstand each other, disagree on decisions, or feel intellectually disconnected. Patience and active listening become crucial.',
    highScore: 'A high Graha Maitri score shows excellent mental rapport. Partners think alike, communicate effortlessly, and share similar approaches to problem-solving. This creates a strong friendship foundation for the marriage.',
  },
  gana: {
    label: 'Gana',
    description: 'Temperament and nature match',
    measures: 'Gana kuta classifies temperaments into three types: Deva (divine/gentle), Manushya (human/balanced), and Rakshasa (demonic/intense). It evaluates whether the fundamental natures and behavioral tendencies of two people can coexist harmoniously.',
    lowScore: 'A low Gana score suggests clashing temperaments. One partner may find the other too aggressive or too passive. A Deva-Rakshasa pairing, for instance, may experience frequent conflicts over lifestyle and social behavior.',
    highScore: 'A high Gana score indicates matching temperaments. Partners share similar social dispositions and behavioral patterns, reducing friction in daily interactions and creating a natural comfort zone.',
  },
  bhakoot: {
    label: 'Bhakoot',
    description: 'Love, emotional bond and health',
    measures: 'Bhakoot (Rashyadhipati) is one of the most important gunas, carrying 7 points. It examines the Moon sign positions of both partners to evaluate emotional compatibility, mutual love potential, financial prosperity, and the overall health of the relationship.',
    lowScore: 'A low Bhakoot score is a significant concern. It can indicate emotional distance, financial strain, or health issues in the marriage. Certain sign combinations (like 6-8 or 2-12 positions) are considered particularly challenging and may require remedial measures.',
    highScore: 'A high Bhakoot score is very auspicious. It indicates deep emotional bonding, financial harmony, and mutual love that grows over time. Partners naturally support each other\'s emotional and material well-being.',
  },
  nadi: {
    label: 'Nadi',
    description: 'Genetic compatibility and health',
    measures: 'Nadi is the most critical guna, carrying the maximum 8 points. It classifies individuals into Aadi (Vata), Madhya (Pitta), or Antya (Kapha) based on their nakshatra. It assesses genetic compatibility and the health prospects of offspring, making it the single most weighted factor in Ashtakoota matching.',
    lowScore: 'A zero Nadi score (Nadi Dosha) is the most serious defect in guna matching. It warns of potential health issues for offspring and fundamental physiological incompatibility. Traditional astrology considers this a significant obstacle, though specific nakshatra exceptions (Nadi Dosha cancellation) may apply.',
    highScore: 'A full 8-point Nadi score indicates excellent genetic compatibility. Partners belong to different Nadi types, ensuring complementary physiological constitutions and healthy prospects for the next generation.',
  },
};

/* ================================================================
   Helpers
   ================================================================ */

function scoreColor(score: number): string {
  if (score >= 25) return 'var(--green)';
  if (score >= 18) return 'var(--gold)';
  return 'var(--red)';
}

function scoreLabel(score: number): string {
  if (score >= 32) return 'Excellent Match';
  if (score >= 25) return 'Very Good Match';
  if (score >= 18) return 'Good Match';
  return 'Needs Attention';
}

function scoreBg(score: number): string {
  if (score >= 25) return 'var(--green-bg)';
  if (score >= 18) return 'var(--gold-bg)';
  return 'var(--red-bg)';
}

/* ================================================================
   Sub-components
   ================================================================ */

function ScoreGauge({ score, maxScore }: { score: number; maxScore: number }) {
  const pct = (score / maxScore) * 100;
  const color = scoreColor(score);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
      <div style={{ position: 'relative', width: 180, height: 180 }}>
        <svg width="180" height="180" viewBox="0 0 180 180">
          <circle cx="90" cy="90" r={radius} fill="none" stroke="var(--border)" strokeWidth="10" />
          <circle
            cx="90" cy="90" r={radius}
            fill="none" stroke={color} strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            transform="rotate(-90 90 90)"
            style={{ transition: 'stroke-dashoffset 0.8s ease-out' }}
          />
        </svg>
        <div
          style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
          }}
        >
          <span style={{ fontSize: 36, fontWeight: 800, color, lineHeight: 1 }}>
            {score}
          </span>
          <span style={{ fontSize: 14, color: 'var(--text-faint)', marginTop: 2 }}>
            / {maxScore}
          </span>
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <p style={{ fontSize: 16, fontWeight: 700, color }}>{scoreLabel(score)}</p>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
          {Math.round(pct)}% compatibility
        </p>
      </div>
    </div>
  );
}

function GunaCard({ gunaKey, guna, person1Name, person2Name }: {
  gunaKey: string;
  guna: GunaResult;
  person1Name: string;
  person2Name: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const info = GUNA_INFO[gunaKey];
  if (!info) return null;
  const pct = guna.max_points > 0 ? (guna.points / guna.max_points) * 100 : 0;
  const barColor = pct >= 75 ? 'var(--green)' : pct >= 50 ? 'var(--gold)' : 'var(--red)';
  const isHigh = pct >= 50;

  return (
    <div
      style={{
        border: `1px solid ${expanded ? barColor : 'var(--border)'}`,
        borderRadius: 12,
        background: 'var(--card)',
        padding: 16,
        cursor: 'pointer',
        transition: 'border-color 0.2s, box-shadow 0.2s',
        boxShadow: expanded ? `0 0 0 1px ${barColor}20` : 'none',
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
          {info.label}
        </h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: barColor, fontFamily: 'monospace' }}>
            {guna.points}/{guna.max_points}
          </span>
          <ChevronDown
            style={{
              width: 14, height: 14, color: 'var(--text-faint)',
              transition: 'transform 0.2s',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            }}
          />
        </div>
      </div>
      <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden', marginBottom: 8 }}>
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            background: barColor,
            borderRadius: 3,
            transition: 'width 0.5s ease-out',
          }}
        />
      </div>
      <p style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>
        {info.description}
      </p>

      {/* Expanded detail */}
      {expanded && (
        <div
          style={{
            marginTop: 14,
            paddingTop: 14,
            borderTop: '1px solid var(--border)',
            animation: 'fadeIn 0.2s ease-out',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* What this guna measures */}
          <div style={{ marginBottom: 12 }}>
            <p style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-faint)', marginBottom: 4 }}>
              What this measures
            </p>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              {info.measures}
            </p>
          </div>

          {/* How the two profiles compare */}
          <div style={{ marginBottom: 12 }}>
            <p style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-faint)', marginBottom: 4 }}>
              {person1Name} & {person2Name}
            </p>
            <div
              style={{
                padding: 10,
                borderRadius: 8,
                background: isHigh ? 'var(--green-bg)' : 'var(--red-bg)',
                fontSize: 12,
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
              }}
            >
              {guna.description || (isHigh
                ? `${person1Name} and ${person2Name} show strong ${info.label.toLowerCase()} compatibility, scoring ${guna.points} out of ${guna.max_points} points.`
                : `${person1Name} and ${person2Name} have lower ${info.label.toLowerCase()} compatibility at ${guna.points} out of ${guna.max_points} points. Consider the remedial suggestions below.`
              )}
            </div>
          </div>

          {/* Score interpretation */}
          <div>
            <p style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-faint)', marginBottom: 4 }}>
              {isHigh ? 'High score means' : 'Low score means'}
            </p>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              {isHigh ? info.highScore : info.lowScore}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function ManglikSection({ status, person1Name, person2Name }: {
  status: ManglikStatus;
  person1Name: string;
  person2Name: string;
}) {
  const match = status.manglik_match;

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 12,
        background: 'var(--card)',
        padding: 20,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <div
          style={{
            width: 32, height: 32, borderRadius: 10,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: match ? 'var(--green-bg)' : 'var(--red-bg)',
          }}
        >
          {match
            ? <CheckCircle style={{ width: 16, height: 16, color: 'var(--green)' }} />
            : <AlertTriangle style={{ width: 16, height: 16, color: 'var(--red)' }} />}
        </div>
        <div>
          <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
            Manglik Dosha
          </h4>
          <p style={{ fontSize: 11, color: match ? 'var(--green)' : 'var(--red)', fontWeight: 500 }}>
            {match ? 'Compatible' : 'Mismatch detected'}
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <ManglikPerson name={person1Name} isManglik={status.person1} />
        <ManglikPerson name={person2Name} isManglik={status.person2} />
      </div>

      {!match && (
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 14, lineHeight: 1.5 }}>
          One partner is Manglik while the other is not. Traditional Vedic astrology recommends
          specific remedies such as Kumbh Vivah or matching with another Manglik partner.
        </p>
      )}
    </div>
  );
}

function ManglikPerson({ name, isManglik }: { name: string; isManglik: boolean }) {
  return (
    <div
      style={{
        padding: 12,
        borderRadius: 8,
        background: isManglik ? 'var(--red-bg)' : 'var(--green-bg)',
        display: 'flex', alignItems: 'center', gap: 8,
      }}
    >
      {isManglik
        ? <XCircle style={{ width: 14, height: 14, color: 'var(--red)', flexShrink: 0 }} />
        : <CheckCircle style={{ width: 14, height: 14, color: 'var(--green)', flexShrink: 0 }} />}
      <div>
        <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>{name}</p>
        <p style={{ fontSize: 11, color: isManglik ? 'var(--red)' : 'var(--green)' }}>
          {isManglik ? 'Manglik' : 'Non-Manglik'}
        </p>
      </div>
    </div>
  );
}

function SkeletonGauge() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
      <div
        style={{
          width: 180, height: 180, borderRadius: '50%',
          background: 'var(--border)', opacity: 0.4,
          animation: 'pulse 2s infinite',
        }}
      />
      <div style={{ width: 120, height: 16, borderRadius: 8, background: 'var(--border)', opacity: 0.4 }} />
    </div>
  );
}

function SkeletonCards() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          style={{
            height: 100, borderRadius: 12,
            background: 'var(--border)', opacity: 0.3,
            animation: 'pulse 2s infinite',
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
    </div>
  );
}

/* ================================================================
   Main Page
   ================================================================ */

export default function CompatibilityPage() {
  const [person1Id, setPerson1Id] = useState<string>('');
  const [person2Id, setPerson2Id] = useState<string>('');

  const {
    mutate: calculate,
    data: response,
    isPending,
    error,
    reset,
  } = useMutation({
    mutationFn: () =>
      apiClient.post<CompatibilityData>(
        `/api/v1/compatibility/calculate?person1_id=${person1Id}&person2_id=${person2Id}`
      ),
  });

  const result = response?.data;
  const canCalculate = person1Id && person2Id && person1Id !== person2Id && !isPending;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 4px' }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <div
            style={{
              width: 36, height: 36, borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'var(--gold-bg)',
            }}
          >
            <Heart style={{ width: 18, height: 18, color: 'var(--gold)' }} />
          </div>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              Compatibility
            </h1>
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Ashtakoota Guna Matching
            </p>
          </div>
        </div>
      </div>

      {/* Profile Pair Selector */}
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 12,
          background: 'var(--card)',
          padding: 20,
          marginBottom: 24,
        }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <div>
            <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 6 }}>
              Person 1
            </label>
            <ProfileSelector
              value={person1Id}
              onChange={(id) => { setPerson1Id(id); reset(); }}
              showDefault={false}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 6 }}>
              Person 2
            </label>
            <ProfileSelector
              value={person2Id}
              onChange={(id) => { setPerson2Id(id); reset(); }}
              showDefault={false}
            />
          </div>
        </div>

        {person1Id && person2Id && person1Id === person2Id && (
          <p style={{ fontSize: 12, color: 'var(--red)', marginBottom: 12 }}>
            Please select two different profiles.
          </p>
        )}

        <button
          disabled={!canCalculate}
          onClick={() => calculate()}
          style={{
            width: '100%',
            padding: '12px 0',
            borderRadius: 10,
            border: 'none',
            background: canCalculate ? 'var(--gold)' : 'var(--border)',
            color: canCalculate ? '#fff' : 'var(--text-faint)',
            fontSize: 14,
            fontWeight: 700,
            cursor: canCalculate ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s',
          }}
        >
          {isPending ? 'Calculating...' : 'Calculate Compatibility'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div
          style={{
            border: '1px solid var(--red)',
            borderRadius: 12,
            background: 'var(--red-bg)',
            padding: 16,
            marginBottom: 24,
            display: 'flex', alignItems: 'center', gap: 10,
          }}
        >
          <AlertTriangle style={{ width: 16, height: 16, color: 'var(--red)', flexShrink: 0 }} />
          <p style={{ fontSize: 13, color: 'var(--red)' }}>
            {(error as Error).message || 'Failed to calculate compatibility'}
          </p>
        </div>
      )}

      {/* Loading */}
      {isPending && (
        <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 32 }}>
            <SkeletonGauge />
          </div>
          <SkeletonCards />
        </div>
      )}

      {/* Results */}
      {result && !isPending && (
        <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
          {/* Score Display */}
          <div
            style={{
              border: '1px solid var(--border)',
              borderRadius: 12,
              background: 'var(--card)',
              padding: 28,
              marginBottom: 24,
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <ScoreGauge score={result.total_score} maxScore={result.max_score} />
          </div>

          {/* 8 Guna Breakdown */}
          <SectionHeading>Guna Breakdown</SectionHeading>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14, marginBottom: 28 }}>
            {Object.entries(GUNA_INFO).map(([key]) => {
              const guna = result.gunas[key];
              if (!guna) return null;
              return (
                <GunaCard
                  key={key}
                  gunaKey={key}
                  guna={guna}
                  person1Name={result.person1.name}
                  person2Name={result.person2.name}
                />
              );
            })}
          </div>

          {/* Manglik Dosha */}
          <SectionHeading>Manglik Dosha Analysis</SectionHeading>
          <div style={{ marginBottom: 28 }}>
            <ManglikSection
              status={result.manglik_status}
              person1Name={result.person1.name}
              person2Name={result.person2.name}
            />
          </div>

          {/* Recommendations */}
          {result.recommendations && Array.isArray(result.recommendations) && result.recommendations.length > 0 && (
            <>
              <SectionHeading>Recommendations</SectionHeading>
              <div
                style={{
                  border: '1px solid var(--border)',
                  borderRadius: 12,
                  background: 'var(--card)',
                  padding: 20,
                  marginBottom: 28,
                }}
              >
                {result.recommendations.map((rec: string, i: number) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: i < result.recommendations.length - 1 ? 10 : 0 }}>
                    <Star style={{ width: 12, height: 12, color: 'var(--gold)', marginTop: 2, flexShrink: 0 }} />
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{rec}</p>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Detailed Analysis */}
          {result.detailed_analysis && (
            <>
              <SectionHeading>Overall Assessment</SectionHeading>
              <div
                style={{
                  border: '1px solid var(--border)',
                  borderRadius: 12,
                  background: scoreBg(result.total_score),
                  padding: 20,
                  marginBottom: 28,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                  <Shield style={{ width: 16, height: 16, color: scoreColor(result.total_score) }} />
                  <span style={{ fontSize: 14, fontWeight: 700, color: scoreColor(result.total_score) }}>
                    {result.compatibility_level}
                  </span>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {typeof result.detailed_analysis === 'string'
                    ? result.detailed_analysis
                    : JSON.stringify(result.detailed_analysis)}
                </p>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

/* ================================================================
   Shared sub-component
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
