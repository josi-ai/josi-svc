'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Briefcase,
  DollarSign,
  Heart,
  Home,
  Activity,
  GraduationCap,
  Sparkles,
  Plane,
  Users,
  Scale,
  AlertTriangle,
  Lightbulb,
  ChevronDown,
  MessageSquare,
  type LucideIcon,
} from 'lucide-react';
import { scoreColor, scoreBg } from './score-card';

/* ==========================================================================
   Types
   ========================================================================== */

export interface Category {
  name: string;
  slug: string;
  score: number;
  summary: string;
  details?: string;
  advice: string;
  caution: string | null;
}

/* ==========================================================================
   Constants
   ========================================================================== */

const CATEGORY_ICONS: Record<string, LucideIcon> = {
  career: Briefcase,
  finance: DollarSign,
  love: Heart,
  family: Home,
  health: Activity,
  education: GraduationCap,
  spirituality: Sparkles,
  travel: Plane,
  social: Users,
  legal: Scale,
};

/* ==========================================================================
   Component
   ========================================================================== */

export function CategoryCard({ cat }: { cat: Category }) {
  const Icon = CATEGORY_ICONS[cat.slug] || Sparkles;
  const color = scoreColor(cat.score);
  const barPct = (cat.score / 10) * 100;
  const router = useRouter();

  const [expanded, setExpanded] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const [contentHeight, setContentHeight] = useState(0);

  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(contentRef.current.scrollHeight);
    }
  }, [expanded, cat.details]);

  const hasExpandable = !!(cat.details || cat.advice || cat.caution);

  return (
    <div
      style={{
        background: 'var(--card)',
        border: expanded ? '1px solid var(--gold)' : '1px solid var(--border)',
        borderRadius: 12,
        padding: 20,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        cursor: hasExpandable ? 'pointer' : 'default',
        transition: 'border-color 0.2s ease',
      }}
      onClick={() => hasExpandable && setExpanded((prev) => !prev)}
    >
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 8,
              background: scoreBg(cat.score),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon size={18} style={{ color }} />
          </div>
          <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
            {cat.name}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontWeight: 700, fontSize: 18, color }}>{cat.score.toFixed(1)}</span>
          {hasExpandable && (
            <ChevronDown
              size={16}
              style={{
                color: 'var(--text-muted)',
                transition: 'transform 0.25s ease',
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
              }}
            />
          )}
        </div>
      </div>

      {/* Score bar */}
      <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
        <div
          style={{
            width: `${barPct}%`,
            height: '100%',
            borderRadius: 3,
            background: color,
            transition: 'width 0.5s ease',
          }}
        />
      </div>

      {/* Summary */}
      <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
        {cat.summary}
      </p>

      {/* Expandable section */}
      <div
        style={{
          maxHeight: expanded ? contentHeight : 0,
          overflow: 'hidden',
          transition: 'max-height 0.3s ease',
        }}
      >
        <div ref={contentRef} style={{ display: 'flex', flexDirection: 'column', gap: 10, paddingTop: 4 }}>
          {/* Details */}
          {cat.details && (
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0, paddingTop: 8, borderTop: '1px solid var(--border)' }}>
              {cat.details}
            </p>
          )}

          {/* Advice */}
          {cat.advice && (
            <div
              style={{
                display: 'flex',
                gap: 8,
                alignItems: 'flex-start',
                fontSize: 12,
                color: 'var(--text-muted)',
                background: 'rgba(99,102,241,0.06)',
                borderRadius: 8,
                padding: '8px 10px',
              }}
            >
              <Lightbulb size={14} style={{ color: 'var(--gold)', flexShrink: 0, marginTop: 1 }} />
              <span>{cat.advice}</span>
            </div>
          )}

          {/* Caution */}
          {cat.caution && (
            <div
              style={{
                display: 'flex',
                gap: 8,
                alignItems: 'flex-start',
                fontSize: 12,
                color: '#d97706',
                background: 'rgba(217,119,6,0.08)',
                borderRadius: 8,
                padding: '8px 10px',
              }}
            >
              <AlertTriangle size={14} style={{ flexShrink: 0, marginTop: 1 }} />
              <span>{cat.caution}</span>
            </div>
          )}

          {/* Ask AI button */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              router.push(`/ai?q=${encodeURIComponent(cat.name + ' outlook')}`);
            }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              alignSelf: 'flex-start',
              padding: '6px 14px',
              fontSize: 12,
              fontWeight: 600,
              color: 'var(--gold)',
              background: 'rgba(212,175,55,0.1)',
              border: '1px solid rgba(212,175,55,0.25)',
              borderRadius: 8,
              cursor: 'pointer',
              transition: 'background 0.15s ease',
              marginTop: 4,
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(212,175,55,0.18)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(212,175,55,0.1)')}
          >
            <MessageSquare size={13} />
            Ask AI about {cat.name}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   Skeleton
   ========================================================================== */

export function SkeletonCategoryCard() {
  return (
    <div
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 12,
        padding: 20,
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 36, height: 36, borderRadius: 8, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
        <div style={{ width: 120, height: 14, borderRadius: 4, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
      </div>
      <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
      <div style={{ height: 40, borderRadius: 6, background: 'var(--border)', animation: 'pulse 1.5s ease infinite' }} />
    </div>
  );
}
