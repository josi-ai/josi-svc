/**
 * Helpers and constants for the Dasha page.
 */

import React from 'react';

export const PLANET_COLORS: Record<string, string> = {
  Sun: 'var(--planet-sun)', Moon: 'var(--planet-moon)', Mars: 'var(--planet-mars)', Mercury: 'var(--planet-mercury)',
  Jupiter: 'var(--planet-jupiter)', Venus: 'var(--planet-venus)', Saturn: 'var(--planet-saturn)', Rahu: 'var(--planet-rahu)', Ketu: 'var(--planet-ketu)',
};
export const pColor = (p: string) => PLANET_COLORS[p] || 'var(--text-muted)';

export function parseDate(d: string | Date | undefined): Date | null {
  if (!d) return null;
  const dt = d instanceof Date ? d : new Date(d);
  return isNaN(dt.getTime()) ? null : dt;
}

export function fmtDate(d: string | Date | undefined): string {
  const dt = parseDate(d);
  return dt ? dt.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '\u2014';
}

export const HEADING: React.CSSProperties = { fontFamily: "'DM Serif Display', serif", fontSize: 16, color: 'var(--text-primary)', marginBottom: 16 };
export const CARD: React.CSSProperties = { border: '1px solid var(--border)', borderRadius: 14, background: 'var(--bg-card)', padding: 20 };
export const LABEL: React.CSSProperties = { fontSize: 10, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 };

export interface PlanetInterpretation {
  theme: string;
  areas: string[];
  doAdvice: string[];
  dontAdvice: string[];
}

export const PLANET_INTERPRETATIONS: Record<string, PlanetInterpretation> = {
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
