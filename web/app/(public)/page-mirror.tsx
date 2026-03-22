'use client';

import Link from 'next/link';
import BirthDataForm from '@/components/landing/birth-data-form';
import { VedicChartIcon, WesternChartIcon, ChineseChartIcon, HellenisticChartIcon, MayanChartIcon, CelticChartIcon } from '@/components/landing/tradition-chart-icons';

const constellationBg = `url("data:image/svg+xml,%3Csvg width='200' height='200' viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='20' cy='30' r='1' fill='%23C8913A'/%3E%3Ccircle cx='80' cy='60' r='1.5' fill='%23C8913A'/%3E%3Ccircle cx='150' cy='20' r='1' fill='%23C8913A'/%3E%3Ccircle cx='120' cy='100' r='1.2' fill='%23C8913A'/%3E%3Ccircle cx='40' cy='140' r='1' fill='%23C8913A'/%3E%3Ccircle cx='170' cy='150' r='1.5' fill='%23C8913A'/%3E%3Ccircle cx='90' cy='180' r='1' fill='%23C8913A'/%3E%3Cline x1='20' y1='30' x2='80' y2='60' stroke='%23C8913A' stroke-width='0.3'/%3E%3Cline x1='80' y1='60' x2='150' y2='20' stroke='%23C8913A' stroke-width='0.3'/%3E%3Cline x1='80' y1='60' x2='120' y2='100' stroke='%23C8913A' stroke-width='0.3'/%3E%3Cline x1='120' y1='100' x2='170' y2='150' stroke='%23C8913A' stroke-width='0.3'/%3E%3Cline x1='40' y1='140' x2='90' y2='180' stroke='%23C8913A' stroke-width='0.3'/%3E%3C/svg%3E")`;

export default function LandingPageMirror() {
  return (
    <div className="min-h-screen text-white" style={{ background: '#000000' }}>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 1 — HERO (AI Chat Preview + Form)
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="relative min-h-screen flex items-center px-4 overflow-hidden">
        <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: constellationBg, backgroundSize: '200px 200px' }} />
        <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse 50% 35% at 50% 45%, rgba(200,145,58,0.05) 0%, transparent 70%)' }} />

        <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-6 px-8 py-3 rounded-full"
          style={{ background: 'rgba(0,0,0,0.40)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(200,145,58,0.12)' }}>
          <span className="text-lg font-display tracking-tight text-white">Josi</span>
          <Link href="/auth/login" className="text-sm font-medium transition-colors hover:opacity-80" style={{ color: '#C8913A' }}>Sign In</Link>
        </nav>

        <div className="relative z-10 w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 lg:gap-16 items-center pt-28 pb-16 lg:pt-0 lg:pb-0">
          {/* Left: Copy + mini chat */}
          <div className="max-w-lg">
            <p className="text-xs font-semibold uppercase tracking-[3px] mb-6" style={{ color: '#C8913A' }}>Your Cosmic Blueprint</p>
            <h1 className="text-4xl md:text-5xl font-light tracking-tight mb-6 font-display leading-tight" style={{ color: '#D4DAE6' }}>
              The stars have been telling your story since the day you were born
            </h1>
            <p className="text-base md:text-[17px] leading-relaxed font-reading mb-8" style={{ color: '#7B8CA8' }}>
              Vedic sees your karma. Western maps your psyche. Chinese reads your elements. See yourself through all of them.
            </p>

            {/* Mini chat preview */}
            <div className="rounded-2xl p-5 max-w-sm" style={{
              background: 'rgba(17,24,40,0.50)', border: '1px solid rgba(200,145,58,0.18)',
              backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
            }}>
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                  style={{ background: 'rgba(200,145,58,0.25)', color: '#C8913A', border: '1px solid rgba(200,145,58,0.30)' }}>&#10022;</div>
                <div>
                  <div className="text-[13px] font-medium" style={{ color: '#D4DAE6' }}>Josi AI</div>
                  <div className="text-[10px]" style={{ color: '#5B6A8A' }}>Your personal astrologer</div>
                </div>
              </div>
              <div className="rounded-xl p-3.5" style={{ background: 'rgba(17,24,40,0.60)', borderLeft: '2px solid rgba(200,145,58,0.40)', border: '1px solid rgba(26,35,64,0.50)' }}>
                <p className="text-[13px] leading-relaxed font-reading" style={{ color: '#94A3B8' }}>
                  Your Moon in Scorpio creates a deep well of creative intensity. This placement suggests your emotional world is rich and transformative.
                </p>
              </div>
            </div>
            <p className="text-[11px] mt-3" style={{ color: '#5B6A8A' }}>AI astrologer that knows your chart &middot; Learns from you</p>
          </div>

          {/* Right: Form */}
          <div><BirthDataForm /></div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 2 — SEE IT IN ACTION (Product Previews)
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="py-28 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <p className="font-semibold uppercase mb-4" style={{ fontSize: '10px', letterSpacing: '3px', color: '#C8913A' }}>See It In Action</p>
            <h2 className="text-3xl md:text-[36px] md:leading-tight font-display mb-3" style={{ color: '#D4DAE6' }}>
              Everything you need, in one place
            </h2>
            <p className="text-sm" style={{ color: '#5B6A8A' }}>Your dashboard. Your charts. Your AI astrologer.</p>
          </div>

          {/* Three product preview cards */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Dashboard Preview */}
            <div className="rounded-2xl overflow-hidden" style={{ background: 'rgba(17,24,40,0.30)', border: '1px solid rgba(26,35,64,0.50)' }}>
              {/* Mock dashboard header */}
              <div className="px-5 pt-5 pb-3">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 rounded-full" style={{ background: '#C45D4A' }} />
                  <div className="w-2 h-2 rounded-full" style={{ background: '#D4A04A' }} />
                  <div className="w-2 h-2 rounded-full" style={{ background: '#6AB07A' }} />
                </div>
                {/* Mini widget mockup */}
                <div className="rounded-lg p-3 mb-2" style={{ background: 'rgba(200,145,58,0.06)', border: '1px solid rgba(200,145,58,0.12)' }}>
                  <div className="text-[9px] uppercase tracking-wider mb-1" style={{ color: '#C8913A' }}>Today&rsquo;s Sky</div>
                  <div className="text-[13px] font-display" style={{ color: '#D4DAE6' }}>Shukla Chaturthi</div>
                  <div className="text-[10px]" style={{ color: '#5B6A8A' }}>Moon in Taurus &middot; Rohini</div>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1 rounded-lg p-2.5" style={{ background: 'rgba(10,15,30,0.40)', border: '1px solid rgba(26,35,64,0.40)' }}>
                    <div className="text-[9px]" style={{ color: '#5B6A8A' }}>Charts</div>
                    <div className="text-[16px] font-display" style={{ color: '#D4DAE6' }}>12</div>
                  </div>
                  <div className="flex-1 rounded-lg p-2.5" style={{ background: 'rgba(10,15,30,0.40)', border: '1px solid rgba(26,35,64,0.40)' }}>
                    <div className="text-[9px]" style={{ color: '#5B6A8A' }}>AI Readings</div>
                    <div className="text-[16px] font-display" style={{ color: '#9678C8' }}>7</div>
                  </div>
                </div>
              </div>
              <div className="px-5 pb-5 pt-3">
                <h3 className="text-[15px] font-semibold mb-1" style={{ color: '#D4DAE6' }}>Personalized Dashboard</h3>
                <p className="text-[12px] leading-relaxed" style={{ color: '#5B6A8A' }}>
                  Daily sky updates, chart widgets, dasha timeline, and muhurta timing — all customizable.
                </p>
              </div>
            </div>

            {/* Chart Preview */}
            <div className="rounded-2xl overflow-hidden" style={{ background: 'rgba(17,24,40,0.30)', border: '1px solid rgba(26,35,64,0.50)' }}>
              <div className="px-5 pt-5 pb-3">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 rounded-full" style={{ background: '#C45D4A' }} />
                  <div className="w-2 h-2 rounded-full" style={{ background: '#D4A04A' }} />
                  <div className="w-2 h-2 rounded-full" style={{ background: '#6AB07A' }} />
                </div>
                {/* Mini chart mockup */}
                <div className="flex items-center gap-4 mb-3">
                  <div className="flex-shrink-0"><VedicChartIcon /></div>
                  <div>
                    <div className="text-[12px] font-medium" style={{ color: '#D4DAE6' }}>Sun Pisces, Moon Scorpio</div>
                    <div className="text-[10px]" style={{ color: '#5B6A8A' }}>Ascendant Cancer &middot; Anuradha</div>
                  </div>
                </div>
                {/* Mini planet table */}
                <div className="space-y-1.5">
                  {[
                    { planet: 'Sun', sign: 'Pisces', deg: '29°14\'', color: '#C8913A' },
                    { planet: 'Moon', sign: 'Scorpio', deg: '14°32\'', color: '#6A9FD8' },
                    { planet: 'Mars', sign: 'Aries', deg: '08°45\'', color: '#E08060' },
                  ].map((p) => (
                    <div key={p.planet} className="flex items-center justify-between text-[10px]">
                      <div className="flex items-center gap-1.5">
                        <div className="w-1.5 h-1.5 rounded-full" style={{ background: p.color }} />
                        <span style={{ color: '#94A3B8' }}>{p.planet}</span>
                      </div>
                      <span style={{ color: '#5B6A8A' }}>{p.sign} {p.deg}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="px-5 pb-5 pt-3">
                <h3 className="text-[15px] font-semibold mb-1" style={{ color: '#D4DAE6' }}>Multi-Tradition Charts</h3>
                <p className="text-[12px] leading-relaxed" style={{ color: '#5B6A8A' }}>
                  Six chart systems. Tabbed detail view with planets, houses, aspects, divisional charts, and yogas.
                </p>
              </div>
            </div>

            {/* AI Chat Preview */}
            <div className="rounded-2xl overflow-hidden" style={{ background: 'rgba(17,24,40,0.30)', border: '1px solid rgba(26,35,64,0.50)' }}>
              <div className="px-5 pt-5 pb-3">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 rounded-full" style={{ background: '#C45D4A' }} />
                  <div className="w-2 h-2 rounded-full" style={{ background: '#D4A04A' }} />
                  <div className="w-2 h-2 rounded-full" style={{ background: '#6AB07A' }} />
                </div>
                {/* Mini chat mockup */}
                <div className="space-y-2.5">
                  <div className="flex justify-end">
                    <div className="rounded-lg px-3 py-1.5 text-[10px] max-w-[75%]" style={{ background: 'rgba(200,145,58,0.12)', color: '#D4DAE6' }}>
                      Why do I keep overthinking everything?
                    </div>
                  </div>
                  <div className="rounded-lg px-3 py-2 text-[10px] leading-relaxed" style={{ background: 'rgba(10,15,30,0.60)', borderLeft: '2px solid rgba(200,145,58,0.3)', color: '#94A3B8' }}>
                    Your Mercury in Gemini in the 3rd house creates a mind that processes by exploring every angle. It&rsquo;s not overthinking — it&rsquo;s your cognitive architecture.
                  </div>
                  <div className="flex justify-end">
                    <div className="rounded-lg px-3 py-1.5 text-[10px] max-w-[75%]" style={{ background: 'rgba(200,145,58,0.12)', color: '#D4DAE6' }}>
                      How do I work with it instead of against it?
                    </div>
                  </div>
                  <div className="rounded-lg px-3 py-2 text-[10px] leading-relaxed" style={{ background: 'rgba(10,15,30,0.60)', borderLeft: '2px solid rgba(200,145,58,0.3)', color: '#94A3B8' }}>
                    Write before you decide. Your Mercury needs to externalize thoughts to find clarity.
                  </div>
                </div>
              </div>
              <div className="px-5 pb-5 pt-3">
                <h3 className="text-[15px] font-semibold mb-1" style={{ color: '#D4DAE6' }}>AI Astrologer</h3>
                <p className="text-[12px] leading-relaxed" style={{ color: '#5B6A8A' }}>
                  Ask anything. Get chart-specific answers. Five interpretation styles. Learns from every conversation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          SECTION 3 — HOW IT WORKS (3 steps)
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="py-28 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-[36px] md:leading-tight font-display mb-3" style={{ color: '#D4DAE6' }}>
              From birth data to cosmic clarity
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-8 left-[16.67%] right-[16.67%] h-px" style={{ background: 'linear-gradient(to right, #C8913A, rgba(200,145,58,0.2), #C8913A)' }} />
            {[
              { n: '1', title: 'Enter your birth details', desc: "Date, time, and place. That\u2019s all we need. If you don\u2019t know your exact time, we\u2019ll work with what you have." },
              { n: '2', title: 'Choose your traditions', desc: 'See your chart through Vedic, Western, Chinese, or all six at once. Each tradition reveals something different.' },
              { n: '3', title: 'Explore with AI or an expert', desc: 'Chat with Josi AI about what your chart means. Or book a session with a verified astrologer.' },
            ].map((step) => (
              <div key={step.n} className="text-center relative">
                <div className="w-16 h-16 mx-auto mb-6 rounded-full flex items-center justify-center text-xl font-display relative z-10"
                  style={{ background: '#000000', border: '2px solid #C8913A', color: '#C8913A' }}>{step.n}</div>
                <h3 className="text-lg font-medium mb-3" style={{ color: '#D4DAE6' }}>{step.title}</h3>
                <p className="text-sm" style={{ color: '#5B6A8A' }}>{step.desc}</p>
              </div>
            ))}
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
                <div className="w-[52px] h-[52px] flex-shrink-0 flex items-center justify-center rounded-lg overflow-hidden" style={{ background: t.bg }}>
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
          CLOSING MESSAGE
       ═══════════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4" style={{ borderTop: '1px solid #1A1A1A' }}>
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl md:text-[32px] md:leading-snug font-display mb-4" style={{ color: '#D4DAE6' }}>
            The sky has always been speaking
          </h2>
          <p className="text-[15px] font-reading leading-relaxed" style={{ color: '#5B6A8A' }}>
            Six ancient traditions listened. Now it&rsquo;s your turn.
          </p>
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
