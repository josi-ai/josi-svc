/**
 * Helpers for the Compatibility page.
 */

export function scoreColor(score: number): string {
  if (score >= 25) return 'var(--green)';
  if (score >= 18) return 'var(--gold)';
  return 'var(--red)';
}

export function scoreLabel(score: number): string {
  if (score >= 32) return 'Excellent Match';
  if (score >= 25) return 'Very Good Match';
  if (score >= 18) return 'Good Match';
  return 'Needs Attention';
}

export function scoreBg(score: number): string {
  if (score >= 25) return 'var(--green-bg)';
  if (score >= 18) return 'var(--gold-bg)';
  return 'var(--red-bg)';
}
