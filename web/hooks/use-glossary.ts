/**
 * Hook for translating astrological terms into the user's preferred language.
 *
 * Reads language_preference from the user profile (via AuthContext), falling
 * back to browser locale detection, then to English.
 */

import { useAuth } from '@/contexts/AuthContext';
import { GLOSSARY, findEntry, type GlossaryLang } from '@/config/astro-glossary';

const SUPPORTED_LANGS: GlossaryLang[] = ['ta', 'te', 'kn', 'hi', 'ml', 'bn', 'sa'];

function detectBrowserLang(): GlossaryLang {
  if (typeof navigator === 'undefined') return 'en';
  const bl = navigator.language?.split('-')[0];
  return (SUPPORTED_LANGS as string[]).includes(bl)
    ? (bl as GlossaryLang)
    : 'en';
}

export interface TranslatedTerm {
  /** The canonical English name. */
  name: string;
  /** The native-script translation, or null when the user's language is English. */
  local: string | null;
}

export function useGlossary() {
  const { user } = useAuth();
  const lang = ((user as Record<string, unknown> | null)?.language_preference as GlossaryLang | undefined)
    || detectBrowserLang()
    || 'en';

  /**
   * Translate an astrological term.
   *
   * Accepts either a glossary key (`"ashwini"`) or an English display name
   * (`"Ashwini"`). Returns the English name plus the native-script form in
   * the user's preferred language (or `null` when the language is English).
   */
  function t(term: string): TranslatedTerm {
    const entry = findEntry(term);
    if (!entry) return { name: term, local: null };
    if (lang === 'en') return { name: entry.en, local: null };
    const localName = entry[lang];
    // Only show the local name when it is meaningfully different from English
    return {
      name: entry.en,
      local: localName && localName !== entry.en ? localName : null,
    };
  }

  return { t, lang };
}
