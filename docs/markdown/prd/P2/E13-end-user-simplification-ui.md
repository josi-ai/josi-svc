---
prd_id: E13
epic_id: E13
title: "End-User Simplification UI — Chat-First Consumer Surface"
phase: P2-breadth
tags: [#end-user-ux, #ai-chat, #i18n, #correctness, #performance]
priority: must
depends_on: [E11a, E11b, F9, F10, F11, F12]
enables: [D1, D3, D5, D6, I6]
classical_sources: []
estimated_effort: 6-8 weeks
status: draft
author: @agent
last_updated: 2026-04-19
---

# E13 — End-User Simplification UI

## 1. Purpose & Rationale

The end-user is not an astrologer. They do not want to choose an aggregation strategy, they do not want to know the difference between Saravali and Phaladeepika, and they do not want a 10-tab workbench. They want one thing: *a trustworthy, plain-language answer to a personal question about their life*.

Every successful consumer astrology product in the last decade — Co-Star, The Pattern, Sanctuary — wins by relentless simplification. Josi's defensible advantage over them is *depth and source honesty* (debate mode, citations, classical breadth). But that advantage only converts if the surface that exposes it to end-users is simpler than theirs, not more complex. E13 is that surface.

The thesis of this PRD is "chat-first": the primary CTA on every page is "Ask anything about your chart." The AI response is the dominant UI element. Everything else — chart view, daily insights, settings — is secondary and progressively-disclosed. One-paragraph answers by default; "Want more?" expands to citations and reasoning. The depth is always *one tap away*, never in front of the user by default.

The second thesis is **confidence-tuned honesty**. Josi never pretends to certainty it doesn't have. Low-confidence claims are phrased hesitantly ("some classical traditions see…") not strongly. This is how Josi earns long-term trust from educated users who have been burned by over-confident LLM-wrappers.

The third thesis is **global reach from launch**. 10+ languages at launch, with Sanskrit technical terms always tooltipped in the user's UI language. The Indian diaspora and Tamil-speaking community are first-class audiences, not afterthoughts.

Commercial framing: E13 is the surface on which most Free / Explorer / Mystic-tier users will spend 90% of their time. Chat question volume, daily-insight engagement, and drill-down tap rate are the primary B2C product metrics.

## 2. Scope

### 2.1 In scope

**Information architecture — chat-first, 4 primary destinations**

- **Home** — greeting, 3 daily insights (AI-generated), one hero CTA: "Ask anything."
- **Chat** — primary working surface; same chat engine as E11a/E11b, simplified chrome.
- **My Chart** — minimal summary; planets + signs; progressive disclosure to houses, aspects, yogas, dasa on tap.
- **Settings** — profile, source/tradition preference (simplified: "Which tradition guides you?"), language, notifications, privacy.

Mobile bottom navigation: Home / Chat / My Chart / Settings.
Desktop: same 4 destinations as horizontal nav; Chat takes center panel by default.

**Chat as the primary interaction**

- Dominant UI element on every screen is a "Ask anything about your chart…" input. On Home, it's the hero. On My Chart, it's anchored at bottom. On Chat, it's the composer.
- Single tap opens the chat with the typed question pre-submitted.
- Conversations carry across surfaces; unread indicator on bottom nav.

**One-paragraph answers by default**

- AI response presents as a single well-written paragraph (≤ 3 sentences typical).
- Below the paragraph: "Want more?" button. Tap expands to:
  - Longer reasoning (2–3 paragraphs)
  - Classical citation chips
  - "Why?" affordance per claim (drill-down per E11b)
  - Debate-mode toggle (Mystic+ surfaces the four strategies)

**Confidence-tuned tone**

- Claude system prompt (extended from F11) maps confidence buckets to specific phrasings:
  - ≥ 0.85: "This strongly supports…"
  - 0.60 – 0.85: "Classical sources indicate…"
  - 0.40 – 0.60: "Some traditions see…"
  - < 0.40: "This is contested — only [source] holds that…"
- Colors on the UI reflect the same bucket: confident (teal), neutral (slate), contested (amber-low-contrast). Never red — contested is not "wrong."

**Daily/weekly summary cards**

- Home shows 3 AI-generated insights per day, recomputed lazily at 6 am local time:
  1. Current dasa highlight ("Jupiter Mahadasa is expansive — consider…")
  2. Major transit of the day
  3. Personalized question prompt ("Would you like to explore…?")
- Weekly digest (Sunday) is a longer-form summary card.
- Delivered as push notifications (opt-in): cards tap through to chat with the topic pre-scoped.
- Backend: new worker generates summaries; stored in `daily_insight` table keyed by `(user_id, chart_id, date)`.

**Minimal chart view**

- Default render: user's selected style (North Indian default for Indian locale; Western wheel default otherwise).
- Planets + zodiac signs only by default — no house lines, no aspects, no yogas.
- Tap to reveal: houses, then aspects, then yogas (progressive taps).
- Above the chart: "Ask about your chart" button anchored.
- No other tabs; no workbench-style depth on this surface.

**"Why?" drill-downs**

- Every claim in chat responses is clickable.
- Tapping expands inline (not modal) to a compact drill-down: one-line citation + confidence bar. "See the verse" link opens a fuller classical citation modal.
- Preserves the E11b drill-down backend; UI is mobile-simplified.

**Progressive disclosure**

- **First-visit state (new user):** only Home + Chat visible. My Chart and Settings accessible via "more" menu.
- **Level 2 (after 5 questions asked):** My Chart becomes prominent in nav.
- **Level 3 (after "Why?" clicked 3 times):** "See classical source" button appears in chat responses by default.
- **Power-user opt-in:** Settings has a "Show me everything" toggle that disables progressive disclosure; shows full UI unconditionally.
- Progression tracked in `user_feature_reveal` table (user_id, feature_key, revealed_at).

**Onboarding**

- Reuses existing 3-step wizard (per CLAUDE.md memory: onboarding is mandatory for new users).
- Wizard collects: birth date/time/place → computes chart → user identifies tradition/style preference → drops them into Home with first AI greeting.
- Post-onboarding: Home displays a prominent "Try asking: [suggested question]" card on first visit.

**Mobile-first**

- Designed for 375px portrait first; desktop enhances, doesn't transform.
- Bottom navigation on mobile; side nav on desktop (same destinations).
- Chat scales from fullscreen mobile to centered column desktop (max-width 768px for readability).
- Voice-preview (from E11b) surfaced as a play button on every assistant message (Mystic+).
- Haptic feedback on iOS: subtle tap on "Send," confirmation on "Expand."

**Accessibility**

- Min 16px base font; user-scalable up to 24px.
- Screen reader: assistant messages announced with role / confidence ("Strongly supports, [message]"); chart view has full ARIA description.
- Color-blind safe palette (same as E12 pass).
- Keyboard nav parity with mouse/touch.
- Reduced-motion mode for users with vestibular disorders (no chart-view animations, no progressive disclosure fade-ins).

**Internationalization — 10 languages at launch**

- English, Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam, Gujarati, Punjabi.
- Message catalogs managed via `next-intl`; translation workflow documented.
- Sanskrit technical terms rendered through `<SanskritTerm>` component with plain-language meaning in the user's UI language.
- Date/time formatting: locale-aware; user-selectable calendar.
- Per-language AI response: Claude prompted with UI language; voice preview (E11b) uses same language for TTS voice selection.

**Performance**

- Chat response streaming begins within **500 ms of send** (P95).
- Home first meaningful paint < 1.5 s on 3G (throttled Lighthouse CI).
- Chart view renders within 200 ms of "My Chart" tap.
- Lazy-load all non-critical bundles; Home is the critical bundle.
- Offline fallback: last chat session and today's daily insights available offline.

### 2.2 Out of scope

- **Marketplace / astrologer bookings** — D4 + consultations UI already exists; may be linked from Settings but not a primary destination in E13.
- **Community features** (share your chart publicly, comments) — future.
- **Advanced chart customization** (custom rulership schemes, custom dasa systems) — astrologer workbench territory.
- **Biometric data integration** (Apple Health, Oura, WHOOP) — D5 in P5.
- **Longitudinal personal dashboard** (trends over months) — D6 in P5.
- **Voice-native two-way conversation** — D1 in P5.
- **Payments / subscription management UI** — exists separately (`web/app/(dashboard)/settings/billing` or equivalent); linked from Settings.
- **Multi-chart switching** (family charts) — deferred; v1 binds one user to one chart.
- **Chart creation flow from chat** — user must complete onboarding wizard; no mid-chat chart creation.
- **Native mobile app** — responsive PWA at launch; native app is a separate track.
- **Admin / moderator tooling** — internal, not E13.
- **Non-user-initiated push notifications beyond daily/weekly cards** — no marketing pushes in E13.

### 2.3 Dependencies

- **E11a** — chat orchestration + SSE streaming.
- **E11b** — drill-down, voice preview, debate mode (tier-gated).
- **F9** — `chart_reading_view` supplies chart data + summaries for Home cards.
- **F10/F11** — typed tools + CitedFact envelope.
- **F12** — prompt caching keeps chat latency low.
- **Onboarding wizard** — already shipped; E13 requires its output (user has chart).
- **Clerk auth** — already integrated.
- **User model** — `ui_language`, `tradition_preference`, `show_full_ui` columns (some new; see §5.2).
- **`next-intl`** — localization framework (introduced in E12; reused here).

## 3. Technical Research

### 3.1 Why chat-first (not dashboard-first)

Competitive landscape: Co-Star's horoscope-card model, The Pattern's event-card model, Sanctuary's "ask an astrologer" model. The winning consumer pattern in 2024–2026 is *conversational* — ChatGPT and Claude have reset user expectations. A dashboard of 20 widgets overwhelms a user who came to ask "is this a good week to change jobs?"

Chat-first has three advantages for Josi:

1. **Single surface** for arbitrarily complex questions — no UI redesign required as engines expand (P3/P4 new techniques are automatically chat-accessible via F10 tools).
2. **Natural progressive disclosure** — the answer is the answer; depth is opt-in via "Want more?"
3. **AI's cost curve is our ally** — per-request cost drops ~50% per year; chat gets cheaper to deliver while more accurate.

A "dashboard" still exists, but it's tiny and secondary: Home shows 3 AI-generated cards plus the chat CTA. My Chart is a quiet reference view, not a workbench.

### 3.2 One-paragraph answer prompt engineering

The Claude system prompt used by E13 chat sessions differs from E11a's:

```
Role: Josi, a warm and trustworthy astrology guide.
Audience: a general-interest user, not a professional.
Response style:
  - Default to a single well-written paragraph (≤ 3 sentences).
  - Close with an inviting follow-up question or CTA ("Would you like to explore the dasa context?").
  - Use the confidence-tuning phrase table (F11 §3.3).
  - Never use raw source_ids or technical jargon unless explicitly asked.
  - Sanskrit terms may appear when relevant; always parenthesize the plain-language meaning.
Length control:
  - If user asks "why?" or "tell me more", you may expand to 2–3 paragraphs.
  - Cite classical sources via display name only (not raw id).
Tone:
  - Warm, not clinical.
  - Honest about uncertainty; never over-confident.
  - Never medical/legal/financial advice; include gentle disclaimer when questions drift there.
```

System prompt is a cached breakpoint (F12). Changes bump the prompt version and cache key.

### 3.3 Confidence-tuned tone — implementation detail

On the frontend, each `CitedFact<T>` used in a chat message is classified into a confidence bucket client-side:

```ts
type ConfidenceBucket = 'high' | 'medium' | 'low' | 'contested';

function toBucket(c: number): ConfidenceBucket {
  if (c >= 0.85) return 'high';
  if (c >= 0.60) return 'medium';
  if (c >= 0.40) return 'low';
  return 'contested';
}
```

CSS variables:

```css
--confidence-high: var(--teal-300);
--confidence-medium: var(--slate-300);
--confidence-low: var(--amber-200);
--confidence-contested: var(--amber-400);
```

Claim spans in message text receive an underline in the bucket color. Mini confidence bar on drill-down shows the exact numeric.

### 3.4 Daily insight generation

Backend worker runs at user's local 6 am (derived from chart's birth location or user-set timezone). For each active user with a chart and opt-in:

1. Fetch current `chart_reading_view` for the user.
2. Select 3 relevant angles: (a) dominant current dasa, (b) top transit of the day, (c) conversation-starter prompt.
3. Call Claude with a compact prompt ("generate 3 insights") returning a JSON list.
4. Persist to `daily_insight` table with TTL; push to client via Firebase Cloud Messaging (if opted in).

Cost-control: insights are cached per chart + date; generated at most once per user per day. If a chart's dasa/transit didn't change from yesterday, we re-issue yesterday's insight (cheap).

Weekly digest: generated Sunday 6 am; longer-form; always new.

### 3.5 Progressive disclosure — how features unlock

State tracked in a `user_feature_reveal` table. Feature keys include:

- `my_chart_prominent` — reveal after 5 chat questions
- `see_source_default` — reveal after 3 "Why?" taps
- `debate_mode_hint` — reveal after Mystic upgrade
- `voice_preview_hint` — reveal after Mystic upgrade

When the app boots, it queries `/api/v1/me/feature-reveal` and renders the unlocked set. "Show me everything" toggle in Settings bypasses this (writes all keys as revealed).

This is intentionally lightweight — no gamification, no badges, just a quiet unfold as the user engages. Revealing a feature triggers a single subtle in-product hint the first time.

### 3.6 Mobile-first design choices

- **Bottom-nav over hamburger:** thumb-reachable; the four destinations are the entire app.
- **Chat composer is always reachable** with the thumb: sticky bottom on Home, anchored below chart on My Chart.
- **No carousels on mobile primary flows** — carousels hide content and increase tap count; progressive disclosure is preferred.
- **Large-tap-target rule** — 44×44 pt minimum (WCAG AAA).
- **Haptic feedback on key actions** (iOS only; light impact for send, success for expand).

### 3.7 Offline strategy

Service worker caches:
- Last 50 chat messages of the current session.
- Today's daily insights.
- User's chart view (last computed).
- UI shell and i18n bundle for active language.

When offline, the chat composer disables with a "You're offline — your question will send when you reconnect" banner. Cached content is read-only.

### 3.8 Analytics

Lightweight, privacy-respecting analytics:
- Feature-reveal progression (aggregate, no individual user IDs client-side).
- Chat question volume, length, language distribution.
- Drill-down tap rate, debate-mode activation rate.
- Daily-insight notification open rate.
- Tier conversion after specific events (e.g., upgrade modal after Debate-mode click).

Tracked via existing telemetry layer (event name + coarse bucket; no PII).

### 3.9 Alternatives considered

| Alternative | Rejected because |
|---|---|
| Dashboard-first with chat as one widget | Over-familiar; muddles the chat-first thesis; competes with competitive offerings on their terms |
| Single-destination fullscreen chat (no nav) | Loses chart reference; users want to peek at their chart |
| Full chart details on My Chart by default | Overwhelms on first visit; progressive disclosure is the right principle |
| Gamified progression (badges, levels) | Feels manipulative; users come for reflection, not games |
| Cards-based feed (Instagram / Co-Star pattern) | Passive; Josi's value is in conversation, not scrolling |
| Astrologer-first copy tone ("your lagna lord in the 5th...") | Alienates general-interest users |
| One-app-per-language | Linguistic fragmentation; i18n within one app is correct |
| Client-side LLM (privacy win) | Impossible at Josi's model size and latency needs |
| No onboarding wizard, chat-to-generate-chart | Brittle; users drop off; the wizard is already shipped per CLAUDE.md memory |

## 4. Open Questions Resolved

| Question | Decision | Rationale |
|---|---|---|
| Chat-first vs dashboard-first | Chat-first | Competitive thesis; AI is the moat |
| Number of daily insights | 3 | More is noise; fewer is thin |
| Weekly digest | Sunday 6 am local | Pre-week reflection; culturally universal |
| Default chart style | North Indian for Indian locale; Western wheel otherwise | Cultural default |
| Minimal chart default layers | Planets + signs only | Progressive disclosure |
| Confidence color scheme | Teal / slate / amber-low / amber-high | Never red; contested ≠ wrong |
| Drill-down presentation on mobile | Inline expansion, not modal | Modals break flow on small screens |
| Drill-down presentation on desktop | Inline, with option to "open classical source" side-drawer | Same primitive scaled up |
| Onboarding | Reuse existing 3-step wizard | Already shipped; no re-invention |
| Progressive disclosure override | "Show me everything" toggle in Settings | Respect power-user choice |
| Feature reveal storage | `user_feature_reveal` table (server) | Cross-device consistency |
| Languages at launch | 10 (en, hi, ta, te, bn, mr, kn, ml, gu, pa) | Indian market + Indian diaspora + English |
| AI response language | Match UI language | Consistency |
| Sanskrit term rendering | Devanagari + roman + UI-language tooltip | Classical fidelity + accessibility |
| Push notification opt-in | Opt-in required (default off) | Respect user attention |
| Offline capability | Service worker with last-50-messages + daily insights | Engagement + resilience |
| Tier gating UI | Inline upgrade modal with preview image | Consistent with E11b |
| Voice preview surface | Play button on assistant messages, Mystic+ only | Natural placement |
| Debate mode access point | Chat header toggle, Mystic+ only | Progressive reveal |
| Analytics | Aggregate, privacy-respecting | Avoid PII |
| Chart viewing — fullscreen or inline | Inline by default; fullscreen on tap | Reduce modality |
| SSR policy | Public pages SSR; all post-auth pages client-only (per CLAUDE.md) | Hydration safety |
| Keyboard shortcuts | Minimal; power users can enable via Settings | Consumer surface |

## 5. Component Design

### 5.1 Route tree

```
web/app/(dashboard)/
├── layout.tsx                              # DashboardShell (existing, client-only)
├── page.tsx                                # Home
├── chat/
│   ├── page.tsx                            # primary chat surface
│   └── [sessionId]/page.tsx                # specific session
├── my-chart/
│   └── page.tsx
├── settings/
│   ├── page.tsx                            # index
│   ├── profile/page.tsx
│   ├── tradition/page.tsx                  # "which tradition guides you?"
│   ├── language/page.tsx
│   ├── notifications/page.tsx
│   ├── privacy/page.tsx
│   └── advanced/page.tsx                   # "show me everything" toggle
└── (deprecated dashboard pages retained behind redirects for backwards compat)
```

Note: workbench lives at `(pro)/workbench` from E12 and is not accessible from the end-user (dashboard) shell. Role-based gate on the (pro) route group.

### 5.2 Components

```
web/components/chat/
├── chat-surface.tsx                        # container for message list + composer
├── message-list.tsx                        # virtualized
├── message-assistant.tsx                   # one paragraph + Want-more affordance
├── message-user.tsx
├── composer.tsx                            # text input + send (sticky-bottom)
├── composer-voice.tsx                      # voice-to-text (future D1 scaffold)
├── want-more-button.tsx                    # reveals expanded reasoning
├── expanded-reasoning.tsx                  # the expanded view
├── claim-span.tsx                          # inline clickable claim with confidence underline
├── drill-down-inline.tsx                   # mobile-optimized inline expansion
├── drill-down-drawer.tsx                   # desktop-optimized side drawer
├── citation-chip.tsx                       # compact display-name chip
├── confidence-bar.tsx                      # mini horizontal bar
├── debate-toggle.tsx                       # Mystic+ in chat header
├── voice-play-button.tsx                   # Mystic+ per-message
└── chat-empty-state.tsx                    # first-visit state with suggested questions

web/components/home/
├── daily-insight-card.tsx
├── insight-header.tsx
├── ask-anything-cta.tsx                    # hero CTA
├── weekly-digest-card.tsx
└── home-greeting.tsx                       # "Good morning, [name]"

web/components/my-chart/
├── chart-surface.tsx                       # chart render + ask-anything anchor
├── chart-layer-toggle.tsx                  # planets → +houses → +aspects → +yogas
├── minimal-chart-view.tsx
├── chart-style-switch.tsx                  # North Indian / Western
└── chart-disclosure-badge.tsx              # "tap to see more" prompt

web/components/settings/
├── tradition-picker.tsx                    # "Which tradition guides you?"
├── language-picker.tsx
├── notification-preferences.tsx
├── show-full-ui-toggle.tsx
└── account-row.tsx

web/components/common/
├── sanskrit-term.tsx                       # shared with E12
├── confidence-label.tsx
├── bottom-nav.tsx                          # mobile
├── side-nav.tsx                            # desktop
├── upgrade-modal.tsx                       # tier gating
├── offline-banner.tsx
└── reduced-motion-guard.tsx                # respects prefers-reduced-motion

web/components/onboarding/
└── (existing wizard, unchanged)
```

Each ≤ 300 lines. Tight scopes.

### 5.3 Types

```
web/types/
├── chat-e13.ts                             # MessageView, ExpandedReasoningView, ClaimView
├── daily-insight.ts                        # DailyInsight, WeeklyDigest
├── my-chart-view.ts                        # MinimalChartData, DiscloseLayer
├── settings-user.ts                        # UserSettings, TraditionId, LanguageCode
├── feature-reveal.ts                       # FeatureKey, FeatureRevealState
└── index.ts                                # re-exports
```

Example:

```ts
export type TraditionId = 'vedic' | 'western' | 'hybrid';
export type LanguageCode =
  | 'en' | 'hi' | 'ta' | 'te' | 'bn' | 'mr' | 'kn' | 'ml' | 'gu' | 'pa';
export type ConfidenceBucket = 'high' | 'medium' | 'low' | 'contested';

export interface MessageView {
  messageId: string;
  role: 'user' | 'assistant';
  content: string;
  confidenceBucket?: ConfidenceBucket;
  claims: ClaimView[];
  expandedAvailable: boolean;
  voiceAvailable: boolean;
}

export interface ClaimView {
  claimIndex: number;
  textSpan: [number, number];
  confidenceBucket: ConfidenceBucket;
  citationDisplayName: string;
}
```

TanStack Query usage (transform in queryFn per CLAUDE.md):

```ts
const { data: messages = [] } = useQuery<MessageView[]>({
  queryKey: ['chat-session-messages', sessionId],
  queryFn: async () => {
    const res = await apiClient.get<{ data: { messages: ChatMessageRaw[] } }>(
      `/api/v1/ai/chat/sessions/${sessionId}`,
    );
    return res.data.data.messages.map(toMessageView);
  },
});
```

### 5.4 Data model additions

```sql
-- E13: user UI preferences
ALTER TABLE "user"
    ADD COLUMN ui_language TEXT NOT NULL DEFAULT 'en'
        CHECK (ui_language IN
          ('en','hi','ta','te','bn','mr','kn','ml','gu','pa')),
    ADD COLUMN tradition_preference TEXT NOT NULL DEFAULT 'vedic'
        CHECK (tradition_preference IN ('vedic', 'western', 'hybrid')),
    ADD COLUMN show_full_ui BOOLEAN NOT NULL DEFAULT false;

-- E13: daily/weekly insight cards
CREATE TABLE daily_insight (
    insight_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(organization_id),
    user_id        UUID NOT NULL REFERENCES "user"(user_id),
    chart_id       UUID NOT NULL REFERENCES astrology_chart(chart_id),
    insight_date   DATE NOT NULL,
    kind           TEXT NOT NULL CHECK (kind IN ('daily', 'weekly')),
    body_language  TEXT NOT NULL,
    body           JSONB NOT NULL,                  -- {cards: [{title, paragraph, cta}]}
    pushed_at      TIMESTAMPTZ,
    opened_at      TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, kind, insight_date)
);

CREATE INDEX idx_daily_insight_user_date
    ON daily_insight(user_id, insight_date DESC);

-- E13: progressive disclosure state
CREATE TABLE user_feature_reveal (
    organization_id UUID NOT NULL REFERENCES organization(organization_id),
    user_id        UUID NOT NULL REFERENCES "user"(user_id),
    feature_key    TEXT NOT NULL,
    revealed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, feature_key)
);

-- E13: notification opt-in and push tokens
CREATE TABLE notification_preference (
    user_id        UUID PRIMARY KEY REFERENCES "user"(user_id),
    daily_enabled  BOOLEAN NOT NULL DEFAULT false,
    weekly_enabled BOOLEAN NOT NULL DEFAULT false,
    push_tokens    JSONB NOT NULL DEFAULT '[]'::jsonb,
    quiet_hours    JSONB NOT NULL DEFAULT '{"start":"22:00","end":"07:00"}'::jsonb,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 5.5 API contract

```
GET  /api/v1/home                                   # returns greeting + daily insights + suggested question
GET  /api/v1/daily-insights?date=YYYY-MM-DD
GET  /api/v1/daily-insights/weekly?week_of=YYYY-MM-DD
POST /api/v1/daily-insights/{id}/opened             # track engagement

GET  /api/v1/my-chart                               # minimal chart view shape
GET  /api/v1/my-chart/layer/{layer}                 # houses | aspects | yogas (lazy)

GET  /api/v1/me/feature-reveal                      # returns revealed set
POST /api/v1/me/feature-reveal                      # marks a feature revealed

GET  /api/v1/me/settings                            # profile + tradition + language + notifications
PUT  /api/v1/me/settings                            # partial update

POST /api/v1/notifications/subscribe                # register push token
DELETE /api/v1/notifications/subscribe              # unregister

(chat endpoints: reuse E11a + E11b)
```

### 5.6 Backend delta

```
src/josi/api/v1/controllers/
├── home_controller.py
├── daily_insight_controller.py
├── my_chart_controller.py
├── feature_reveal_controller.py
└── settings_controller.py

src/josi/services/insights/
├── daily_insight_service.py
├── weekly_digest_service.py
└── insight_prompt_builder.py

src/josi/services/user/
├── feature_reveal_service.py
└── settings_service.py

src/josi/workers/
└── daily_insight_worker.py                 # scheduled per-user-TZ
```

### 5.7 Styling

All colors via CSS variables in `globals.css`. New variables for E13:

```css
:root {
  --confidence-high: var(--teal-400);
  --confidence-medium: var(--slate-400);
  --confidence-low: var(--amber-300);
  --confidence-contested: var(--amber-500);
  --claim-underline-thickness: 2px;
  --bottom-nav-height: 56px;
  --chat-composer-height: 64px;
  --message-user-bg: var(--surface-muted);
  --message-assistant-bg: var(--surface);
  --drill-down-bg: var(--surface-elevated);
}
```

Tailwind handles layout (flex, grid, padding, responsive breakpoints). No hardcoded hex.

### 5.8 Performance budgets

- Home JavaScript bundle ≤ 200 KB gzipped (critical path).
- Chat bundle ≤ 150 KB gzipped.
- My Chart bundle ≤ 100 KB gzipped.
- Total initial JS on Home ≤ 250 KB gzipped.
- SSR used for public pages only; all (dashboard) pages client-only per CLAUDE.md.
- Chat streaming first-byte ≤ 500 ms P95.
- Home first meaningful paint ≤ 1.5 s on throttled 3G.

## 6. User Stories

### US-E13.1: As a new user, after onboarding I land on Home and see a greeting + suggested first question
**Acceptance:** Home renders greeting, 3 insight placeholders (or first insights if worker completed), hero CTA. Tapping the suggestion sends the question and opens Chat.

### US-E13.2: As a user, I ask a question and get a 1-paragraph answer in ≤ 500 ms first byte
**Acceptance:** Question sent → stream begins within 500 ms P95 → single paragraph rendered; "Want more?" button visible.

### US-E13.3: As a user, I tap "Want more?" and see longer reasoning + citations
**Acceptance:** Tap reveals 2–3 paragraph expansion with citation chips and "Why?" affordances on each claim.

### US-E13.4: As a user, I tap a claim and see the classical citation inline
**Acceptance:** Claim expands inline on mobile (drawer on desktop) showing source display-name + verse reference + confidence bar.

### US-E13.5: As a user viewing a low-confidence claim, the AI is honest about it
**Acceptance:** Claim text shows muted-amber underline; AI prose uses phrase bank ("some traditions see…"); drill-down confirms numeric confidence < 0.6.

### US-E13.6: As a Tamil-speaking user, the entire UI is in Tamil
**Acceptance:** Language setting = ta → every label, button, placeholder is Tamil. AI responses are in Tamil. Sanskrit terms tooltip in Tamil.

### US-E13.7: As a mobile user, I can reach every destination with my thumb
**Acceptance:** Bottom nav Home / Chat / My Chart / Settings always visible; 44pt tap targets; composer anchored within reach.

### US-E13.8: As a new user, I only see Home + Chat at first; my chart gets prominent after 5 questions
**Acceptance:** First 4 sessions: nav shows Home + Chat + ellipsis. 5th session: My Chart becomes prominent with a single hint.

### US-E13.9: As a power user, I toggle "Show me everything" and all disclosures unlock
**Acceptance:** Settings toggle → all `user_feature_reveal` keys set. UI immediately shows full nav and all default expansions.

### US-E13.10: As a user opted into notifications, I receive a daily insight card at 6 am local time
**Acceptance:** Push at 6 am; card displays in home within tapping distance; tapping opens Chat pre-scoped to the insight topic.

### US-E13.11: As a user offline, I can read my last 50 messages and today's insights
**Acceptance:** Network disabled → cached content visible; composer shows "offline" banner.

### US-E13.12: As a screen-reader user, assistant messages are announced with confidence
**Acceptance:** VoiceOver announces "Strongly supports: [message]" or "Contested claim: [message]" per confidence bucket.

### US-E13.13: As a Mystic+ user, I tap the speaker on an assistant message and hear it read aloud
**Acceptance:** Play button visible; audio plays via mini-player; language matches message language.

### US-E13.14: As a Mystic+ user, I enable Debate mode from the chat header
**Acceptance:** Toggle reveals; next question uses debate mode; responses show "See where the strategies disagree" section.

### US-E13.15: As a user, my chart view is minimal by default
**Acceptance:** My Chart tab → planets + signs only; tapping "Show houses" reveals houses; then aspects; then yogas. State persists.

### US-E13.16: As a user, I don't see a single hex color or hardcoded `any` in the code
**Acceptance:** CI asserts zero hex colors in `(dashboard)` tree; zero `any` in chat-first code path; all colors via CSS vars.

### US-E13.17: As a user with reduced-motion preference, animations respect that
**Acceptance:** `prefers-reduced-motion: reduce` → no fade-ins on expansions; instant state changes.

### US-E13.18: As a user, my language + tradition preference persists across devices
**Acceptance:** Setting change on phone → web reloads with same language.

## 7. Tasks

### T-E13.1: Route restructuring — Home / Chat / My Chart / Settings
- **Definition:** Build new `(dashboard)/page.tsx` (Home), `/chat/*`, `/my-chart`, `/settings/*` tree. Redirect deprecated pages.
- **Acceptance:** All 4 destinations reachable; bottom nav + side nav functional.
- **Effort:** 3 days

### T-E13.2: Chat surface (simplified chrome)
- **Definition:** `chat-surface.tsx`, `message-list.tsx`, `composer.tsx`, `message-assistant.tsx`, `message-user.tsx`.
- **Acceptance:** Functional chat via existing E11a/E11b backend; one-paragraph-by-default rendering.
- **Effort:** 4 days

### T-E13.3: "Want more?" expansion
- **Definition:** `want-more-button.tsx` + `expanded-reasoning.tsx`; fetches extended view on tap (or streams additional from backend).
- **Acceptance:** Tap reveals citations + per-claim drill-downs.
- **Effort:** 2 days

### T-E13.4: Claim span + inline drill-down (mobile) + drawer (desktop)
- **Definition:** `claim-span.tsx`, `drill-down-inline.tsx`, `drill-down-drawer.tsx`.
- **Acceptance:** Tapping claim shows citation inline on mobile, drawer on desktop; consumes E11b endpoint.
- **Effort:** 3 days

### T-E13.5: Confidence-tuned styling
- **Definition:** `confidence-bar.tsx`, `confidence-label.tsx`, CSS variables, claim-underline color map.
- **Acceptance:** Four buckets visually distinct; color-blind safe.
- **Effort:** 1 day

### T-E13.6: Home page with greeting + insight cards + CTA
- **Definition:** `home-greeting.tsx`, `daily-insight-card.tsx`, `ask-anything-cta.tsx`, `weekly-digest-card.tsx`.
- **Acceptance:** Renders greeting keyed to time-of-day + language; 3 insight cards; hero CTA.
- **Effort:** 3 days

### T-E13.7: Daily insight worker + table
- **Definition:** `daily_insight_worker.py`, `daily_insight_service.py`, `insight_prompt_builder.py`. Schedule per-user TZ.
- **Acceptance:** 6 am local trigger produces 3 insights per active user with chart; costs bounded.
- **Effort:** 4 days

### T-E13.8: Weekly digest
- **Definition:** Weekly variant of above; Sunday 6 am local; longer-form prompt.
- **Acceptance:** Weekly card appears on Home once per week.
- **Effort:** 2 days

### T-E13.9: Push notifications + opt-in UI
- **Definition:** FCM integration; `POST /api/v1/notifications/subscribe`; opt-in settings page; quiet-hours respect.
- **Acceptance:** Push delivered; opt-out persists; no pushes during quiet hours.
- **Effort:** 3 days

### T-E13.10: My Chart minimal view
- **Definition:** `minimal-chart-view.tsx`, `chart-layer-toggle.tsx`, `chart-style-switch.tsx`.
- **Acceptance:** Planets + signs by default; progressive taps reveal houses → aspects → yogas.
- **Effort:** 3 days

### T-E13.11: Settings pages
- **Definition:** Profile, Tradition, Language, Notifications, Privacy, Advanced (show-full-ui toggle).
- **Acceptance:** All settings persist via `/api/v1/me/settings`; language switch reloads UI.
- **Effort:** 3 days

### T-E13.12: i18n — 10-language catalogs
- **Definition:** `next-intl` messages for en, hi, ta, te, bn, mr, kn, ml, gu, pa. `<SanskritTerm>` tooltips in user language.
- **Acceptance:** All strings translated; CI check for hardcoded English in (dashboard) tree.
- **Effort:** 4 days (translation work; setup is shared with E12)

### T-E13.13: Progressive disclosure engine
- **Definition:** `user_feature_reveal` table + endpoints + client hook. Reveal triggers on instrumented events.
- **Acceptance:** Nav changes as user hits triggers; "Show everything" overrides.
- **Effort:** 3 days

### T-E13.14: Bottom nav (mobile) + side nav (desktop)
- **Definition:** `bottom-nav.tsx` with 4 destinations + mystical pulse for active tab; `side-nav.tsx` desktop variant.
- **Acceptance:** Both navs work; switch at breakpoint; haptic on iOS.
- **Effort:** 2 days

### T-E13.15: Voice preview button integration (Mystic+)
- **Definition:** `voice-play-button.tsx` on assistant messages; reuses E11b mini-player.
- **Acceptance:** Plays audio; gated to Mystic+; language matches message.
- **Effort:** 1 day (heavy lifting in E11b)

### T-E13.16: Debate-mode toggle in chat header (Mystic+)
- **Definition:** `debate-toggle.tsx`; switches next question to debate mode.
- **Acceptance:** Debate-mode UI from E11b renders in this shell.
- **Effort:** 1 day

### T-E13.17: Offline support via service worker
- **Definition:** SW caches UI shell + last 50 messages + today's insights; `offline-banner.tsx`.
- **Acceptance:** Airplane mode → content visible; composer disables.
- **Effort:** 3 days

### T-E13.18: Accessibility pass
- **Definition:** ARIA labels, focus rings, reduced-motion, screen-reader announcements for confidence.
- **Acceptance:** axe-core in Playwright passes; manual screen-reader pass.
- **Effort:** 2 days

### T-E13.19: Performance budget + Lighthouse CI
- **Definition:** Budget file for bundle sizes; Lighthouse CI gates merges on Home perf ≥ 90.
- **Acceptance:** Regressions block merge.
- **Effort:** 1 day

### T-E13.20: Upgrade modals + tier-gate UX
- **Definition:** `upgrade-modal.tsx` with preview image per gated feature.
- **Acceptance:** Free user tapping Debate / Voice / Similarity sees upgrade modal.
- **Effort:** 2 days

### T-E13.21: Documentation + onboarding polish
- **Definition:** `docs/markdown/end-user-ui.md`; first-visit suggested-question card; help overlay.
- **Acceptance:** Docs merged; first-visit experience tested with 5 users.
- **Effort:** 2 days

### T-E13.22: Analytics instrumentation
- **Definition:** Event layer for feature reveal, chat volume, drill-down rate, conversion.
- **Acceptance:** Events fire; dashboard shows them; no PII.
- **Effort:** 2 days

## 8. Unit Tests

### 8.1 Chat surface (RTL)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_chat_surface_renders_messages` | 3 messages | 3 message bubbles | basic |
| `test_message_assistant_shows_want_more` | assistant message with `expandedAvailable=true` | "Want more?" button visible | affordance |
| `test_message_assistant_hides_want_more_when_unavailable` | flag false | button hidden | UX cleanliness |
| `test_composer_sends_on_enter` | type + Enter | onSend fires with text | keyboard |
| `test_composer_offline_disabled` | offline state | input disabled + banner shown | offline UX |
| `test_composer_max_length` | type > 4000 chars | truncated with counter | guardrail |

### 8.2 WantMoreButton + ExpandedReasoning

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_want_more_expands_on_tap` | tap button | ExpandedReasoning renders; fetch fires | behavior |
| `test_expanded_reasoning_shows_citations` | reasoning payload | citation chips visible | citations surface |
| `test_want_more_collapses_on_second_tap` | tap again | reasoning hidden | toggle |

### 8.3 ClaimSpan + DrillDown

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_claim_span_confidence_underline_color` | confidenceBucket='contested' | underline has `--confidence-contested` | styling |
| `test_claim_span_tap_opens_drilldown_inline_on_mobile` | viewport < 768px, tap | inline expansion | mobile |
| `test_claim_span_tap_opens_drawer_on_desktop` | viewport ≥ 768px, tap | side drawer opens | desktop |
| `test_drilldown_shows_citation_and_confidence_bar` | drilled-down payload | citation display-name + bar | info density |
| `test_drilldown_persists_state` | expand claim, reload | drill-down still expanded | localStorage |

### 8.4 Home

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_home_renders_greeting_by_time` | 9 am local | "Good morning, X" | personalization |
| `test_home_renders_insight_cards` | 3 insights | 3 cards | home structure |
| `test_home_empty_state_no_insights` | worker not yet run | 3 skeleton cards with gentle message | first-session UX |
| `test_home_cta_opens_chat_with_prefilled_question` | tap suggestion | chat opens, question prefilled | flow |

### 8.5 Daily insight backend

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_daily_insight_worker_generates_3_cards` | user with chart + dasa + transit | 3 cards in `daily_insight.body` | generation |
| `test_daily_insight_worker_skips_when_today_exists` | row for today exists | no-op | idempotency |
| `test_daily_insight_worker_fallback_on_no_change` | same dasa/transit as yesterday | reuses yesterday text | cost control |
| `test_daily_insight_language_matches_user` | user ui_language=ta | Claude called with Tamil prompt | localization |
| `test_weekly_digest_only_on_sunday` | Wednesday | no weekly digest generated | schedule |

### 8.6 MyChart

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_my_chart_renders_planets_and_signs_by_default` | chart data | planets + zodiac signs, no houses | minimal default |
| `test_my_chart_layer_toggle_reveals_houses` | tap "Show houses" | house lines render | progressive |
| `test_my_chart_further_tap_reveals_aspects` | tap again | aspect lines render | progressive |
| `test_my_chart_style_switch` | North → Western | chart re-renders in Western wheel | style switch |

### 8.7 Settings

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_language_picker_updates_user_settings` | select ta | PUT /me/settings called | persistence |
| `test_language_change_reloads_ui` | switch lang | full i18n reload | UX |
| `test_tradition_picker_persists` | select western | saved | persistence |
| `test_show_full_ui_toggle_unlocks_all` | toggle on | user_feature_reveal shows all keys | bypass |
| `test_notification_optin_respects_quiet_hours` | 23:00 | no push fires | respect |

### 8.8 Feature reveal engine

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_reveal_fires_after_5_questions` | 5 sessions sent | `my_chart_prominent` revealed | progression |
| `test_reveal_fires_after_3_whys` | 3 drill-down taps | `see_source_default` revealed | progression |
| `test_reveal_is_idempotent` | reveal same key twice | single row | correctness |
| `test_show_full_ui_overrides_all` | toggle on | all keys revealed | override |

### 8.9 i18n

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_all_10_languages_have_bottom_nav_labels` | each lang | 4 translated labels | coverage |
| `test_sanskrit_term_tooltip_follows_ui_language` | lang=te "raja-yoga" | tooltip in Telugu | fidelity |
| `test_ai_prompt_includes_user_language` | user lang=hi | Claude prompted in Hindi | AI i18n |
| `test_date_formatting_locale_aware` | lang=ta 2026-04-19 | Tamil date format | localization |

### 8.10 Accessibility

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_assistant_message_announced_with_confidence` | screen reader | aria-label includes "Strongly supports" | a11y |
| `test_focus_ring_visible_on_claim_span` | tab focus | visible ring | a11y |
| `test_reduced_motion_disables_transitions` | prefers-reduced-motion | no fade-in class applied | respect |
| `test_color_blind_palette_pass` | all buckets | passes deuteranopia simulator | inclusion |
| `test_axe_home_no_violations` | Home | 0 axe violations | baseline |
| `test_axe_chat_no_violations` | Chat | 0 axe violations | baseline |

### 8.11 Offline

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_service_worker_caches_last_50_messages` | fetch, go offline | messages readable | offline |
| `test_composer_disables_offline` | offline | disabled input + banner | UX |
| `test_daily_insight_cached` | today's insight fetched, go offline | still visible | offline |

### 8.12 Performance (Lighthouse CI + custom)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_home_lighthouse_perf_90` | Home page CI run | score ≥ 90 | budget |
| `test_chat_first_byte_under_500ms` | send message | first byte P95 < 500ms | streaming SLA |
| `test_home_bundle_size_under_budget` | build | gzipped ≤ 250 KB | budget |
| `test_my_chart_render_under_200ms` | mount | render < 200 ms | SLA |

### 8.13 Type discipline (TypeScript)

| Test name | Input | Expected | Rationale |
|---|---|---|---|
| `test_no_any_in_dashboard_path` | `tsc --noEmit` + lint | 0 `any` in (dashboard) code | CLAUDE.md |
| `test_no_hardcoded_hex_in_dashboard_path` | CI grep | 0 `#[0-9a-fA-F]{6}` | CLAUDE.md |
| `test_no_duplicate_type_definitions` | CI grep | types only in web/types | CLAUDE.md |
| `test_all_files_under_300_lines` | CI wc | all .tsx/.ts in (dashboard) ≤ 300 | CLAUDE.md |

### 8.14 Playwright end-to-end

| Test name | Flow | Assertion | Rationale |
|---|---|---|---|
| `e2e_first_time_user_onboarding_to_first_question` | sign up → wizard → Home → tap CTA → send question → get answer | 1-paragraph answer rendered within 2s | headline flow |
| `e2e_want_more_to_drill_down_to_citation` | ask question → Want more → tap claim → see citation | citation display-name visible | depth flow |
| `e2e_language_switch_reloads_ui` | Settings → language=ta → reload | all visible text Tamil | i18n |
| `e2e_progressive_disclosure_reveals_my_chart` | ask 5 questions → see hint → My Chart prominent | nav shows My Chart | progressive |
| `e2e_show_everything_toggle` | Settings → toggle on → Home | full UI unlocked | override |
| `e2e_daily_insight_push_to_chat` | receive push → tap → chat pre-scoped | chat opens on topic | notification flow |
| `e2e_offline_banner_and_cached_read` | airplane mode → Home | banner visible + insights readable | offline |
| `e2e_debate_mode_toggle_mystic_plus` | Mystic user → chat header toggle → ask | Debate view renders | E11b integration |
| `e2e_voice_preview_mystic_plus` | Mystic → tap speaker → audio plays | audio element active | E11b integration |
| `e2e_free_tier_upgrade_modal_on_debate` | Free user taps Debate | upgrade modal shown | conversion |
| `e2e_dont_show_me_this_again_persistence` | dismiss hint → reload | hint stays dismissed | state persistence |
| `e2e_screen_reader_confidence_announcement` | VoiceOver on low-confidence message | announcement includes "Contested" | a11y |

## 9. EPIC-Level Acceptance Criteria

- [ ] Four-destination architecture live: Home / Chat / My Chart / Settings
- [ ] Chat surface renders 1-paragraph answers by default with "Want more?" affordance
- [ ] Claim spans clickable → inline drill-down (mobile) + drawer (desktop)
- [ ] Confidence-tuned styling + prompt phrasing across 4 buckets
- [ ] Home page shows greeting + 3 daily insight cards + hero CTA
- [ ] Daily insight worker schedules per-user TZ; weekly digest on Sunday
- [ ] Push notifications opt-in + quiet-hours respected
- [ ] My Chart minimal view with progressive disclosure of layers
- [ ] Settings: profile, tradition, language (10 options), notifications, privacy, "show everything" toggle
- [ ] 10-language i18n complete; Sanskrit terms tooltipped in UI language
- [ ] Progressive disclosure engine: nav + affordances evolve with engagement
- [ ] Offline support: service worker + cached content + banner
- [ ] Mystic+ voice preview button + debate mode toggle integrated
- [ ] Accessibility: axe-core green; screen reader tested; color-blind safe; reduced-motion respected
- [ ] Performance: Home first byte on 3G < 1.5s; chat stream < 500ms P95; Lighthouse Home perf ≥ 90
- [ ] Type discipline: zero `any` in (dashboard) chat-first path; centralized types only; ≤ 300 lines/file; CSS vars for colors
- [ ] Playwright e2e green (12 flows)
- [ ] Unit test coverage ≥ 85% for E13 components and services
- [ ] Documentation: `docs/markdown/end-user-ui.md` + onboarding polish

## 10. Rollout Plan

- **Feature flag:** `END_USER_UI_V2_ENABLED` (default OFF; gradual roll).
- **Staged rollout:** 5% of new signups → 25% → 100% over 3 weeks. Existing users migrate on next session with a welcome modal.
- **Backfill:** None. Daily insight worker backfills one day of insights for existing users on their first post-launch visit.
- **Rollback plan:** Flip flag OFF → legacy widget dashboard returns. Data columns remain (additive).
- **Monitoring:**
  - Home first meaningful paint distribution.
  - Chat first-byte latency histogram.
  - Drill-down tap rate.
  - Feature-reveal progression histograms (how long from signup to each reveal).
  - Daily insight open rate.
  - Tier conversion rate after upgrade modal triggers.
  - Language distribution of active sessions.
- **A/B structure** (via E14a):
  - Arm A: chat-first (this PRD).
  - Arm B: legacy widget dashboard.
  - Primary metric: weekly active sessions per user; secondary: tier conversion.

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Existing users resent simplified UI loss of widgets | High | High | Welcome modal explains change; "Advanced" toggle preserves power-user flow; don't auto-migrate opted-out users |
| Chat-first confuses users who wanted dashboard | Medium | Medium | First-visit tour; "Ask anything" CTA is prominent; suggested-question card |
| Daily insight worker blows Anthropic budget | Medium | High | Per-user daily cap; reuse-yesterday fallback when state unchanged; alert on cost anomaly |
| Progressive disclosure feels infantilizing | Medium | Medium | "Show me everything" toggle is one click; default to minimal is a trade, not a limitation |
| 10-language translations inconsistent quality | High | Medium | Native reviewer per language; CI check for missing keys; launch minimum bar = English + Hindi + Tamil, others can ship progressively |
| Sanskrit term tooltips overwhelm in running prose | Medium | Low | Tooltip is hover/tap only; not inline annotation |
| Confidence-tuned prose confuses in translation | Medium | Medium | Phrase bank translated per language with native review; avoid literal translations |
| Push notifications get user frustration | Medium | High | Double-opt-in; quiet hours respected; one-tap unsubscribe in-app; frequency cap |
| Offline cache staleness | Medium | Low | Service worker TTL; "content may be outdated" banner when offline |
| Screen reader announcements annoying | Medium | Low | User can disable confidence announcements in settings |
| Bundle size creeps | High | Medium | Budget CI check; route-level code splitting; bundle-analyzer snapshots |
| Chart view on tiny screens (320px) clips | Medium | Low | Tested at 320px; zoom + pan affordance |
| Feature-reveal events fire incorrectly (reveal too early / never) | Medium | Low | Unit tests for each trigger; one-way state (no unreveal) |
| Voice preview fails in some languages | Medium | Medium | Graceful fallback: hide button if provider doesn't support language |
| Push payload leaks chart details | Low | High | Push body contains only generic "Your daily insight is ready"; content fetched on tap |
| Tier gating bypass via client-only checks | Low | High | Backend enforces; client is UX only |
| Hydration mismatches reappear | Low | Medium | Client-only (dashboard) mount pattern (per CLAUDE.md) unchanged |
| New nav conflicts with existing deep links | Medium | Low | Redirect map from legacy routes to new ones; 301s |

## 12. References

- Master spec: [`docs/superpowers/specs/2026-04-19-classical-techniques-expansion-design.md`](../../../superpowers/specs/2026-04-19-classical-techniques-expansion-design.md) §1.2, §3.2
- Chat engine: [`P1/E11a-ai-chat-orchestration-v1.md`](../P1/E11a-ai-chat-orchestration-v1.md)
- Chat v2 (debate, ultra, voice, similarity): [`P2/E11b-ai-chat-debate-mode.md`](./E11b-ai-chat-debate-mode.md)
- Citation envelope (drives confidence tuning): [`P0/F11-citation-embedded-responses.md`](../P0/F11-citation-embedded-responses.md)
- Reading view: [`P0/F9-chart-reading-view-table.md`](../P0/F9-chart-reading-view-table.md)
- Prompt caching: [`P0/F12-prompt-caching-claude.md`](../P0/F12-prompt-caching-claude.md)
- Professional counterpart: [`P2/E12-astrologer-workbench-ui.md`](./E12-astrologer-workbench-ui.md)
- Future voice-native: `P5/D1-voice-native-ai-astrologer.md`
- Future localization breadth: `P5/D3-localization-20-plus-traditions.md`
- Future longitudinal dashboard: `P5/D6-longitudinal-dashboard.md`
- Frontend conventions: [`CLAUDE.md`](../../../../CLAUDE.md) → "Frontend Conventions (MUST FOLLOW)"
- next-intl: https://next-intl-docs.vercel.app
- Service worker recipes: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- Co-Star product study (reference): https://www.costarastrology.com (chat-free model; counterexample)
- The Pattern product study: https://thepattern.com (event-card model)
