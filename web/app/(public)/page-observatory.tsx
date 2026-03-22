'use client';

import Link from 'next/link';
import { Fingerprint, Hourglass, Heart } from 'lucide-react';
import BirthDataForm from '@/components/landing/birth-data-form';
import SkyMap from '@/components/landing/sky-map';
import { VedicChartIcon, WesternChartIcon, ChineseChartIcon, HellenisticChartIcon, MayanChartIcon, CelticChartIcon } from '@/components/landing/tradition-chart-icons';

export default function LandingPage() {
  return (
    <div className="min-h-screen text-white" style={{ background: '#000000' }}>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 1 — HERO (Sky Map + Form)
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
        <SkyMap />

        <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-6 px-8 py-3 rounded-full"
          style={{ background: 'rgba(17,24,40,0.25)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', border: '1px solid rgba(200,145,58,0.12)' }}>
          <span className="text-lg font-display tracking-tight text-white">Josi</span>
          <Link href="/auth/login" className="text-sm font-medium transition-colors hover:opacity-80" style={{ color: '#C8913A' }}>Sign In</Link>
        </nav>

        <div className="relative z-10 w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 lg:gap-16 items-center px-4">
          <div>
            <p className="font-semibold uppercase mb-6" style={{ fontSize: '10px', letterSpacing: '3px', color: '#C8913A' }}>
              Multi-Tradition Astrology Platform
            </p>
            <h1 className="text-4xl md:text-5xl font-display mb-6 leading-tight" style={{ color: '#D4DAE6' }}>
              Ancient eyes on an infinite sky
            </h1>
            <p className="text-base md:text-[17px] font-reading leading-relaxed" style={{ color: '#7B8CA8' }}>
              The moment you were born, six ancient traditions began telling your story. Each one sees something different. Together, they see all of you.
            </p>
          </div>
          <div>
            <BirthDataForm />
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce z-10">
          <svg className="w-6 h-6" style={{ color: '#3A4A6A' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 2 — WHAT YOU'LL DISCOVER (outcome-focused, visual)
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="py-28 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-[40px] md:leading-tight font-display mb-4" style={{ color: '#D4DAE6' }}>
              What you&rsquo;ll discover
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Fingerprint className="w-7 h-7" />,
                title: 'Your personality patterns',
                desc: 'Why you think the way you do. Why relationships follow certain rhythms. What drives you beneath the surface.',
                color: '#C8913A',
                bg: 'rgba(200,145,58,0.10)',
              },
              {
                icon: <Hourglass className="w-7 h-7" />,
                title: 'Your life timing',
                desc: 'When to act, when to wait. Planetary periods that shape your career, relationships, and growth — mapped across years.',
                color: '#6A9FD8',
                bg: 'rgba(106,159,216,0.10)',
              },
              {
                icon: <Heart className="w-7 h-7" />,
                title: 'Your cosmic connections',
                desc: 'How you relate to others. Compatibility across traditions. Which relationships challenge you and which ones flow.',
                color: '#6AB07A',
                bg: 'rgba(106,176,122,0.10)',
              },
            ].map((item) => (
              <div key={item.title} className="text-center">
                <div className="w-14 h-14 mx-auto mb-5 rounded-2xl flex items-center justify-center" style={{ background: item.bg, color: item.color }}>
                  {item.icon}
                </div>
                <h3 className="text-lg font-display mb-3" style={{ color: '#D4DAE6' }}>{item.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#5B6A8A' }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 3 — AI CHAT PREVIEW
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="py-28 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-5xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left: Copy */}
            <div>
              <p className="font-semibold uppercase mb-5" style={{ fontSize: '10px', letterSpacing: '3px', color: '#C8913A' }}>
                Your AI Astrologer
              </p>
              <h2 className="text-3xl md:text-[36px] md:leading-tight font-display mb-6" style={{ color: '#D4DAE6' }}>
                Ask anything about your chart
              </h2>
              <p className="text-[15px] font-reading leading-relaxed mb-6" style={{ color: '#7B8CA8' }}>
                &ldquo;Why do I keep attracting the same kind of relationship?&rdquo;
                &ldquo;When should I make this career move?&rdquo;
                &ldquo;What does my Saturn return actually mean for me?&rdquo;
              </p>
              <p className="text-sm leading-relaxed" style={{ color: '#5B6A8A' }}>
                Josi AI knows your chart inside and out. It doesn&rsquo;t give generic horoscopes — it reads your specific placements, understands your planetary periods, and learns from every conversation.
              </p>
            </div>

            {/* Right: Chat Preview */}
            <div
              className="rounded-2xl p-6"
              style={{
                background: 'rgba(17,24,40,0.50)',
                border: '1px solid rgba(200,145,58,0.18)',
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 0 1px rgba(200,145,58,0.05) inset',
              }}
            >
              {/* AI Header */}
              <div className="flex items-center gap-2.5 mb-5">
                <div className="w-9 h-9 rounded-full flex items-center justify-center text-sm"
                  style={{ background: 'rgba(200,145,58,0.25)', color: '#C8913A', border: '1px solid rgba(200,145,58,0.30)', boxShadow: '0 0 8px rgba(200,145,58,0.15)' }}>
                  &#10022;
                </div>
                <div>
                  <div className="text-[14px] font-medium" style={{ color: '#D4DAE6' }}>Josi AI</div>
                  <div className="text-[10px]" style={{ color: '#5B6A8A' }}>Knows your chart &middot; Learns from you</div>
                </div>
              </div>

              {/* Conversation */}
              <div className="space-y-4 mb-5">
                {/* User question */}
                <div className="flex justify-end">
                  <div className="rounded-xl px-4 py-2.5 max-w-[80%]" style={{ background: 'rgba(200,145,58,0.12)', border: '1px solid rgba(200,145,58,0.20)' }}>
                    <p className="text-[13px]" style={{ color: '#D4DAE6' }}>I&rsquo;ve been feeling stuck in my career lately. What does my chart say?</p>
                  </div>
                </div>

                {/* AI response */}
                <div className="rounded-xl p-4" style={{
                  background: 'rgba(17,24,40,0.60)', borderLeft: '2px solid rgba(200,145,58,0.40)',
                  borderTop: '1px solid rgba(26,35,64,0.50)', borderRight: '1px solid rgba(26,35,64,0.50)', borderBottom: '1px solid rgba(26,35,64,0.50)',
                }}>
                  <p className="text-[13px] leading-relaxed font-reading" style={{ color: '#94A3B8' }}>
                    <strong style={{ color: '#D4DAE6' }}>Your Saturn Antar Dasha</strong> is asking you to build foundations right now. The &ldquo;stuck&rdquo; feeling is actually Saturn restructuring your 10th house.
                  </p>
                  <p className="text-[13px] leading-relaxed font-reading mt-3" style={{ color: '#94A3B8' }}>
                    This shifts in <strong style={{ color: '#C8913A' }}>June 2026</strong> when Mercury Pratyantar begins — expect doors to open through writing, communication, or international connections.
                  </p>
                </div>

                {/* Follow-up */}
                <div className="flex justify-end">
                  <div className="rounded-xl px-4 py-2.5 max-w-[80%]" style={{ background: 'rgba(200,145,58,0.12)', border: '1px solid rgba(200,145,58,0.20)' }}>
                    <p className="text-[13px]" style={{ color: '#D4DAE6' }}>So I should wait until June?</p>
                  </div>
                </div>

                {/* AI response 2 */}
                <div className="rounded-xl p-4" style={{
                  background: 'rgba(17,24,40,0.60)', borderLeft: '2px solid rgba(200,145,58,0.40)',
                  borderTop: '1px solid rgba(26,35,64,0.50)', borderRight: '1px solid rgba(26,35,64,0.50)', borderBottom: '1px solid rgba(26,35,64,0.50)',
                }}>
                  <p className="text-[13px] leading-relaxed font-reading" style={{ color: '#94A3B8' }}>
                    Not wait — <em>prepare</em>. Saturn rewards effort, not patience. Use this period to build skills and clarity. The shift will amplify whatever you&rsquo;ve built.
                  </p>
                </div>
              </div>

              {/* Input + chips */}
              <div className="rounded-lg px-3.5 py-2.5 mb-3 flex items-center justify-between"
                style={{ background: 'rgba(6,10,20,0.80)', border: '1px solid rgba(26,35,64,0.60)' }}>
                <span className="text-[13px]" style={{ color: '#3A4A6A' }}>Ask about your chart...</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ color: '#C8913A', opacity: 0.5 }}>
                  <path d="M22 2L11 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div className="flex gap-2 flex-wrap">
                {['My relationships', 'Career timing', 'Saturn return'].map((chip) => (
                  <span key={chip} className="rounded-full px-3 py-1.5 text-[11px]"
                    style={{ background: 'rgba(200,145,58,0.06)', border: '1px solid rgba(200,145,58,0.25)', color: 'rgba(200,145,58,0.75)' }}>
                    {chip}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 4 — SIX TRADITIONS (compact)
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="py-28 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-[36px] md:leading-tight font-display mb-3" style={{ color: '#D4DAE6' }}>
              Six traditions. One birth moment.
            </h2>
            <p className="text-sm" style={{ color: '#5B6A8A' }}>Same sky, different wisdom. Each tradition reveals something the others don&rsquo;t.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
            {[
              { icon: <VedicChartIcon />, bg: 'rgba(200,145,58,0.10)', title: 'Vedic', q: 'Life purpose & karma' },
              { icon: <WesternChartIcon />, bg: 'rgba(106,159,216,0.10)', title: 'Western', q: 'Personality & psyche' },
              { icon: <ChineseChartIcon />, bg: 'rgba(224,128,96,0.10)', title: 'Chinese', q: 'Elemental balance' },
              { icon: <HellenisticChartIcon />, bg: 'rgba(150,120,200,0.10)', title: 'Hellenistic', q: 'Social roles & fate' },
              { icon: <MayanChartIcon />, bg: 'rgba(80,184,208,0.10)', title: 'Mayan', q: 'Cosmic frequency' },
              { icon: <CelticChartIcon />, bg: 'rgba(106,176,122,0.10)', title: 'Celtic', q: 'Natural wisdom' },
            ].map((t) => (
              <div key={t.title} className="rounded-xl p-5 flex items-center gap-4" style={{ background: 'rgba(17,24,40,0.30)', border: '1px solid rgba(26,35,64,0.50)' }}>
                <div className="w-[64px] h-[64px] flex-shrink-0 flex items-center justify-center rounded-lg overflow-hidden" style={{ background: t.bg }}>
                  {t.icon}
                </div>
                <div>
                  <h3 className="text-[15px] font-semibold mb-0.5" style={{ color: '#D4DAE6' }}>{t.title}</h3>
                  <p className="text-[12px]" style={{ color: '#5B6A8A' }}>{t.q}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 5 — FINAL CTA
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl md:text-[32px] md:leading-snug font-display mb-4" style={{ color: '#D4DAE6' }}>
            Your chart is already written in the sky
          </h2>
          <p className="mb-10" style={{ color: '#5B6A8A' }}>You just haven&rsquo;t read it yet.</p>
          <Link href="/chart-calculator" className="inline-flex items-center px-8 py-4 rounded-xl font-semibold transition-all hover:opacity-90" style={{ background: '#C8913A', color: '#060A14' }}>
            Discover Your Cosmic Story
          </Link>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          FOOTER
       ═══════════════════════════════════════════════════════════════════ */}
      <footer className="py-8 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <span className="text-sm" style={{ color: '#3A4A6A' }}>&copy; 2026 Josi. All rights reserved.</span>
          <Link href="/auth/login" className="text-sm transition-colors hover:text-white" style={{ color: '#5B6A8A' }}>Sign In</Link>
        </div>
      </footer>
    </div>
  );
}
