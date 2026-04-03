'use client';

import { useState } from 'react';
import {
  BookOpen,
  Gem,
  HandHeart,
  Flame,
  MapPin,
  Sparkles,
  Pill,
  Check,
  Play,
  SkipForward,
  Shield,
  Clock,
  ChevronDown,
  ChevronUp,
  type LucideIcon,
} from 'lucide-react';

/* ==========================================================================
   Types
   ========================================================================== */

export interface RemedyCatalog {
  remedy_id: string;
  name: string;
  type_id: number | null;
  type_name: string | null;
  tradition_name: string | null;
  planet: string | null;
  dosha_type_name: string | null;
  description: Record<string, string>;
  instructions: Record<string, string>;
  benefits: Record<string, string>;
  precautions: Record<string, string>;
  duration_days: number | null;
  frequency: string | null;
  best_time: string | null;
  materials_needed: string[];
  effectiveness_rating: number;
  difficulty_level: number;
  cost_level: number;
  mantra_text: string | null;
}

export interface Recommendation {
  recommendation_id: string;
  remedy: RemedyCatalog;
  relevance_score: number;
  priority_level: number;
  issue_description: string;
  expected_timeline: string | null;
  personalized_instructions: string | null;
  confidence_score: number | null;
}

/* ==========================================================================
   Constants
   ========================================================================== */

const REMEDY_TYPE_ICONS: Record<string, LucideIcon> = {
  Mantra: BookOpen,
  Gemstone: Gem,
  Charity: HandHeart,
  Ritual: Flame,
  Pilgrimage: MapPin,
  Meditation: Sparkles,
  Prayer: Sparkles,
  Fasting: Clock,
  Yantra: Shield,
  Lifestyle: Sparkles,
};

export const TIER_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  free: { label: 'Free', color: '#22c55e', bg: 'rgba(34,197,94,0.1)' },
  low: { label: 'Low Cost', color: '#3b82f6', bg: 'rgba(59,130,246,0.1)' },
  medium: { label: 'Medium', color: 'var(--gold)', bg: 'rgba(212,175,55,0.1)' },
  premium: { label: 'Premium', color: '#a855f7', bg: 'rgba(168,85,247,0.1)' },
};

const DIFFICULTY_LABELS: Record<number, string> = { 1: 'Easy', 2: 'Easy', 3: 'Moderate', 4: 'Advanced', 5: 'Advanced' };
const COST_LABELS: Record<number, string> = { 1: 'Free', 2: '~100-500', 3: '~1K-5K', 4: '~5K-15K', 5: '~15K+' };

export function costTierKey(level: number): string {
  if (level <= 1) return 'free';
  if (level <= 2) return 'low';
  if (level <= 3) return 'medium';
  return 'premium';
}

/* ==========================================================================
   Component
   ========================================================================== */

export function RemedyCard({
  remedy,
  recommendation,
  progressStatus,
  onAction,
  isActioning,
}: {
  remedy: RemedyCatalog;
  recommendation?: Recommendation;
  progressStatus: string;
  onAction: (status: string) => void;
  isActioning: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const Icon = REMEDY_TYPE_ICONS[remedy.type_name || ''] || Pill;
  const tierKey = costTierKey(remedy.cost_level);
  const tier = TIER_CONFIG[tierKey];
  const diffLabel = DIFFICULTY_LABELS[remedy.difficulty_level] || 'Moderate';
  const costLabel = COST_LABELS[remedy.cost_level] || 'Free';
  const description = remedy.description?.en || '';
  const instructions = remedy.instructions?.en || '';
  const benefits = remedy.benefits?.en || '';
  const issueDesc = recommendation?.issue_description || '';
  const personalizedInstr = recommendation?.personalized_instructions || '';

  const statusBadge =
    progressStatus === 'in_progress'
      ? { text: 'In Progress', bg: 'rgba(59,130,246,0.12)', color: '#3b82f6' }
      : progressStatus === 'completed'
        ? { text: 'Completed', bg: 'rgba(34,197,94,0.12)', color: '#22c55e' }
        : progressStatus === 'skipped'
          ? { text: 'Skipped', bg: 'rgba(107,114,128,0.12)', color: '#6b7280' }
          : null;

  const isCompleted = progressStatus === 'completed';
  const isSkipped = progressStatus === 'skipped';

  return (
    <div style={{
      background: 'var(--card)',
      border: `1px solid ${isCompleted ? 'rgba(34,197,94,0.3)' : 'var(--border)'}`,
      borderRadius: 12,
      overflow: 'hidden',
      position: 'relative',
      opacity: isSkipped ? 0.6 : 1,
      transition: 'opacity 0.2s, border-color 0.2s',
    }}>
      {/* Completed checkmark overlay */}
      {isCompleted && (
        <div style={{
          position: 'absolute', top: 12, right: 12, zIndex: 2,
          width: 28, height: 28, borderRadius: '50%',
          background: '#22c55e', display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 2px 6px rgba(34,197,94,0.3)',
        }}>
          <Check size={16} style={{ color: '#fff' }} />
        </div>
      )}
      {/* Header */}
      <div style={{ padding: '16px 18px', cursor: 'pointer' }} onClick={() => setExpanded((e) => !e)}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <div
            style={{
              width: 40, height: 40, borderRadius: 10,
              background: isCompleted ? 'rgba(34,197,94,0.1)' : tier.bg,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}
          >
            <Icon size={20} style={{ color: isCompleted ? '#22c55e' : tier.color }} />
          </div>

          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <h4 style={{
                fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', margin: 0,
                textDecoration: isSkipped ? 'line-through' : 'none',
                textDecorationColor: 'var(--text-muted)',
              }}>
                {remedy.name}
              </h4>
              {remedy.type_name && (
                <span style={{ fontSize: 11, fontWeight: 500, padding: '2px 8px', borderRadius: 20, background: tier.bg, color: tier.color }}>
                  {remedy.type_name}
                </span>
              )}
              {statusBadge && (
                <span style={{ fontSize: 11, fontWeight: 500, padding: '2px 8px', borderRadius: 20, background: statusBadge.bg, color: statusBadge.color }}>
                  {statusBadge.text}
                </span>
              )}
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 6, flexWrap: 'wrap' }}>
              {remedy.best_time && (
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  <Clock size={11} style={{ marginRight: 3, verticalAlign: -1 }} />
                  {remedy.best_time}
                </span>
              )}
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{diffLabel}</span>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{costLabel}</span>
              {remedy.planet && <span style={{ fontSize: 12, color: 'var(--gold)' }}>{remedy.planet}</span>}
            </div>
            {issueDesc && (
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: '6px 0 0', lineHeight: 1.4 }}>
                {issueDesc}
              </p>
            )}
          </div>

          <div style={{ flexShrink: 0, color: 'var(--text-muted)', paddingTop: 4 }}>
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </div>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div style={{ borderTop: '1px solid var(--border)', padding: '14px 18px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {description && (
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>{description}</p>
          )}
          {personalizedInstr && (
            <div style={{ fontSize: 12, background: 'rgba(99,102,241,0.06)', borderRadius: 8, padding: '8px 12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              <strong style={{ color: 'var(--text-primary)' }}>Personalized:</strong> {personalizedInstr}
            </div>
          )}
          {instructions && (
            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
              <strong style={{ color: 'var(--text-secondary)' }}>Instructions:</strong> {instructions}
            </div>
          )}
          {benefits && (
            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>
              <strong style={{ color: 'var(--text-secondary)' }}>Benefits:</strong> {benefits}
            </div>
          )}
          {remedy.mantra_text && (
            <div style={{ fontSize: 13, fontFamily: 'serif', color: 'var(--gold)', background: 'rgba(212,175,55,0.06)', borderRadius: 8, padding: '10px 14px', fontStyle: 'italic' }}>
              {remedy.mantra_text}
            </div>
          )}
          {remedy.frequency && (
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              <strong style={{ color: 'var(--text-secondary)' }}>Frequency:</strong> {remedy.frequency}
              {remedy.duration_days ? ` for ${remedy.duration_days} days` : ''}
            </div>
          )}

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
            {progressStatus !== 'in_progress' && progressStatus !== 'completed' && (
              <button
                onClick={() => onAction('in_progress')}
                disabled={isActioning}
                style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px', fontSize: 12, fontWeight: 600, color: '#fff', background: '#3b82f6', border: 'none', borderRadius: 8, cursor: isActioning ? 'wait' : 'pointer', opacity: isActioning ? 0.6 : 1 }}
              >
                <Play size={13} /> Start
              </button>
            )}
            {progressStatus === 'in_progress' && (
              <button
                onClick={() => onAction('completed')}
                disabled={isActioning}
                style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px', fontSize: 12, fontWeight: 600, color: '#fff', background: '#22c55e', border: 'none', borderRadius: 8, cursor: isActioning ? 'wait' : 'pointer', opacity: isActioning ? 0.6 : 1 }}
              >
                <Check size={13} /> Complete
              </button>
            )}
            {progressStatus !== 'skipped' && progressStatus !== 'completed' && (
              <button
                onClick={() => onAction('skipped')}
                disabled={isActioning}
                style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', background: 'transparent', border: '1px solid var(--border)', borderRadius: 8, cursor: isActioning ? 'wait' : 'pointer', opacity: isActioning ? 0.6 : 1 }}
              >
                <SkipForward size={13} /> Skip
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/* ==========================================================================
   Skeleton
   ========================================================================== */

export function SkeletonRemedyCard() {
  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 12, padding: 18, display: 'flex', gap: 12, alignItems: 'center' }}>
      <div style={{ width: 40, height: 40, borderRadius: 10, background: 'var(--border)', animation: 'pulse 1.5s ease infinite', flexShrink: 0 }} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ width: '60%', height: 14, borderRadius: 4, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
        <div style={{ width: '90%', height: 10, borderRadius: 4, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
      </div>
    </div>
  );
}
