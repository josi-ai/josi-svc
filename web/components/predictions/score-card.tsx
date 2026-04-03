'use client';

/* ==========================================================================
   Overall Score Card — large circular ring + summary text
   ========================================================================== */

export function scoreColor(score: number): string {
  if (score > 7) return '#22c55e';
  if (score >= 5) return '#eab308';
  return '#ef4444';
}

export function scoreBg(score: number): string {
  if (score > 7) return 'rgba(34,197,94,0.12)';
  if (score >= 5) return 'rgba(234,179,8,0.12)';
  return 'rgba(239,68,68,0.12)';
}

export function OverallScoreCard({ score, summary }: { score: number; summary: string }) {
  const color = scoreColor(score);
  const circumference = 2 * Math.PI * 54;
  const dashOffset = circumference - (score / 10) * circumference;

  return (
    <div
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 16,
        padding: 28,
        display: 'flex',
        gap: 28,
        alignItems: 'center',
        flexWrap: 'wrap',
      }}
    >
      {/* Circular score ring */}
      <div style={{ position: 'relative', width: 128, height: 128, flexShrink: 0 }}>
        <svg width="128" height="128" viewBox="0 0 128 128">
          <circle cx="64" cy="64" r="54" fill="none" stroke="var(--border)" strokeWidth="8" />
          <circle
            cx="64"
            cy="64"
            r="54"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            transform="rotate(-90 64 64)"
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <span style={{ fontSize: 36, fontWeight: 700, color, lineHeight: 1 }}>
            {score.toFixed(1)}
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>/ 10</span>
        </div>
      </div>

      {/* Summary text */}
      <div style={{ flex: 1, minWidth: 200 }}>
        <h3
          style={{
            fontSize: 18,
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: 8,
          }}
        >
          Overall Outlook
        </h3>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {summary}
        </p>
      </div>
    </div>
  );
}
