'use client';

import { useGlossary } from '@/hooks/use-glossary';

interface LocalizedTermProps {
  /** The astrological term to translate (glossary key or English name). */
  term: string;
  className?: string;
  style?: React.CSSProperties;
  /** Whether to show the native-script subscript (default: true). */
  showLocal?: boolean;
}

/**
 * Renders an astrological term with an optional native-script subscript.
 *
 * When the user's language preference is non-English, the component displays
 * the English name on the first line and the native translation below it in
 * a smaller, muted font.
 */
export function LocalizedTerm({
  term,
  className,
  style,
  showLocal = true,
}: LocalizedTermProps) {
  const { t } = useGlossary();
  const { name, local } = t(term);

  return (
    <span className={className} style={style}>
      {name}
      {showLocal && local && (
        <span
          style={{
            display: 'block',
            fontSize: '0.75em',
            opacity: 0.7,
            lineHeight: 1.2,
            color: 'var(--text-muted)',
          }}
        >
          {local}
        </span>
      )}
    </span>
  );
}
