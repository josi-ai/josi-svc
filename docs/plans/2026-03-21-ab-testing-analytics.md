# A/B Testing & Analytics for Josi Landing Page

**Date:** 2026-03-21
**Context:** Next.js 16 App Router, deployed on Cloud Run, Clerk auth, startup stage
**Goal:** Split traffic 50/50 between two landing page variants (Page A "Observatory" and Page B "Mirror"), track user behavior, and measure conversions.

---

## Table of Contents

1. [A/B Testing Options](#1-ab-testing-options)
2. [Recommendation: Custom Middleware + PostHog](#2-recommendation-custom-middleware--posthog)
3. [Implementation: 50/50 Split with Next.js Middleware](#3-implementation-5050-split-with-nextjs-middleware)
4. [Analytics Platform Comparison](#4-analytics-platform-comparison)
5. [Analytics Recommendation](#5-analytics-recommendation)
6. [Heatmaps & Session Recording](#6-heatmaps--session-recording)
7. [Conversion Tracking](#7-conversion-tracking)
8. [Full Integration Architecture](#8-full-integration-architecture)
9. [Cost Summary](#9-cost-summary)
10. [Implementation Checklist](#10-implementation-checklist)

---

## 1. A/B Testing Options

### Option A: Custom Next.js Middleware (DIY)

**How it works:** `middleware.ts` intercepts requests, assigns visitors to a variant via cookie, and uses `NextResponse.rewrite()` to serve different page content — all at the edge, zero CLS, no layout shift.

| Pros | Cons |
|------|------|
| Zero dependencies, zero cost | No built-in statistical analysis |
| Runs at the edge (fast) | Must build your own results dashboard |
| Full control over assignment logic | No multi-variate support out of the box |
| Works on any hosting (Cloud Run, Vercel, etc.) | Need separate analytics to measure results |

**Verdict:** Best for a startup that pairs it with an analytics tool (PostHog) for measurement.

### Option B: PostHog Experiments

**How it works:** PostHog feature flags control which variant a user sees. The `@posthog/next` package bootstraps flags server-side so there is no flicker. PostHog's experimentation engine handles statistical significance automatically.

| Pros | Cons |
|------|------|
| Built-in statistical significance calculator | Adds PostHog as a dependency for page rendering |
| Integrated with analytics (same tool measures results) | Feature flag evaluation adds ~50-100ms on first load if not bootstrapped |
| Server-side bootstrapping via middleware | Slightly more complex setup |
| Free tier: 1M feature flag requests/month | |

**Verdict:** Best all-in-one solution if you are already using PostHog for analytics.

### Option C: GrowthBook

**How it works:** Open-source A/B testing platform. SDK evaluates flags locally (no network calls). Deterministic hashing ensures consistent assignment. Integrates with your own analytics for results.

| Pros | Cons |
|------|------|
| Open source, free to self-host | Requires self-hosting or $40/seat/month for cloud |
| Local evaluation (fast, private) | Smaller community than PostHog |
| Warehouse-native: connects to your analytics DB | More setup overhead |
| Free cloud tier for up to 3 users | |

**Verdict:** Good if you want open-source and plan to self-host. Overkill for a single landing page test.

### Option D: Vercel Edge Config + Statsig

**How it works:** Vercel Edge Config stores experiment configuration, middleware reads it in <15ms. Statsig handles assignment and analysis.

| Pros | Cons |
|------|------|
| Ultra-fast Edge Config reads (0-15ms P99) | Vercel-specific (Josi is on Cloud Run) |
| Zero CLS experiments | Statsig has its own pricing |
| Official Vercel integration | Vendor lock-in to Vercel |

**Verdict:** Not applicable — Josi deploys to Cloud Run, not Vercel.

### Option E: LaunchDarkly

**How it works:** Enterprise feature flag platform with built-in experimentation.

| Pros | Cons |
|------|------|
| Industry standard for feature flags | Free tier limited to 1,000 client-side MAUs |
| Strong SDKs and integrations | $12/service connection/month on paid plan |
| | Enterprise-focused, overkill for startup |

**Verdict:** Too expensive and complex for a startup running one landing page test.

### Summary Matrix

| Tool | Cost | Complexity | Self-hosted | Stats Engine | Best For |
|------|------|-----------|-------------|-------------|----------|
| **Custom Middleware** | Free | Low | N/A | None (use PostHog) | Simple split tests |
| **PostHog Experiments** | Free (1M flags/mo) | Medium | Optional | Built-in | All-in-one analytics + experiments |
| **GrowthBook** | Free (self-host) | Medium-High | Yes | Built-in | Teams wanting open-source |
| **Vercel + Statsig** | Paid | Medium | No | Built-in | Vercel-deployed apps |
| **LaunchDarkly** | $12+/mo | High | No | Built-in | Enterprise |

---

## 2. Recommendation: Custom Middleware + PostHog

**For Josi's stage (pre-PMF startup, single A/B test, Cloud Run deployment), the best approach is:**

1. **Custom Next.js middleware** for the 50/50 split (zero dependencies, zero cost, zero latency)
2. **PostHog** for analytics, conversion tracking, and determining which variant wins (free tier: 1M events + 5K session recordings + 1M flag requests)
3. **Microsoft Clarity** as a free add-on for heatmaps and session recordings (unlimited, $0)

This stack costs $0 and gives you everything you need.

---

## 3. Implementation: 50/50 Split with Next.js Middleware

### 3.1 File Structure

```
web/
├── middleware.ts                          # A/B routing logic
├── app/
│   └── (public)/
│       ├── page.tsx                       # Existing landing — becomes router
│       ├── _variants/
│       │   ├── observatory/
│       │   │   └── page.tsx               # Variant A: "Observatory"
│       │   └── mirror/
│       │       └── page.tsx               # Variant B: "Mirror"
```

### 3.2 Middleware: Cookie-Based Sticky Assignment

```typescript
// web/middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { clerkMiddleware } from '@clerk/nextjs/server';

const AB_COOKIE = 'josi-landing-variant';
const AB_TEST_ID = 'landing-2026-03';

// Variants and their weights (must sum to 100)
const VARIANTS = [
  { id: 'observatory', weight: 50 },
  { id: 'mirror', weight: 50 },
] as const;

type VariantId = (typeof VARIANTS)[number]['id'];

function assignVariant(): VariantId {
  const rand = Math.random() * 100;
  let cumulative = 0;
  for (const variant of VARIANTS) {
    cumulative += variant.weight;
    if (rand < cumulative) return variant.id;
  }
  return VARIANTS[0].id; // fallback
}

function handleABTest(req: NextRequest): NextResponse | null {
  // Only apply to the landing page
  if (req.nextUrl.pathname !== '/') return null;

  // Check for existing assignment
  let variant = req.cookies.get(AB_COOKIE)?.value as VariantId | undefined;
  const isNewVisitor = !variant;

  // Assign if new visitor
  if (!variant || !VARIANTS.some((v) => v.id === variant)) {
    variant = assignVariant();
  }

  // Rewrite to the variant page (URL stays as /)
  const url = req.nextUrl.clone();
  url.pathname = `/_variants/${variant}`;
  const response = NextResponse.rewrite(url);

  // Set cookie for sticky session (30 days)
  if (isNewVisitor) {
    response.cookies.set(AB_COOKIE, variant, {
      maxAge: 60 * 60 * 24 * 30,
      path: '/',
      sameSite: 'lax',
      httpOnly: false, // readable by PostHog JS
    });
  }

  return response;
}

export default clerkMiddleware(async (auth, req) => {
  // A/B test handling (runs before Clerk auth)
  const abResponse = handleABTest(req);
  if (abResponse) return abResponse;

  // ... existing Clerk auth logic ...
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
```

### 3.3 Variant Pages

```typescript
// web/app/(public)/_variants/observatory/page.tsx
export default function ObservatoryLanding() {
  return (
    <main>
      {/* Variant A: "Observatory" design */}
      <h1>Your Cosmic Observatory</h1>
      {/* ... */}
    </main>
  );
}
```

```typescript
// web/app/(public)/_variants/mirror/page.tsx
export default function MirrorLanding() {
  return (
    <main>
      {/* Variant B: "Mirror" design */}
      <h1>Your Celestial Mirror</h1>
      {/* ... */}
    </main>
  );
}
```

### 3.4 Reading the Variant Client-Side (for PostHog tracking)

```typescript
// web/lib/ab-test.ts
export function getVariant(): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(/josi-landing-variant=(\w+)/);
  return match ? match[1] : null;
}
```

### 3.5 Alternative: Inline Variant Rendering (No Rewrite)

If you prefer to keep a single `page.tsx` rather than separate variant pages:

```typescript
// web/app/(public)/page.tsx
import { cookies } from 'next/headers';

export default async function LandingPage() {
  const cookieStore = await cookies();
  const variant = cookieStore.get('josi-landing-variant')?.value ?? 'observatory';

  if (variant === 'mirror') {
    return <MirrorLanding />;
  }
  return <ObservatoryLanding />;
}
```

This approach avoids the middleware rewrite entirely — the middleware only sets the cookie, and the page reads it server-side.

---

## 4. Analytics Platform Comparison

### 4.1 Full Comparison Table

| Feature | PostHog | Plausible | Mixpanel | Amplitude | GA4 |
|---------|---------|-----------|----------|-----------|-----|
| **Free tier** | 1M events/mo | None ($9/mo) | 1M events/mo | 100K MTU/mo | Unlimited (sampled) |
| **Open source** | Yes | Yes | No | No | No |
| **Event tracking** | Auto + custom | Page views + custom goals | Custom events | Custom events | Auto + custom |
| **Session recording** | 5K/mo free | No | Yes (new) | No | No |
| **Heatmaps** | Yes (clicks, scroll, rage) | No | Yes (new) | No | No |
| **Feature flags** | 1M requests/mo free | No | No | No | No |
| **A/B testing** | Built-in | No | No | Yes | No |
| **Surveys** | Yes | No | No | No | No |
| **Privacy/GDPR** | EU hosting option | Cookie-free, GDPR native | Compliant | Compliant | Complex |
| **Next.js SDK** | `@posthog/next` (official) | `next-plausible` | `mixpanel-browser` | `@amplitude/analytics-browser` | `@next/third-parties` |
| **Startup program** | $50K credits | None | Credits available | $500K credits | N/A |
| **Self-hostable** | Yes | Yes | No | No | No |
| **Best for** | Product analytics + experiments | Simple web analytics | Product managers | Enterprise analytics | Basic web traffic |

### 4.2 What Each Tool Actually Captures

**Page views only:** Plausible, GA4 (basic mode)

**Clicks, form interactions, custom events:** PostHog (autocapture), Mixpanel (manual), Amplitude (manual), GA4 (enhanced measurement)

**Scrolls, rage clicks, dead clicks:** PostHog (heatmaps), Microsoft Clarity (heatmaps)

**Full session recordings:** PostHog, Microsoft Clarity, Hotjar

**User journeys & funnels:** PostHog, Mixpanel, Amplitude, GA4

### 4.3 Pricing for Startups (Monthly Cost at 10K-50K Users)

| Tool | 10K MAU | 50K MAU | Notes |
|------|---------|---------|-------|
| **PostHog** | $0 | $0-50 | Free up to 1M events (~10-50K users at 20 events/user) |
| **Plausible** | $9 | $19 | Based on pageviews (10K-100K/mo plans) |
| **Mixpanel** | $0 | $0-280 | Free up to 1M events, then tiered |
| **Amplitude** | $0 | Custom | Free tier generous but limited features |
| **GA4** | $0 | $0 | Free but data is sampled, complex setup |
| **Clarity** | $0 | $0 | Always free, unlimited |

---

## 5. Analytics Recommendation

### Primary: PostHog (free tier)

PostHog is the clear winner for a startup with no existing analytics because it combines product analytics, session recording, feature flags, A/B testing, heatmaps, and surveys in one tool — all with a generous free tier.

**Why PostHog over alternatives:**
- 1M free events/month covers ~50K users at 20 events/user
- 5,000 free session recordings/month
- Built-in A/B testing with statistical significance
- Autocapture means you get click/interaction data with zero instrumentation
- `@posthog/next` package has first-class App Router support
- 90%+ of companies use PostHog for free
- $50K startup credits available
- Open source — can self-host later if needed

**What PostHog replaces:** Mixpanel + Hotjar + LaunchDarkly + SurveyMonkey = one tool.

### Secondary: Microsoft Clarity (free, always)

Add Clarity alongside PostHog for unlimited session recordings and heatmaps at zero cost. Clarity has no caps, no sampling, and provides:
- Click heatmaps, scroll heatmaps
- Full session recordings with no limit
- "Dead click" and "rage click" detection
- Integrates with GA4 if you add that later

### Optional: Plausible ($9/mo)

Only if you want a privacy-first, cookie-free dashboard for basic traffic metrics that you can share with non-technical stakeholders. Not essential — PostHog's web analytics dashboard covers this.

### Skip: GA4

GA4 is free but overcomplicated, samples data, and does not provide the behavioral insights (session recordings, heatmaps) that a startup needs to iterate quickly on a landing page. Add it later for SEO/marketing attribution if needed.

---

## 6. Heatmaps & Session Recording

### Comparison: Microsoft Clarity vs Hotjar vs PostHog

| Feature | Microsoft Clarity | Hotjar (Free) | PostHog (Free) |
|---------|-------------------|---------------|----------------|
| **Price** | Always free | Free (35 sessions/day) | 5,000 recordings/mo |
| **Session recordings** | Unlimited | 35/day | 5,000/mo |
| **Click heatmaps** | Yes | Yes | Yes |
| **Scroll heatmaps** | Yes | Yes | Yes |
| **Move/hover maps** | No | Yes | No |
| **Rage click detection** | Yes | No | Yes |
| **Dead click detection** | Yes | No | Yes |
| **Data retention** | 30 days | 365 days | 90 days (free) |
| **On-page surveys** | No | Yes (limited) | Yes |
| **Funnel analysis** | No | Yes (limited) | Yes |
| **Next.js integration** | Script tag | Script tag | `@posthog/next` SDK |
| **Privacy** | GDPR compliant | GDPR compliant | GDPR compliant, EU option |

### Recommendation

Use **both PostHog and Microsoft Clarity**:
- PostHog for integrated analytics + recordings + experiments
- Clarity for unlimited recordings and as a backup heatmap source (zero cost, no limits)

### Microsoft Clarity Integration

```typescript
// web/app/layout.tsx (or a dedicated component)
import Script from 'next/script';

const CLARITY_PROJECT_ID = process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        {CLARITY_PROJECT_ID && (
          <Script
            id="microsoft-clarity"
            strategy="afterInteractive"
          >
            {`
              (function(c,l,a,r,i,t,y){
                c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
                t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
              })(window, document, "clarity", "script", "${CLARITY_PROJECT_ID}");
            `}
          </Script>
        )}
      </body>
    </html>
  );
}
```

---

## 7. Conversion Tracking

### What to Track

For the landing page A/B test, define these conversion events:

| Event | Type | Trigger |
|-------|------|---------|
| `landing_page_view` | Auto | Page load (with variant property) |
| `cta_click` | Click | Primary CTA button ("Get Started", "Try Free") |
| `pricing_click` | Click | "View Pricing" link |
| `signup_start` | Navigation | User reaches `/auth/sign-up` |
| `signup_complete` | Webhook | Clerk webhook fires `user.created` |
| `scroll_depth` | Scroll | 25%, 50%, 75%, 100% of page |
| `feature_section_view` | Visibility | User scrolls to feature section |
| `time_on_page` | Timer | 30s, 60s, 120s thresholds |

### PostHog Event Tracking Code

```typescript
// web/lib/analytics.ts
import posthog from 'posthog-js';
import { getVariant } from './ab-test';

export function trackLandingView() {
  const variant = getVariant();
  posthog.capture('landing_page_view', {
    variant,
    ab_test: 'landing-2026-03',
  });
}

export function trackCTAClick(ctaLabel: string) {
  const variant = getVariant();
  posthog.capture('cta_click', {
    variant,
    ab_test: 'landing-2026-03',
    cta_label: ctaLabel,
  });
}

export function trackSignupStart() {
  const variant = getVariant();
  posthog.capture('signup_start', {
    variant,
    ab_test: 'landing-2026-03',
    $set: { landing_variant: variant },  // persists on user profile
  });
}

export function trackScrollDepth(percent: number) {
  posthog.capture('scroll_depth', {
    variant: getVariant(),
    ab_test: 'landing-2026-03',
    depth_percent: percent,
  });
}
```

### Scroll Depth Tracking Component

```typescript
// web/components/analytics/scroll-tracker.tsx
'use client';

import { useEffect, useRef } from 'react';
import { trackScrollDepth } from '@/lib/analytics';

const THRESHOLDS = [25, 50, 75, 100];

export function ScrollTracker() {
  const tracked = useRef(new Set<number>());

  useEffect(() => {
    function handleScroll() {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const percent = Math.round((scrollTop / docHeight) * 100);

      for (const threshold of THRESHOLDS) {
        if (percent >= threshold && !tracked.current.has(threshold)) {
          tracked.current.add(threshold);
          trackScrollDepth(threshold);
        }
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return null;
}
```

### Measuring Winners in PostHog

Once events are flowing, create a PostHog **Experiment** (or use **Insights** with breakdown by variant):

1. **Funnel insight:** `landing_page_view` → `cta_click` → `signup_start` → `signup_complete`
2. **Break down by:** `variant` property
3. **Goal metric:** Conversion rate from `landing_page_view` to `signup_complete`
4. **Secondary metrics:** CTA click rate, scroll depth distribution, time on page

PostHog's experimentation engine will calculate statistical significance and tell you when you have enough data to declare a winner (typically 100-500 conversions per variant).

---

## 8. Full Integration Architecture

### Package Installation

```bash
cd web
npm install posthog-js @posthog/next
```

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
NEXT_PUBLIC_CLARITY_PROJECT_ID=xxxxxxxxxx
```

### PostHog Provider Setup

```typescript
// web/components/providers/posthog-provider.tsx
'use client';

import posthog from 'posthog-js';
import { PostHogProvider as PHProvider, usePostHog } from 'posthog-js/react';
import { usePathname, useSearchParams } from 'next/navigation';
import { useEffect, Suspense } from 'react';

if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_POSTHOG_KEY) {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
    capture_pageview: false, // we capture manually for SPA navigation
    capture_pageleave: true,
    autocapture: true,
    enable_heatmaps: true,
  });
}

function PostHogPageView() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const ph = usePostHog();

  useEffect(() => {
    if (pathname && ph) {
      let url = window.origin + pathname;
      if (searchParams.toString()) {
        url += '?' + searchParams.toString();
      }
      ph.capture('$pageview', { $current_url: url });
    }
  }, [pathname, searchParams, ph]);

  return null;
}

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  return (
    <PHProvider client={posthog}>
      <Suspense fallback={null}>
        <PostHogPageView />
      </Suspense>
      {children}
    </PHProvider>
  );
}
```

### Wire Into Root Layout

```typescript
// web/app/layout.tsx — add PostHogProvider alongside existing providers
import { PostHogProvider } from '@/components/providers/posthog-provider';

// In the layout JSX, wrap children:
<PostHogProvider>
  {/* existing providers and children */}
</PostHogProvider>
```

### Proxy PostHog Requests (Avoid Ad Blockers)

```typescript
// web/next.config.ts
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/ingest/static/:path*',
        destination: 'https://us-assets.i.posthog.com/static/:path*',
      },
      {
        source: '/ingest/:path*',
        destination: 'https://us.i.posthog.com/:path*',
      },
      {
        source: '/ingest/decide',
        destination: 'https://us.i.posthog.com/decide',
      },
    ];
  },
  // If using the proxy, update skipTrailingSlashRedirect:
  skipTrailingSlashRedirect: true,
};

export default nextConfig;
```

Then update the PostHog init to use the proxy:

```typescript
posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
  api_host: '/ingest',  // use proxy instead of direct
  ui_host: 'https://us.i.posthog.com',
});
```

---

## 9. Cost Summary

### Recommended Stack: $0/month

| Tool | What It Covers | Monthly Cost | Limits |
|------|---------------|-------------|--------|
| **Custom Middleware** | A/B split routing | $0 | Unlimited |
| **PostHog (free tier)** | Analytics, experiments, session replay, heatmaps | $0 | 1M events, 5K recordings, 1M flag requests |
| **Microsoft Clarity** | Heatmaps, session recordings (unlimited) | $0 | No limits |
| **Total** | | **$0** | |

### When You Outgrow Free Tiers

At ~50K MAU (assuming 20 events/user = 1M events/month), PostHog starts at $0.00031/event. Estimated costs:

| MAU | PostHog Cost | Clarity | Total |
|-----|-------------|---------|-------|
| 10K | $0 | $0 | $0 |
| 50K | $0-50 | $0 | ~$50 |
| 100K | ~$300 | $0 | ~$300 |
| 500K | ~$1,500 | $0 | ~$1,500 |

PostHog's startup program offers $50K in credits — apply at posthog.com/startups.

---

## 10. Implementation Checklist

### Phase 1: A/B Test Infrastructure (Day 1)

- [ ] Create `web/middleware.ts` with cookie-based 50/50 split logic
- [ ] Create `web/app/(public)/_variants/observatory/page.tsx`
- [ ] Create `web/app/(public)/_variants/mirror/page.tsx`
- [ ] Test locally: clear cookies, verify 50/50 assignment, verify sticky sessions
- [ ] Verify Clerk middleware still works alongside A/B routing

### Phase 2: PostHog Analytics (Day 1-2)

- [ ] Create PostHog account (posthog.com, select US or EU cloud)
- [ ] `npm install posthog-js @posthog/next`
- [ ] Add `NEXT_PUBLIC_POSTHOG_KEY` and `NEXT_PUBLIC_POSTHOG_HOST` to `.env.local` and Cloud Run secrets
- [ ] Create `web/components/providers/posthog-provider.tsx`
- [ ] Wire PostHogProvider into `web/app/layout.tsx`
- [ ] Add PostHog proxy rewrites in `next.config.ts` (bypass ad blockers)
- [ ] Verify events appear in PostHog dashboard

### Phase 3: Conversion Tracking (Day 2-3)

- [ ] Create `web/lib/analytics.ts` with event helper functions
- [ ] Add `variant` property to all landing page events
- [ ] Track CTA clicks on both variant pages
- [ ] Add `ScrollTracker` component to both variants
- [ ] Track navigation to `/auth/sign-up` as `signup_start`
- [ ] Create PostHog funnel: page_view → cta_click → signup_start → signup_complete
- [ ] Set up PostHog Experiment or Insight with variant breakdown

### Phase 4: Heatmaps & Session Recording (Day 2-3)

- [ ] Enable PostHog heatmaps (`enable_heatmaps: true` in init config)
- [ ] Enable PostHog session recording in project settings
- [ ] Create Microsoft Clarity account (clarity.microsoft.com)
- [ ] Add Clarity script to root layout
- [ ] Verify heatmaps and recordings appear in both dashboards

### Phase 5: Analyze & Decide (Week 2-4)

- [ ] Wait for statistical significance (typically 100-500 conversions per variant)
- [ ] Compare conversion rates between Observatory and Mirror
- [ ] Review session recordings for drop-off patterns
- [ ] Review heatmaps for click/scroll patterns
- [ ] Declare winner and remove losing variant
- [ ] Clean up: remove middleware A/B logic, remove cookie, promote winner to `/`

---

## Sources

### A/B Testing
- [PostHog: How to set up Next.js A/B tests](https://posthog.com/tutorials/nextjs-ab-tests)
- [Vercel: How to run A/B tests with Next.js](https://vercel.com/blog/ab-testing-with-nextjs-and-vercel)
- [Vercel: Zero-CLS A/B tests with Edge Config](https://vercel.com/blog/zero-cls-experiments-nextjs-edge-config)
- [Builder.io: A/B Testing with Next.js Edge Middleware](https://www.builder.io/blog/ab-testing-and-personalization-with-nextjs-edge-middleware)
- [Plasmic: A/B testing with Next.js middleware](https://www.plasmic.app/blog/nextjs-ab-testing)
- [GrowthBook: Next.js App Router Integration](https://docs.growthbook.io/guide/nextjs-app-router)
- [GrowthBook: Vercel Edge Config Integration](https://docs.growthbook.io/guide/nextjs-and-vercel-feature-flags)
- [LaunchDarkly Pricing](https://launchdarkly.com/pricing/)
- [GrowthBook Pricing](https://www.growthbook.io/pricing)

### Analytics
- [PostHog: Next.js Documentation](https://posthog.com/docs/libraries/next-js)
- [PostHog Pricing](https://posthog.com/pricing)
- [PostHog vs Mixpanel](https://posthog.com/blog/posthog-vs-mixpanel)
- [PostHog vs Plausible](https://posthog.com/blog/posthog-vs-plausible)
- [Brainforge: Amplitude vs Mixpanel vs PostHog](https://www.brainforge.ai/resources/amplitude-vs-mixpanel-vs-posthog)
- [F3 Fund It: Solopreneur Analytics Stack 2026](https://f3fundit.com/the-solopreneur-analytics-stack-2026-posthog-vs-plausible-vs-fathom-analytics-and-why-you-should-ditch-google-analytics/)
- [Vemetric: PostHog vs Google Analytics](https://vemetric.com/blog/posthog-vs-google-analytics)
- [next-plausible on npm](https://www.npmjs.com/package/next-plausible)
- [Next.js: Google Analytics with @next/third-parties](https://nextjs.org/docs/messages/next-script-for-ga)
- [GA4 Implementation Guide for Next.js 16](https://medium.com/@aashari/google-analytics-ga4-implementation-guide-for-next-js-16-a7bbf267dbaa)

### Heatmaps & Session Recording
- [Heatmap.com: Microsoft Clarity vs Hotjar](https://www.heatmap.com/blog/microsoft-clarity-vs-hotjar)
- [Userpilot: Microsoft Clarity vs Hotjar](https://userpilot.com/blog/microsoft-clarity-vs-hotjar/)
- [Crazy Egg: Microsoft Clarity vs Hotjar](https://www.crazyegg.com/blog/microsoft-clarity-vs-hotjar/)
- [PostHog: Heatmaps Documentation](https://posthog.com/docs/toolbar/heatmaps)
- [PostHog: Heatmaps Product Page](https://posthog.com/heatmaps)
- [DEV Community: Integrate Microsoft Clarity with Next.js App Router](https://dev.to/chamupathi_mendis_cdd19da/integrate-ms-clarity-to-nextjs-app-app-router--241o)
- [Will Fox: Add Microsoft Clarity to Next.js](https://www.willfox.dev/add-microsoft-clarity-to-your-next-js-app)

### PostHog Next.js Integration
- [PostHog: Next.js middleware feature flag bootstrapping](https://posthog.com/tutorials/nextjs-bootstrap-flags)
- [@posthog/next on npm](https://www.npmjs.com/package/@posthog/next)
- [Vercel: PostHog with Next.js App Router](https://vercel.com/kb/guide/posthog-nextjs-vercel-feature-flags-analytics)
- [PostHog: Next.js App Directory Analytics](https://posthog.com/tutorials/nextjs-app-directory-analytics)
