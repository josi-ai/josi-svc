'use client';

import { RemedyCard, TIER_CONFIG, costTierKey, type RemedyCatalog, type Recommendation } from './remedy-card';

export function TierSection({
  tierKey,
  remedies,
  progressMap,
  onAction,
  actioningKey,
}: {
  tierKey: string;
  remedies: { remedy: RemedyCatalog; recommendation?: Recommendation }[];
  progressMap: Map<string, string>;
  onAction: (remedyName: string, remedyType: string, status: string) => void;
  actioningKey: string | null;
}) {
  const tier = TIER_CONFIG[tierKey];
  if (!remedies.length) return null;

  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <div style={{ width: 4, height: 20, borderRadius: 2, background: tier.color }} />
        <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
          {tier.label}
        </h2>
        <span
          style={{
            fontSize: 12,
            color: 'var(--text-muted)',
            background: 'var(--card)',
            border: '1px solid var(--border)',
            borderRadius: 20,
            padding: '2px 10px',
          }}
        >
          {remedies.length}
        </span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {remedies.map(({ remedy, recommendation }) => {
          const key = `${remedy.type_name || 'unknown'}::${remedy.name}`;
          const status = progressMap.get(key) || 'not_started';
          return (
            <RemedyCard
              key={remedy.remedy_id || key}
              remedy={remedy}
              recommendation={recommendation}
              progressStatus={status}
              onAction={(newStatus) => onAction(remedy.name, remedy.type_name || 'unknown', newStatus)}
              isActioning={actioningKey === key}
            />
          );
        })}
      </div>
    </div>
  );
}
