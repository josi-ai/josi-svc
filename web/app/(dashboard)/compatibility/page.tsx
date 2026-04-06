'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ProfileSelector } from '@/components/ui/profile-selector';
import { Heart, Shield, Star, AlertTriangle } from 'lucide-react';

import type { CompatibilityData } from './_components/compatibility-types';
import { GUNA_INFO } from './_components/compatibility-types';
import { scoreColor, scoreBg } from './_components/compatibility-helpers';
import { ScoreGauge } from './_components/score-gauge';
import { GunaCard } from './_components/guna-card';
import { ManglikSection } from './_components/manglik-section';
import { SectionHeading, SkeletonGauge, SkeletonCards } from './_components/compatibility-states';

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
            color: canCalculate ? 'var(--primary-foreground)' : 'var(--text-faint)',
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
