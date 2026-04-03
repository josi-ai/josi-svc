'use client';

/* ---------- Types ---------- */

export interface TimeframeSelectorProps {
  value: string;
  onChange: (timeframe: string) => void;
  options?: string[];
  className?: string;
  style?: React.CSSProperties;
}

/* ---------- Constants ---------- */

const DEFAULT_OPTIONS = [
  'Daily',
  'Weekly',
  'Monthly',
  'Quarterly',
  'Half-yearly',
  'Yearly',
];

/* ---------- Component ---------- */

export function TimeframeSelector({
  value,
  onChange,
  options = DEFAULT_OPTIONS,
  className = '',
  style,
}: TimeframeSelectorProps) {
  return (
    <div
      className={className}
      style={{
        display: 'flex',
        gap: 0,
        overflowX: 'auto',
        WebkitOverflowScrolling: 'touch',
        msOverflowStyle: 'none',
        scrollbarWidth: 'none',
        borderBottom: '1px solid var(--border)',
        ...style,
      }}
    >
      {options.map((option) => {
        const isActive = value === option;
        return (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            style={{
              padding: '10px 18px',
              fontSize: 13,
              fontWeight: isActive ? 600 : 500,
              color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
              background: 'transparent',
              border: 'none',
              borderBottom: isActive
                ? '3px solid var(--gold)'
                : '3px solid transparent',
              cursor: 'pointer',
              transition: 'color 0.15s, border-color 0.15s',
              marginBottom: -1,
              whiteSpace: 'nowrap',
              flexShrink: 0,
            }}
          >
            {option}
          </button>
        );
      })}

    </div>
  );
}
