import Link from 'next/link';

const tiers = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Start exploring — no commitment needed',
    features: [
      '3 birth charts',
      'Basic Vedic & Western',
      'Community access',
      'Chart calculator',
    ],
    cta: 'Get Started Free',
    ctaLink: '/auth/sign-up',
    highlight: false,
  },
  {
    name: 'Explorer',
    price: '$9.99',
    period: '/month',
    description: 'For curious minds diving deeper',
    features: [
      '25 birth charts',
      'All 6 traditions',
      '10 AI readings/month',
      'Dasha & transit reports',
      'Panchang access',
    ],
    cta: 'Start Exploring',
    ctaLink: '/auth/sign-up',
    highlight: false,
  },
  {
    name: 'Mystic',
    price: '$19.99',
    period: '/month',
    description: 'For seekers committed to self-understanding',
    features: [
      'Unlimited charts',
      'Unlimited AI readings',
      '2 consultations/month',
      'Compatibility analysis',
      'Neural Pathway Questions',
      'Muhurta & timing tools',
    ],
    cta: 'Go Mystic',
    ctaLink: '/auth/sign-up',
    highlight: true,
  },
  {
    name: 'Master',
    price: '$39.99',
    period: '/month',
    description: 'For professionals and power users',
    features: [
      'Everything in Mystic',
      '5 consultations/month',
      'Priority astrologer matching',
      'API access',
      'Custom chart exports',
      'Bulk chart generation',
    ],
    cta: 'Unlock Mastery',
    ctaLink: '/auth/sign-up',
    highlight: false,
  },
];

const faqs = [
  {
    q: 'Can I try Josi for free?',
    a: 'Yes. The Free tier gives you 3 birth charts across Vedic and Western traditions with no time limit. No credit card required.',
  },
  {
    q: 'What happens when I sign up?',
    a: 'Every account starts on the Free tier automatically. You can upgrade to a paid plan at any time from your dashboard.',
  },
  {
    q: 'Can I switch plans later?',
    a: 'Absolutely. Upgrade, downgrade, or cancel at any time. Changes take effect at the start of your next billing cycle.',
  },
  {
    q: 'What are Neural Pathway Questions?',
    a: 'Our unique feature that uses your chart placements to generate personalized psychological reflection prompts. Each session builds on your previous responses to deepen self-awareness.',
  },
  {
    q: 'How do consultations work?',
    a: 'Book verified professional astrologers for video, chat, or email sessions. Transparent pricing, honest reviews, and AI-generated session summaries so nothing gets lost.',
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen text-white" style={{ background: '#060A14' }}>

      {/* Glassmorphism nav */}
      <nav
        className="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-6 px-8 py-3 rounded-full"
        style={{
          background: 'rgba(10,15,30,0.60)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(200,145,58,0.15)',
        }}
      >
        <Link href="/" className="text-lg font-display tracking-tight text-white no-underline">Josi</Link>
        <div className="w-px h-5" style={{ background: 'rgba(200,145,58,0.3)' }} />
        <Link href="/pricing" className="text-sm font-medium transition-colors" style={{ color: '#C8913A' }}>Pricing</Link>
        <Link href="/chart-calculator" className="text-sm transition-colors hover:text-white" style={{ color: '#94A3B8' }}>Calculator</Link>
        <div className="w-px h-5" style={{ background: 'rgba(200,145,58,0.3)' }} />
        <Link href="/auth/login" className="text-sm transition-colors hover:text-white" style={{ color: '#94A3B8' }}>Sign In</Link>
      </nav>

      {/* Header */}
      <section className="pt-32 pb-16 px-4 text-center">
        <p className="font-semibold uppercase mb-4" style={{ fontSize: '10px', letterSpacing: '3px', color: '#C8913A' }}>
          Simple, Transparent Pricing
        </p>
        <h1 className="text-4xl md:text-5xl font-display mb-4" style={{ color: '#D4DAE6' }}>
          Begin where you are
        </h1>
        <p className="text-lg max-w-xl mx-auto" style={{ color: '#5B6A8A' }}>
          Every account starts free. Upgrade when you&rsquo;re ready for more depth.
        </p>
      </section>

      {/* Pricing Grid */}
      <section className="max-w-6xl mx-auto px-4 pb-24">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className="rounded-2xl p-7 flex flex-col"
              style={{
                background: tier.highlight ? 'rgba(200,145,58,0.06)' : 'rgba(17,24,40,0.30)',
                border: tier.highlight ? '1.5px solid rgba(200,145,58,0.35)' : '1px solid rgba(26,35,64,0.50)',
              }}
            >
              {tier.highlight && (
                <span
                  className="text-[10px] font-bold uppercase tracking-widest mb-3 self-start px-3 py-1 rounded-full"
                  style={{ background: 'rgba(200,145,58,0.15)', color: '#C8913A' }}
                >
                  Most Popular
                </span>
              )}
              <h3 className="text-xl font-display mb-1" style={{ color: '#D4DAE6' }}>{tier.name}</h3>
              <div className="mb-2">
                <span className="text-[36px] font-display" style={{ color: '#D4DAE6' }}>{tier.price}</span>
                <span className="text-sm ml-1" style={{ color: '#5B6A8A' }}>{tier.period}</span>
              </div>
              <p className="text-[13px] mb-6" style={{ color: '#5B6A8A' }}>{tier.description}</p>

              <div className="flex-1 space-y-3 mb-8">
                {tier.features.map((f) => (
                  <div key={f} className="flex items-start gap-2.5">
                    <span className="mt-0.5 text-sm" style={{ color: '#C8913A' }}>&#10003;</span>
                    <span className="text-[13px]" style={{ color: '#8B99B5' }}>{f}</span>
                  </div>
                ))}
              </div>

              <Link
                href={tier.ctaLink}
                className="block w-full text-center py-3 rounded-xl font-semibold text-sm transition-all hover:opacity-90"
                style={tier.highlight
                  ? { background: '#C8913A', color: '#060A14' }
                  : { border: '1px solid rgba(200,145,58,0.3)', color: '#C8913A' }
                }
              >
                {tier.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* All plans include */}
        <div className="mt-16 text-center">
          <p className="text-sm font-medium mb-6" style={{ color: '#5B6A8A' }}>All plans include</p>
          <div className="flex flex-wrap justify-center gap-x-8 gap-y-3">
            {[
              'Swiss Ephemeris precision',
              'Secure data encryption',
              'No ads, ever',
              'Cancel anytime',
              'Community access',
            ].map((item) => (
              <span key={item} className="flex items-center gap-2 text-[13px]" style={{ color: '#7B8CA8' }}>
                <span style={{ color: '#C8913A' }}>&#10003;</span>
                {item}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-3xl mx-auto px-4 pb-24" style={{ borderTop: '1px solid #151C30' }}>
        <div className="pt-24">
          <h2 className="text-2xl md:text-3xl font-display mb-12 text-center" style={{ color: '#D4DAE6' }}>
            Common questions
          </h2>
          <div className="space-y-8">
            {faqs.map((faq) => (
              <div key={faq.q}>
                <h3 className="text-[15px] font-semibold mb-2" style={{ color: '#D4DAE6' }}>{faq.q}</h3>
                <p className="text-[14px] leading-relaxed" style={{ color: '#5B6A8A' }}>{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="pb-24 px-4 text-center">
        <h2 className="text-2xl font-display mb-3" style={{ color: '#D4DAE6' }}>Ready to begin?</h2>
        <p className="mb-8" style={{ color: '#5B6A8A' }}>Start free. No credit card required.</p>
        <Link
          href="/auth/sign-up"
          className="inline-flex items-center px-8 py-4 rounded-xl font-semibold transition-all hover:opacity-90"
          style={{ background: '#C8913A', color: '#060A14' }}
        >
          Create Free Account
        </Link>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4" style={{ borderTop: '1px solid #151C30' }}>
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <span className="text-sm" style={{ color: '#3A4A6A' }}>&copy; 2026 Josi. All rights reserved.</span>
          <Link href="/auth/login" className="text-sm transition-colors hover:text-white" style={{ color: '#5B6A8A' }}>Sign In</Link>
        </div>
      </footer>
    </div>
  );
}
