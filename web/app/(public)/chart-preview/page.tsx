'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Lock, Star, MessageSquare, Clock } from 'lucide-react';
import { getSunSign, parseDateToMonthDay } from '@/lib/sun-sign';

interface BirthData {
  name?: string;
  dob: string;
  tob?: string;
  place?: string;
}

export default function ChartPreviewPage() {
  const router = useRouter();
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [sunSign, setSunSign] = useState<ReturnType<typeof getSunSign> | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem('josi-birth-data');
    if (!raw) { router.push('/'); return; }
    try {
      const data = JSON.parse(raw) as BirthData;
      setBirthData(data);
      const parsed = parseDateToMonthDay(data.dob);
      if (parsed) setSunSign(getSunSign(parsed.month, parsed.day));
    } catch { router.push('/'); }
  }, [router]);

  if (!birthData || !sunSign) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#000000' }}>
        <div style={{ color: '#5B6A8A' }}>Loading your chart...</div>
      </div>
    );
  }

  const displayName = birthData.name || 'Your';
  const hasName = !!birthData.name;

  return (
    <div className="min-h-screen text-white" style={{ background: '#000000' }}>

      {/* Nav */}
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-6 px-8 py-3 rounded-full"
        style={{ background: 'rgba(17,24,40,0.40)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(200,145,58,0.12)' }}>
        <Link href="/" className="text-lg font-display tracking-tight text-white no-underline">Josi</Link>
        <Link href="/auth/login" className="text-sm font-medium transition-colors hover:opacity-80" style={{ color: '#C8913A' }}>Sign In</Link>
      </nav>

      {/* ═══ SUN SIGN — REAL ═══ */}
      <section className="pt-32 pb-12 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="font-semibold uppercase mb-6" style={{ fontSize: '10px', letterSpacing: '3px', color: '#C8913A' }}>
            {displayName}&rsquo;s Cosmic Blueprint
          </p>

          {/* Sun sign circle */}
          <div className="w-28 h-28 mx-auto mb-8 rounded-full flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, rgba(200,145,58,0.15), rgba(200,145,58,0.05))', border: '2px solid rgba(200,145,58,0.30)', boxShadow: '0 0 40px rgba(200,145,58,0.10)' }}>
            <span className="font-display" style={{ fontSize: '52px', color: '#C8913A' }}>{sunSign.symbol}</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-display mb-5" style={{ color: '#D4DAE6' }}>
            {hasName ? `${displayName}, you` : 'You'}&rsquo;re a {sunSign.sign}
          </h1>
          <p className="text-lg font-reading leading-relaxed max-w-xl mx-auto mb-8" style={{ color: '#7B8CA8' }}>
            {sunSign.snippet}
          </p>
          <div className="flex justify-center gap-6 text-sm" style={{ color: '#5B6A8A' }}>
            <span>{sunSign.element} sign</span>
            <span>&middot;</span>
            <span>{sunSign.quality}</span>
            <span>&middot;</span>
            <span>Ruled by {sunSign.ruling}</span>
          </div>
        </div>
      </section>

      {/* ═══ SIGN UP CTA ═══ */}
      <section className="py-10 px-4">
        <div className="max-w-lg mx-auto">
          <div className="rounded-2xl p-8 text-center" style={{
            background: 'rgba(200,145,58,0.06)', border: '1px solid rgba(200,145,58,0.20)',
          }}>
            <h2 className="text-xl font-display mb-3" style={{ color: '#D4DAE6' }}>
              Your full chart is ready
            </h2>
            <p className="text-sm mb-6" style={{ color: '#7B8CA8' }}>
              Create a free account to unlock your Moon sign, Ascendant, planetary positions, Dasha timeline, and AI-powered interpretations across all six traditions.
            </p>
            <Link href="/auth/sign-up"
              className="inline-flex items-center px-8 py-3.5 rounded-xl font-semibold transition-all hover:opacity-90"
              style={{ background: '#C8913A', color: '#000000' }}>
              Create Free Account &rarr;
            </Link>
            <p className="text-xs mt-4" style={{ color: '#3A4A6A' }}>
              No credit card required &middot; Free tier includes 3 charts
            </p>
          </div>
        </div>
      </section>

      {/* ═══ LOCKED FEATURES — Solid cards, no blur ═══ */}
      <section className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <p className="text-center text-sm mb-8" style={{ color: '#5B6A8A' }}>Here&rsquo;s what&rsquo;s waiting for you</p>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Locked: Full Chart */}
            <div className="rounded-2xl p-8 text-center" style={{ background: 'rgba(17,24,40,0.40)', border: '1px solid rgba(26,35,64,0.50)' }}>
              <div className="w-14 h-14 mx-auto mb-5 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(200,145,58,0.10)' }}>
                <Star className="w-7 h-7" style={{ color: '#C8913A' }} />
              </div>
              <Lock className="w-5 h-5 mx-auto mb-3" style={{ color: '#3A4A6A' }} />
              <h3 className="text-lg font-display mb-2" style={{ color: '#D4DAE6' }}>Your Complete Birth Chart</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#5B6A8A' }}>
                Moon sign, Ascendant, all 9 planetary positions with exact degrees, Nakshatras, house placements, and divisional charts across six traditions.
              </p>
            </div>

            {/* Locked: AI Chat */}
            <div className="rounded-2xl p-8 text-center" style={{ background: 'rgba(17,24,40,0.40)', border: '1px solid rgba(26,35,64,0.50)' }}>
              <div className="w-14 h-14 mx-auto mb-5 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(150,120,200,0.10)' }}>
                <MessageSquare className="w-7 h-7" style={{ color: '#9678C8' }} />
              </div>
              <Lock className="w-5 h-5 mx-auto mb-3" style={{ color: '#3A4A6A' }} />
              <h3 className="text-lg font-display mb-2" style={{ color: '#D4DAE6' }}>AI Astrologer</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#5B6A8A' }}>
                Ask anything about your {sunSign.sign} placements. &ldquo;Why do I overthink?&rdquo; &ldquo;When should I change careers?&rdquo; Get chart-specific answers, not generic horoscopes.
              </p>
            </div>

            {/* Locked: Dasha Timeline */}
            <div className="rounded-2xl p-8 text-center" style={{ background: 'rgba(17,24,40,0.40)', border: '1px solid rgba(26,35,64,0.50)' }}>
              <div className="w-14 h-14 mx-auto mb-5 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(106,159,216,0.10)' }}>
                <Clock className="w-7 h-7" style={{ color: '#6A9FD8' }} />
              </div>
              <Lock className="w-5 h-5 mx-auto mb-3" style={{ color: '#3A4A6A' }} />
              <h3 className="text-lg font-display mb-2" style={{ color: '#D4DAE6' }}>Life Period Timeline</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#5B6A8A' }}>
                Your Vimshottari Dasha — planetary periods that map your life into chapters. Know which planet rules your current period and when the next shift comes.
              </p>
            </div>

            {/* Locked: Compatibility */}
            <div className="rounded-2xl p-8 text-center" style={{ background: 'rgba(17,24,40,0.40)', border: '1px solid rgba(26,35,64,0.50)' }}>
              <div className="w-14 h-14 mx-auto mb-5 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(106,176,122,0.10)' }}>
                <span className="text-2xl" style={{ color: '#6AB07A' }}>&#10023;</span>
              </div>
              <Lock className="w-5 h-5 mx-auto mb-3" style={{ color: '#3A4A6A' }} />
              <h3 className="text-lg font-display mb-2" style={{ color: '#D4DAE6' }}>Compatibility Analysis</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#5B6A8A' }}>
                Compare your chart with anyone else&rsquo;s. Ashtakoot matching, synastry, and AI-powered relationship insights across traditions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ FINAL CTA ═══ */}
      <section className="py-16 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-display mb-3" style={{ color: '#D4DAE6' }}>
            Your {sunSign.sign} story goes much deeper
          </h2>
          <p className="text-sm mb-8" style={{ color: '#5B6A8A' }}>
            The Sun is just the beginning. Your Moon, Ascendant, and planetary periods reveal the rest.
          </p>
          <Link href="/auth/sign-up"
            className="inline-flex items-center px-8 py-3.5 rounded-xl font-semibold transition-all hover:opacity-90"
            style={{ background: '#C8913A', color: '#000000' }}>
            Create Free Account &rarr;
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <span className="text-sm" style={{ color: '#3A4A6A' }}>&copy; 2026 Josi. All rights reserved.</span>
          <Link href="/auth/login" className="text-sm transition-colors hover:text-white" style={{ color: '#5B6A8A' }}>Sign In</Link>
        </div>
      </footer>
    </div>
  );
}
