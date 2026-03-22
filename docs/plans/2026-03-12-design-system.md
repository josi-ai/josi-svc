# Josi Design System

> **Brand Archetype**: The Alchemist
> **Tagline**: "Ancient eyes on an infinite sky"
> **Preview**: `docs/plans/brand-preview-v7.html`

---

## 1. Color Tokens

All colors are defined as CSS custom properties on `:root` (dark) and `body.light` (light). In Tailwind/shadcn, these map to HSL variables.

### Backgrounds

| Token | Dark | Light | Usage |
|-------|------|-------|-------|
| `--bg-page` | `#060A14` | `#F0F2F7` | Page/body background |
| `--bg-frame` | `#0A0F1E` | `#FFFFFF` | App frame, mobile frame, content area |
| `--bg-surface` | `#080E1C` | `#F6F7FB` | Sidebar, top nav, elevated surfaces |
| `--bg-card` | `#111828` | `#FFFFFF` | Cards, panels, modals |
| `--bg-card-hover` | `#151E30` | `#F8F9FC` | Card hover state |
| `--bg-hero` | `linear-gradient(135deg, #111828 0%, #0F1A2E 50%, #131425 100%)` | `linear-gradient(135deg, #FFFFFF 0%, #F4F6FB 50%, #F0F3F9 100%)` | Hero sections |

### Borders

| Token | Dark | Light | Usage |
|-------|------|-------|-------|
| `--border-subtle` | `#151C30` | `#E8ECF2` | Dividers between major sections |
| `--border-default` | `#1A2340` | `#DDE1EB` | Card borders, input borders |
| `--border-strong` | `#253050` | `#CED4E0` | Hover state borders, emphasis |
| `--border-divider` | `#14203A` | `#E8ECF2` | List item separators |

### Text

| Token | Dark | Light | Usage |
|-------|------|-------|-------|
| `--text-primary` | `#D4DAE6` | `#1A1F2E` | Headings, names, primary content |
| `--text-secondary` | `#8B99B5` | `#4A5268` | Subheadings, secondary info |
| `--text-body` | `#7B8CA8` | `#5A6478` | Body text, descriptions |
| `--text-body-reading` | `#7080A0` | `#4E5A70` | Long-form reading content |
| `--text-muted` | `#5B6A8A` | `#7E8DA5` | Labels, timestamps, placeholders |
| `--text-faint` | `#3A4A6A` | `#A0AABB` | Disabled, decorative, tertiary |

### Accents

| Token | Dark | Light | Usage |
|-------|------|-------|-------|
| `--accent-gold` | `#C8913A` | `#B8832E` | Primary accent, CTAs, links |
| `--accent-gold-bright` | `#D4A04A` | `#C8913A` | Highlight values, active states |
| `--accent-gold-bg` | `rgba(200,145,58,0.12)` | `rgba(184,131,46,0.08)` | Badge backgrounds, pill fills |
| `--accent-gold-bg-subtle` | `rgba(200,145,58,0.06)` | `rgba(184,131,46,0.04)` | Muhurta "now" highlight |
| `--accent-blue` | `#6A9FD8` | `#4A7FB5` | Informational, transit data |
| `--accent-blue-bg` | `rgba(106,159,216,0.1)` | `rgba(74,127,181,0.08)` | Blue pill backgrounds |
| `--accent-green` | `#6AAF7A` | `#5A8F6A` | Positive status, "available" |
| `--accent-green-bg` | `rgba(106,175,122,0.1)` | `rgba(90,143,106,0.07)` | Green pill backgrounds |
| `--accent-red` | `#C45D4A` | `#C45D4A` | Warnings, "avoid" muhurta |

### Semantic Colors

| Token | Dark | Light | Usage |
|-------|------|-------|-------|
| `--bar-good` | `#6AAF7A` | `#5A8F6A` | Muhurta: favorable |
| `--bar-neutral` | `#3A4A6A` | `#CED4E0` | Muhurta: neutral |
| `--bar-avoid` | `#C45D4A` | `#C45D4A` | Muhurta: Rahu kala, avoid |
| `--bar-special` | `#D4A04A` | `#C8913A` | Muhurta: shubh, current |

---

## 2. Typography

Three typefaces, each with a specific role:

| Typeface | Role | Weights | Loading |
|----------|------|---------|---------|
| **DM Serif Display** | Display headings (h1, h2), large numbers, pull quotes | Regular, Italic | Google Fonts |
| **Inter** | UI text, labels, buttons, navigation, body copy | 300–700 | Google Fonts (variable) |
| **DM Serif Text** | Reading content, interpretations, AI-generated text | Regular, Italic | Google Fonts |

### Type Scale

| Name | Font | Size | Weight | Line Height | Usage |
|------|------|------|--------|-------------|-------|
| `display-xl` | DM Serif Display | 48px | 400 | 1.15 | Reading page h1 |
| `display-lg` | DM Serif Display | 34px | 400 | 1.25 | Hero titles (web) |
| `display-md` | DM Serif Display | 28px | 400 | 1.25 | Card titles, hero (mobile) |
| `display-sm` | DM Serif Display | 22px | 400 | 1.3 | Section titles |
| `display-xs` | DM Serif Display | 16px | 400 | 1.3 | Inline headings |
| `heading-lg` | Inter | 14px | 600 | 1.4 | Page subtitles |
| `heading-sm` | Inter | 13px | 600 | 1.4 | Card headings, nav items |
| `body-lg` | DM Serif Text | 20px | 400 | 1.85 | Lead paragraphs |
| `body-md` | DM Serif Text | 17px | 400 | 1.9 | Reading body text |
| `body-sm` | DM Serif Text | 15px | 400 | 1.75 | Card descriptions |
| `body-xs` | DM Serif Text | 13px | 400 | 1.7 | Mobile body text |
| `ui-lg` | Inter | 14px | 500 | 1.5 | Buttons (large) |
| `ui-md` | Inter | 13px | 500 | 1.4 | Navigation links |
| `ui-sm` | Inter | 12px | 500 | 1.4 | Buttons (small), tags |
| `ui-xs` | Inter | 11px | 500 | 1.3 | Badges, tooltips |
| `label` | Inter | 10px | 600 | 1.2 | Section labels, overlines |
| `caption` | Inter | 9px | 500 | 1.2 | Tab labels, muhurta times |
| `stat-lg` | DM Serif Display | 40px | 400 | 1.0 | Large stat numbers (web) |
| `stat-md` | DM Serif Display | 36px | 400 | 1.0 | Stat numbers (sidebar) |

### Label Convention

All section labels and overlines use:
- Font: Inter
- Size: 10px
- Weight: 600
- Transform: uppercase
- Letter-spacing: 1.5–2.5px
- Color: `--text-muted` (section) or `--accent-gold` (feature)

---

## 3. Spacing

Base unit: **4px**. All spacing is a multiple of 4.

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight gaps (icon-to-text) |
| `space-2` | 6px | Button group gaps |
| `space-3` | 8px | Pill gaps, small card padding |
| `space-4` | 10px | Grid gaps (mobile), list padding |
| `space-5` | 12px | Standard inner padding, section labels margin |
| `space-6` | 14px | Nav item padding, card inner spacing |
| `space-7` | 16px | Mobile card padding, reading lead padding |
| `space-8` | 20px | Card padding (standard), content margins |
| `space-9` | 24px | Section spacing, web card padding |
| `space-10` | 28px | Web card padding (large), content area padding |
| `space-11` | 32px | Reading page section spacing |
| `space-12` | 40px | Web content area horizontal padding |
| `space-13` | 44px | Hero padding (web) |
| `space-14` | 48px | Pull quote padding |
| `space-15` | 56px | Reading hero top padding |

### Grid Gaps

| Context | Gap |
|---------|-----|
| Mobile daily cards | 10px |
| Mobile muhurta slots | 0 (border-separated) |
| Web card rows | 20px |
| Web hero inner | 48px |
| Web bottom row | 20px |

---

## 4. Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-xs` | 6px | Browser URL bar, small badges, muhurta slots |
| `radius-sm` | 7px | Toggle buttons, sidebar nav items |
| `radius-md` | 8px | Muhurta slot (first/last), input fields |
| `radius-lg` | 10px | Buttons (standard) |
| `radius-xl` | 12px | Time badge, mobile cards, web frame |
| `radius-2xl` | 14px | Standard cards (mobile + web), insight cards |
| `radius-3xl` | 16px | Web cards (option 2), pills |
| `radius-hero` | 18px | Mobile hero card |
| `radius-hero-lg` | 20px | Web hero card |
| `radius-pill` | 9999px | Avatar circles, plan badges |
| `radius-mobile` | 40px | Mobile phone frame |

---

## 5. Shadows

| Token | Dark | Light | Usage |
|-------|------|-------|-------|
| `shadow-frame` | `0 20px 80px rgba(0,0,0,0.4)` | `0 8px 40px rgba(26,31,46,0.08)` | Web browser frame |
| `shadow-mobile` | `0 20px 80px rgba(0,0,0,0.5)` | `0 12px 48px rgba(26,31,46,0.1)` | Mobile phone frame |
| `shadow-gold-btn` | — | `0 2px 8px rgba(200,145,58,0.3)` | Active theme toggle |

> Cards do **not** have box-shadows. Elevation is communicated via background color difference and borders.

---

## 6. Layout System

### User Preference: Navigation Style

Users choose between two navigation layouts in Settings. Stored as a user preference.

| Option | Name | Description |
|--------|------|-------------|
| **Side Nav** | Sidebar Dashboard | 240px persistent sidebar, denser layout |
| **Top Nav** | Top Navigation | Full-width, no sidebar, more breathing room |

### Page-Specific Overrides

Regardless of preference, certain page types force a specific layout:

| Page Type | Layout | Reason |
|-----------|--------|--------|
| Home / Dashboard | User preference | Browsing mode |
| Booking / Astrologers | User preference | Browsing mode |
| Chart exploration | Sidebar + Canvas + Panel | Tool mode requires panels |
| AI Reading | Centered single-column (680px) | Focus/reading mode |

### Breakpoints

| Name | Width | Layout |
|------|-------|--------|
| Mobile | < 768px | Single column, bottom tab bar |
| Tablet | 768–1024px | Collapsible sidebar or top nav |
| Desktop | 1024–1280px | Full layout |
| Wide | > 1280px | Centered with max-width: 1280px |

### Content Widths

| Context | Max Width |
|---------|-----------|
| Web frame | 1280px |
| Top nav content area | 1120px |
| Reading hero | 800px |
| Reading body text | 680px |
| Mobile frame | 390px |

### Sidebar Dimensions

| Element | Value |
|---------|-------|
| Sidebar width | 240px |
| Sidebar header padding | 20px |
| Sidebar nav item height | ~34px |
| Sidebar footer height | ~58px |
| Sidebar group label size | 9px uppercase |

### Grid Layouts

**Home (Sidebar):**
```
[Hero card (1fr)] [Muhurta (340px)]
[Chart] [Charts count] [AI readings]
[Latest reading (1fr)] [Astrologers (1fr)]
```

**Home (Top Nav):**
```
[Greeting row — full width]
[Hero card with muhurta embedded — full width]
[Chart (1fr)] [Charts (1fr)] [Readings (1fr)]
[Latest reading (1fr)] [Astrologers (1fr)]
```

---

## 7. Component Specifications

### Pills / Badges

- Font: Inter 11px / 500
- Padding: 5px 12px
- Border radius: 16px
- Variants: gold, blue, green (each with bg + text color from accent tokens)

### Plan Badge

- Font: Inter 9–10px / 700
- Padding: 3–4px 8–10px
- Border radius: 10–12px
- Background: `--accent-gold-bg`
- Color: `--accent-gold-bright`

### Buttons

| Variant | Background | Text | Border | Radius |
|---------|-----------|------|--------|--------|
| Primary (gold) | `--accent-gold` | `#fff` | none | 6–10px |
| Ghost | transparent | `--text-secondary` | `--border-default` | 6px |
| Secondary | `--bg-card` | `--text-primary` | `--border-default` | 10px |

### Cards

- Background: `--bg-card`
- Border: 1px solid `--border-default`
- Border radius: 14–16px
- Padding: 20–28px
- Hover: border shifts to `--border-strong`
- No box-shadow

### Avatar

| Size | Diameter | Font Size | Usage |
|------|----------|-----------|-------|
| sm | 30px | 11px | Sidebar footer, mobile topbar |
| md | 32px | 11px | Top nav |
| lg | 42px | 16px | Astrologer list |
| xl | 48px | 18px | Astrologer card (mobile) |

- User avatar: `--avatar-gradient` background, `--avatar-text` color, bold weight
- Placeholder avatar: `--avatar-placeholder` gradient, DM Serif Display, `--text-primary`

### Mini Chart Wheel

- Diameter: 64px (web), 80px (mobile)
- Outer border: 1.5px solid `--border-strong`
- Inner ring: 65% diameter, 1px solid `--border-default`
- Planet dots: 5px circles in accent colors
- Center label: 7–8px uppercase, `--text-faint`

### Muhurta Slots

- Slot width: 56px (mobile scroll), flex-1 (web strip), 1fr (web grid)
- Time: 9–10px Inter, `--text-muted`
- Bar: 24–28px wide, 5px tall, rounded 3px
- Label: 8–9px Inter, `--text-faint`
- "Now" state: background + border from `--muhurta-now-*` tokens

### Tab Bar (Mobile)

- Background: `--tab-bar-bg` with backdrop-filter: blur(16px)
- 5 tabs, equal width
- Icon: 17px, inactive: `--text-faint`, active: `--accent-gold-bright`
- Label: 9px Inter 500, same color scheme
- Bottom padding: 28px (safe area)

---

## 8. Reading Mode

Reading pages follow a distinct typographic layout:

### Structure
```
[Top Nav]
[Hero: centered, 800px max]
  - Category label (overline)
  - Title (display-xl, centered)
  - Byline + time badge
[Divider: 1px, 800px max]
[Lead paragraph: 680px, border-left gold, DM Serif Text 20px]
[Body: 680px, DM Serif Text 17px, line-height 1.9]
[Pull quote: 800px, DM Serif Display 32px, centered, bordered top+bottom]
[Insight card: 680px, bg-card, label + DM Serif Text 16px]
[More body...]
[Neural Pathway card: same as insight]
[Action buttons: 680px, flex row]
```

### Key Reading Metrics
- Line length: ~65–75 characters (680px at 17px)
- Line height: 1.85–1.9 for body, 1.75 for insight cards
- Paragraph spacing: 24px
- Section spacing: 32–40px

---

## 9. Mobile Patterns

### Scrollytelling (Chart Page)
- Chart wheel is sticky at top
- Planet sections scroll beneath
- Each section: planet label (overline with color dot) + detail card
- Detail card: planet row (dot, name, sign, degree) + interpretation text

### Content Hierarchy (Home)
1. Greeting + date
2. Hero card (today's sky)
3. Muhurta horizontal scroll
4. Chart glance card
5. Daily 2-col grid (moon phase, transit, charts, readings)
6. Latest reading preview
7. Astrologer spotlight
8. Tab bar (persistent)

### Navigation
- Bottom tab bar: Today, Charts, Insights, Consult, Profile
- Back button: top-left, text-based ("← Back")
- Share button: top-right on reading pages

---

## 10. Iconography

Currently using Unicode symbols. For production, replace with a consistent icon set:

| Current | Meaning | Recommended |
|---------|---------|-------------|
| ☾ (&#9790;) | Moon / dark mode | Lucide: `moon` |
| ☼ (&#9788;) | Sun / light mode | Lucide: `sun` |
| ★ (&#9733;) | Astrologers / favorite | Lucide: `star` |
| ☆ (&#9734;) | Charts | Lucide: `circle-dot` |
| ✨ (&#10024;) | AI / Insights | Lucide: `sparkles` |
| ⚙ (&#9881;) | Settings / Profile | Lucide: `settings` |
| ↺ (&#8634;) | Transits | Lucide: `refresh-cw` |
| ☽ (&#9789;) | Panchang | Lucide: `moon-star` |
| ◑ (&#9681;) | Dasha | Lucide: `clock` |
| ☻ (&#9883;) | Muhurta | Lucide: `timer` |
| ✉ (&#9993;) | Consultations | Lucide: `message-square` |
| ✧ (&#10023;) | Compatibility | Lucide: `heart` |

> **Icon set**: [Lucide](https://lucide.dev/) — already bundled with shadcn/ui.

---

## 11. Implementation Notes

### shadcn/ui Mapping

| Design System Component | shadcn/ui Component |
|------------------------|---------------------|
| Cards | `Card`, `CardHeader`, `CardContent` |
| Buttons (gold, ghost, secondary) | `Button` with custom variants |
| Pills / Badges | `Badge` with custom variants |
| Tab bar | Custom (not standard tabs) |
| Navigation sidebar | `Sidebar` from shadcn/ui |
| Top navigation | Custom `Navbar` component |
| Avatar | `Avatar`, `AvatarFallback` |
| Plan badge | `Badge` variant |
| Muhurta strip | Custom component |
| Chart wheel | Custom SVG component |
| Toggle (theme) | `Toggle` or custom |
| Reading layout | Prose/typography plugin |

### CSS Variable Setup (globals.css)

```css
@layer base {
  :root {
    /* Map design tokens to shadcn HSL format */
    --background: 222 45% 4%;      /* #060A14 */
    --foreground: 222 20% 88%;     /* #D4DAE6 */
    --card: 222 33% 10%;           /* #111828 */
    --card-foreground: 222 20% 88%;
    --primary: 35 55% 50%;         /* #C8913A */
    --primary-foreground: 0 0% 100%;
    --secondary: 222 33% 10%;
    --secondary-foreground: 222 20% 88%;
    --muted: 222 25% 15%;
    --muted-foreground: 222 20% 45%;
    --accent: 35 55% 50%;
    --accent-foreground: 0 0% 100%;
    --border: 222 33% 17%;         /* #1A2340 */
    --ring: 35 55% 50%;
    --radius: 0.875rem;
  }

  .light {
    --background: 225 16% 95%;     /* #F0F2F7 */
    --foreground: 225 25% 14%;     /* #1A1F2E */
    --card: 0 0% 100%;
    --card-foreground: 225 25% 14%;
    --primary: 35 60% 45%;         /* #B8832E */
    --primary-foreground: 0 0% 100%;
    --border: 225 16% 88%;         /* #DDE1EB */
    /* ... etc */
  }
}
```

### Tailwind Config Extensions

```js
extend: {
  fontFamily: {
    display: ['"DM Serif Display"', 'serif'],
    reading: ['"DM Serif Text"', 'serif'],
    sans: ['Inter', 'system-ui', 'sans-serif'],
  },
  fontSize: {
    'display-xl': ['48px', { lineHeight: '1.15' }],
    'display-lg': ['34px', { lineHeight: '1.25' }],
    'display-md': ['28px', { lineHeight: '1.25' }],
    'stat-lg': ['40px', { lineHeight: '1' }],
  },
  maxWidth: {
    'reading': '680px',
    'reading-hero': '800px',
    'content': '1120px',
  },
}
```
