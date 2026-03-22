# Phase 1: Dashboard, Sidebar & Theme System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Josi frontend with a dual-theme system (dark Observatory + light Stripe+Gold), a sidebar with colored icons and badges, and a customizable widget-based dashboard.

**Architecture:** Theme-first approach. We update CSS variables and build a ThemeProvider first, then rebuild the sidebar with colored icons/badges that respond to themes, then build the widget dashboard on top. All state is client-side for now (localStorage for theme + widget preferences). The sidebar layout is the only layout for Phase 1 (top nav deferred).

**Tech Stack:** Next.js 16 (App Router), React 19, Tailwind CSS v4 (CSS-first config via `@import "tailwindcss"` — the `tailwind.config.ts` file is NOT loaded in v4 without an explicit `@config` directive; all theme tokens live in CSS variables in `globals.css`), next-themes (to install), CSS custom properties, localStorage, lucide-react icons, existing Clerk auth + React Query setup.

**Reference mockups:**
- Sidebar variants: `docs/mockups/decisions/00-sidebar-final-variants.html` (Observatory dark + Stripe+Gold light)
- Widget dashboard: `docs/mockups/decisions/01-tradition-selector/final-v2-widget-dashboard.html`

**Important notes:**
- The existing CSS uses `:root` for dark and `.light` for light. We're flipping to `:root` = light (default), `.dark` = dark override. ALL existing CSS variables must be migrated to both blocks.
- `tailwind.config.ts` is effectively dead in Tailwind v4 — do NOT modify it. All tokens are in `globals.css`.
- Use `next-themes` instead of a custom ThemeProvider — it handles SSR, FOUC prevention, and system preference detection out of the box.
- Sidebar background uses CSS `background` property (not `background-color`) because the dark theme uses a gradient value.

---

## File Structure

### Files to modify:
| File | Responsibility |
|------|---------------|
| `web/app/globals.css` | CSS variables for both themes (dark + light), icon colors, counter colors, card shadows |
| `web/app/layout.tsx` | Remove hardcoded `dark` class, integrate ThemeProvider |
| `web/app/(dashboard)/layout.tsx` | Simplify to sidebar-only layout, integrate new sidebar |
| `web/app/(dashboard)/dashboard/page.tsx` | Complete rewrite — widget grid dashboard |
| `web/components/layout/app-sidebar.tsx` | Complete rewrite — colored icons, colored badges, dual-theme |
| `web/components/layout/user-dropdown.tsx` | Update theme toggle to use ThemeProvider |
| `web/config/sidebar-config.ts` | Add icon colors, counter badge colors, icon components |
| `web/components/providers.tsx` | Add ThemeProvider to provider stack, make ClerkProvider theme-aware |

### Files to create:
| File | Responsibility |
|------|---------------|
| ~~`web/contexts/ThemeContext.tsx`~~ | ~~Custom ThemeProvider~~ — **USE `next-themes` INSTEAD** (install via `npm install next-themes`) |
| `web/config/widget-config.ts` | Widget type definitions, default widget layout, widget catalog |
| `web/components/dashboard/widget-grid.tsx` | Widget grid layout component with add/remove |
| `web/components/dashboard/add-widget-modal.tsx` | Modal for browsing/adding widgets |
| `web/components/dashboard/widgets/todays-sky.tsx` | Today's Sky hero widget |
| `web/components/dashboard/widgets/chart-quick-view.tsx` | Mini chart preview widget |
| `web/components/dashboard/widgets/current-dasha.tsx` | Current dasha period widget |
| `web/components/dashboard/widgets/ai-chat-access.tsx` | AI chat quick access widget |
| `web/components/dashboard/widgets/muhurta-timeline.tsx` | Muhurta time bar widget |
| `web/components/dashboard/widgets/western-transit.tsx` | Western transit alert widget |
| `web/components/dashboard/widgets/latest-reading.tsx` | Latest AI reading widget |
| `web/components/dashboard/widgets/available-astrologers.tsx` | Astrologer availability widget |
| `web/components/dashboard/widgets/bazi-summary.tsx` | Chinese BaZi summary widget |
| `web/components/dashboard/widgets/widget-card.tsx` | Shared widget card wrapper (drag handle, remove, tradition badge) |

---

## Task 1: Theme System — CSS Variables & next-themes

**Files:**
- Modify: `web/app/globals.css`
- Modify: `web/app/layout.tsx`
- Modify: `web/components/providers.tsx`
- Install: `next-themes`

### Step-by-step:

- [ ] **Step 1: Update `globals.css` — dark theme variables (Observatory)**

Replace the existing `:root` variables with the Observatory dark theme as the base. The dark theme is applied via `.dark` class on `<html>`.

Key dark theme values:
```css
.dark {
  --background: #060A14;
  --surface: #080E1C;
  --frame: #0A0F1E;
  --card: #111828;
  --card-hover: #151E30;
  --border: #1A2340;
  --border-subtle: #151C30;
  --border-strong: #253050;
  --border-divider: #14203A;
  --text-primary: #D4DAE6;
  --text-secondary: #8B99B5;
  --text-body: #7B8CA8;
  --text-muted: #5B6A8A;
  --text-faint: #3A4A6A;
  --gold: #C8913A;
  --gold-bright: #D4A04A;
  --gold-bg: rgba(200,145,58,0.12);
  --gold-bg-subtle: rgba(200,145,58,0.06);
  --shadow-card: 0 1px 3px rgba(0,0,0,0.2);
  /* Sidebar-specific (Observatory) */
  --sb-bg: linear-gradient(180deg, #141C30 0%, #0F1724 100%);
  --sb-border: #1E2A42;
  --sb-text: #8B99B5;
  --sb-text-active: #FFFFFF;
  --sb-active-bg: rgba(200,145,58,0.10);
  --sb-hover-bg: rgba(255,255,255,0.04);
  --sb-top-line: linear-gradient(90deg, transparent, #D4A04A, transparent);
  --sb-divider: linear-gradient(90deg, transparent 10%, rgba(200,145,58,0.15) 50%, transparent 90%);
  --btn-add-text: #FFFFFF;
}
```

- [ ] **Step 2: Add light theme variables (Stripe + Gold) to `globals.css`**

The light theme is applied when `.dark` is NOT present (or `.light` class is added):
```css
:root {
  --background: #FFFFFF;
  --surface: #F4F6FA;
  --frame: #FFFFFF;
  --card: #FFFFFF;
  --card-hover: #F8F9FC;
  --border: #DDE2EB;
  --border-subtle: #E4E8EE;
  --border-strong: #CDD4E0;
  --border-divider: #E8ECF2;
  --text-primary: #111828;
  --text-secondary: #4A5268;
  --text-body: #5A6478;
  --text-muted: #6A7488;
  --text-faint: #94A0B8;
  --gold: #A87E30;
  --gold-bright: #BA8E3A;
  --gold-bg: rgba(168,126,48,0.09);
  --gold-bg-subtle: rgba(168,126,48,0.04);
  --shadow-card: 0 1px 3px rgba(26,31,46,0.06), 0 1px 2px rgba(26,31,46,0.04);
  /* Sidebar-specific (Stripe + Gold) */
  --sb-bg: #F8F9FB;
  --sb-border: #E4E6EA;
  --sb-text: #0F1520;
  --sb-text-active: #000000;
  --sb-active-bg: rgba(200,145,58,0.12);
  --sb-hover-bg: rgba(200,145,58,0.04);
  --sb-top-line: linear-gradient(90deg, transparent 10%, #C8913A 50%, transparent 90%);
  --sb-divider: #E4E6EA;
  --btn-add-text: #000000;
}
```

- [ ] **Step 3: Add icon color variables to `globals.css`**

These are constant across themes (brighter versions used in dark mode via component logic):
```css
:root {
  /* Nav icon colors (light mode) */
  --ic-dashboard: #C8913A;
  --ic-charts: #4A7FB5;
  --ic-ai: #7B5AAF;
  --ic-compatibility: #C4627A;
  --ic-transits: #3A9DB5;
  --ic-panchang: #D48A30;
  --ic-dasha: #3A8F7A;
  --ic-muhurta: #BA8040;
  --ic-astrologers: #528E62;
  --ic-consultations: #C46A50;
  /* Counter badge colors */
  --ct-charts-bg: rgba(74,127,181,0.12);
  --ct-charts-text: #4A7FB5;
  --ct-ai-bg: rgba(123,90,175,0.12);
  --ct-ai-text: #7B5AAF;
  --ct-consultations-bg: rgba(196,106,80,0.12);
  --ct-consultations-text: #C46A50;
}
.dark {
  /* Brighter icon colors for dark bg */
  --ic-dashboard: #E0A848;
  --ic-charts: #5E9AD0;
  --ic-ai: #9678C8;
  --ic-compatibility: #DA7A94;
  --ic-transits: #50B8D0;
  --ic-panchang: #F0A040;
  --ic-dasha: #50B098;
  --ic-muhurta: #D49850;
  --ic-astrologers: #6AB07A;
  --ic-consultations: #E08060;
  /* Brighter counter colors for dark bg */
  --ct-charts-bg: rgba(94,154,208,0.18);
  --ct-charts-text: #5E9AD0;
  --ct-ai-bg: rgba(150,120,200,0.18);
  --ct-ai-text: #9678C8;
  --ct-consultations-bg: rgba(224,128,96,0.18);
  --ct-consultations-text: #E08060;
}
```

- [ ] **Step 4: Install `next-themes`**

Run: `cd web && npm install next-themes`

- [ ] **Step 5: Update `web/app/layout.tsx`**

Change `<html lang="en" className="dark">` to `<html lang="en" suppressHydrationWarning>`. The `next-themes` ThemeProvider will manage the class dynamically.

- [ ] **Step 6: Add ThemeProvider to `web/components/providers.tsx`**

Import `ThemeProvider` from `next-themes` and wrap it around all existing providers:
```typescript
import { ThemeProvider } from 'next-themes'

// In the Providers component, wrap outermost:
<ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
  <ClerkProvider ...>
    ...
  </ClerkProvider>
</ThemeProvider>
```

Also make ClerkProvider theme-aware by using `useTheme()` from `next-themes` to switch between dark/light Clerk appearance. This requires splitting into an inner component that can access the theme context:
```typescript
import { useTheme } from 'next-themes'
import { dark } from '@clerk/themes'

function ClerkThemeWrapper({ children }) {
  const { resolvedTheme } = useTheme()
  return (
    <ClerkProvider appearance={{
      baseTheme: resolvedTheme === 'dark' ? dark : undefined,
      variables: { colorPrimary: '#C8913A' }
    }}>
      {children}
    </ClerkProvider>
  )
}
```

- [ ] **Step 7: Verify theme toggle works**

Run: `cd web && npm run dev`
Open `http://localhost:4000/dashboard`. Open browser console, run:
```js
document.documentElement.classList.toggle('dark')
```
Verify colors switch between dark and light. Toggle back.

- [ ] **Step 8: Commit**
```bash
git add web/app/globals.css web/contexts/ThemeContext.tsx web/app/layout.tsx web/components/providers.tsx
git commit -m "feat(web): add dual-theme system with Observatory dark and Stripe+Gold light"
```

---

## Task 2: Sidebar Config — Add Icon Colors & Components

**Files:**
- Modify: `web/config/sidebar-config.ts`

- [ ] **Step 1: Update sidebar config with icon colors and LucideIcon references**

```typescript
import {
  LayoutDashboard, CircleDot, Users, Heart, RefreshCw,
  Clock, MoonStar, Lightbulb, Pill, Star, Sparkles,
  Settings, MessageSquare
} from 'lucide-react'
import { LucideIcon } from 'lucide-react'

export interface SidebarMenuItem {
  key: string
  label: string
  path: string
  icon: LucideIcon
  iconColorVar: string       // CSS variable name for icon color
  counterColorBgVar?: string // CSS variable for counter badge bg
  counterColorTextVar?: string // CSS variable for counter badge text
}

export interface SidebarGroup {
  label: string
  items: SidebarMenuItem[]
}

export const sidebarMenuItems: Record<string, SidebarMenuItem> = {
  dashboard: { key: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, iconColorVar: '--ic-dashboard' },
  charts: { key: 'charts', label: 'Charts', path: '/charts', icon: CircleDot, iconColorVar: '--ic-charts', counterColorBgVar: '--ct-charts-bg', counterColorTextVar: '--ct-charts-text' },
  persons: { key: 'persons', label: 'Profiles', path: '/persons', icon: Users, iconColorVar: '--ic-charts' },
  ai: { key: 'ai', label: 'AI Readings', path: '/ai', icon: Sparkles, iconColorVar: '--ic-ai', counterColorBgVar: '--ct-ai-bg', counterColorTextVar: '--ct-ai-text' },
  compatibility: { key: 'compatibility', label: 'Compatibility', path: '/compatibility', icon: Heart, iconColorVar: '--ic-compatibility' },
  transits: { key: 'transits', label: 'Transits', path: '/transits', icon: RefreshCw, iconColorVar: '--ic-transits' },
  panchang: { key: 'panchang', label: 'Panchang', path: '/panchang', icon: MoonStar, iconColorVar: '--ic-panchang' },
  dasha: { key: 'dasha', label: 'Dasha', path: '/dasha', icon: Clock, iconColorVar: '--ic-dasha' },
  muhurta: { key: 'muhurta', label: 'Muhurta', path: '/muhurta', icon: Star, iconColorVar: '--ic-muhurta' },
  astrologers: { key: 'astrologers', label: 'Astrologers', path: '/astrologers', icon: Star, iconColorVar: '--ic-astrologers' },
  consultations: { key: 'consultations', label: 'Consultations', path: '/consultations', icon: MessageSquare, iconColorVar: '--ic-consultations', counterColorBgVar: '--ct-consultations-bg', counterColorTextVar: '--ct-consultations-text' },
  settings: { key: 'settings', label: 'Settings', path: '/settings', icon: Settings, iconColorVar: '--ic-dashboard' },
}

export const sidebarGroups: SidebarGroup[] = [
  { label: 'Overview', items: [sidebarMenuItems.dashboard, sidebarMenuItems.charts, sidebarMenuItems.persons, sidebarMenuItems.ai] },
  { label: 'Explore', items: [sidebarMenuItems.compatibility, sidebarMenuItems.transits, sidebarMenuItems.panchang, sidebarMenuItems.dasha, sidebarMenuItems.muhurta] },
  { label: 'Connect', items: [sidebarMenuItems.astrologers, sidebarMenuItems.consultations] },
]
```

- [ ] **Step 2: Commit**
```bash
git add web/config/sidebar-config.ts
git commit -m "feat(web): add icon colors and counter badge colors to sidebar config"
```

---

## Task 3: Rebuild Sidebar Component

**Files:**
- Modify: `web/components/layout/app-sidebar.tsx`

- [ ] **Step 1: Rewrite `app-sidebar.tsx` with colored icons and themed styling**

Key requirements:
- Each nav icon renders with its unique color via CSS variable (`style={{ color: 'var(--ic-dashboard)' }}`)
- Counter badges use colored backgrounds (`style={{ background: 'var(--ct-charts-bg)', color: 'var(--ct-charts-text)' }}`)
- Active item: gold left border (3px), themed active background, bold text
- Dark mode: Observatory styling (gradient bg, gold top line, gold glow on active)
- Light mode: Stripe+Gold styling (#F8F9FB bg, gold-tinted active row, black bold active text)
- Sidebar header: "Josi" logo (DM Serif Display) + MYSTIC badge (gold)
- Footer: gold gradient avatar + user name + plan
- Gold top accent line (`--sb-top-line` variable)
- Section dividers between groups

**IMPORTANT:** The sidebar background MUST use inline `style={{ background: 'var(--sb-bg)' }}` (not Tailwind's `bg-` utility) because the dark theme value is a CSS gradient, not a solid color. Tailwind's `bg-[var(--sb-bg)]` generates `background-color` which ignores gradients.

The component should use CSS variables for all theme-dependent colors (no conditional class logic). The CSS variables in `globals.css` handle the theme switching.

Structure:
```
<aside> (bg via --sb-bg, border-right via --sb-border)
  <div class="top-line" /> (1-2px gold accent)
  <header> Logo + MYSTIC badge </header>
  <nav>
    {groups.map(group => (
      <>
        <GroupLabel />
        {group.items.map(item => (
          <NavItem icon={item.icon} color={item.iconColorVar} counter={...} />
        ))}
        <Divider />
      </>
    ))}
  </nav>
  <footer> Avatar + Name + Plan </footer>
</aside>
```

- [ ] **Step 2: Verify sidebar renders in both themes**

Run dev server, toggle theme via browser console `document.documentElement.classList.toggle('dark')`. Verify:
- Icons show unique colors in both themes
- Active item has gold left border + themed background
- Counter badges are colored (blue, purple, coral)
- Gold top accent line visible
- MYSTIC badge is gold
- Logo reads "Josi" with no spacing issues

- [ ] **Step 3: Commit**
```bash
git add web/components/layout/app-sidebar.tsx
git commit -m "feat(web): rebuild sidebar with colored icons, badges, and dual-theme support"
```

---

## Task 4: Update Dashboard Layout

**Files:**
- Modify: `web/app/(dashboard)/layout.tsx`
- Modify: `web/components/layout/user-dropdown.tsx`

- [ ] **Step 1: Simplify dashboard layout — sidebar-only for Phase 1**

Remove the `navMode` toggle logic. Keep sidebar-only layout:
- Sidebar: fixed left, 240px expanded / 64px collapsed
- Header: sticky top, greeting + date + "+ Add Widget" gold button + UserDropdown
- Main: flex-1 with padding, scrollable
- The "+ Add Widget" button: `bg-[var(--gold)] text-[var(--btn-add-text)]`

- [ ] **Step 2: Update `user-dropdown.tsx` — wire theme toggle to ThemeProvider**

Replace the hardcoded theme buttons with `next-themes` `useTheme()` hook:
```typescript
import { useTheme } from 'next-themes'
const { theme, setTheme } = useTheme()
```
The three theme options (Light, Dark, Auto) should call `setTheme('light')`, `setTheme('dark')`, `setTheme('system')`. Highlight the active option by comparing against `theme`.

- [ ] **Step 3: Verify layout + theme toggle**

Run dev server. Open dashboard. Click avatar → theme section. Toggle between Light/Dark/Auto. Verify:
- Sidebar switches between Observatory (dark) and Stripe+Gold (light)
- Content area switches between dark and white
- "+ Add Widget" button has white text in dark, black text in light
- Theme persists on page reload (localStorage)

- [ ] **Step 4: Commit**
```bash
git add web/app/(dashboard)/layout.tsx web/components/layout/user-dropdown.tsx
git commit -m "feat(web): simplify dashboard layout, wire theme toggle to ThemeProvider"
```

---

## Task 5: Widget System — Types, Config & State

**Files:**
- Create: `web/config/widget-config.ts`

- [ ] **Step 1: Define widget types and catalog**

```typescript
export type WidgetType =
  | 'todays-sky' | 'moon-phase' | 'muhurta-timeline' | 'panchang-summary'
  | 'chart-quick-view' | 'active-transits' | 'current-dasha'
  | 'ai-chat-access' | 'latest-reading' | 'neural-pathway'
  | 'bazi-summary' | 'western-transit' | 'celtic-tree'
  | 'available-astrologers' | 'upcoming-consultations'

export type WidgetSize = 'full' | 'half' | 'third'
export type TraditionBadge = 'vedic' | 'western' | 'chinese' | 'celtic' | 'ai' | 'general'

export interface WidgetDefinition {
  type: WidgetType
  label: string
  description: string
  icon: string   // emoji for catalog display
  tradition: TraditionBadge
  defaultSize: WidgetSize
  category: 'daily' | 'charts' | 'ai' | 'multi-tradition' | 'connect'
}

export interface WidgetInstance {
  id: string
  type: WidgetType
  size: WidgetSize
}

export const widgetCatalog: WidgetDefinition[] = [
  // Daily & Timing
  { type: 'todays-sky', label: "Today's Sky", description: 'Tithi, nakshatra, yoga for today', icon: '☀', tradition: 'vedic', defaultSize: 'full', category: 'daily' },
  { type: 'muhurta-timeline', label: 'Muhurta Timeline', description: 'Auspicious/inauspicious time windows', icon: '⏰', tradition: 'vedic', defaultSize: 'half', category: 'daily' },
  // Charts
  { type: 'chart-quick-view', label: 'Chart Quick View', description: 'Mini birth chart with key placements', icon: '📊', tradition: 'vedic', defaultSize: 'third', category: 'charts' },
  { type: 'current-dasha', label: 'Current Dasha', description: 'Your active planetary period', icon: '📈', tradition: 'vedic', defaultSize: 'third', category: 'charts' },
  { type: 'active-transits', label: 'Active Transits', description: 'Planets currently affecting your chart', icon: '🔄', tradition: 'vedic', defaultSize: 'third', category: 'charts' },
  // AI & Insights
  { type: 'ai-chat-access', label: 'AI Chat', description: 'Ask Josi AI anything', icon: '🤖', tradition: 'ai', defaultSize: 'third', category: 'ai' },
  { type: 'latest-reading', label: 'Latest Reading', description: 'Most recent AI-generated insight', icon: '📖', tradition: 'vedic', defaultSize: 'half', category: 'ai' },
  { type: 'neural-pathway', label: 'Neural Pathway', description: 'Daily reflection prompt', icon: '🧠', tradition: 'ai', defaultSize: 'half', category: 'ai' },
  // Multi-Tradition
  { type: 'bazi-summary', label: 'BaZi Summary', description: 'Chinese Four Pillars overview', icon: '🏮', tradition: 'chinese', defaultSize: 'third', category: 'multi-tradition' },
  { type: 'western-transit', label: 'Western Transit', description: 'Current Western transits', icon: '⭐', tradition: 'western', defaultSize: 'half', category: 'multi-tradition' },
  { type: 'celtic-tree', label: 'Celtic Tree Sign', description: 'Your Celtic tree and attributes', icon: '🌿', tradition: 'celtic', defaultSize: 'third', category: 'multi-tradition' },
  // Connect
  { type: 'available-astrologers', label: 'Available Astrologers', description: "Who's online now", icon: '👤', tradition: 'general', defaultSize: 'third', category: 'connect' },
  { type: 'upcoming-consultations', label: 'Upcoming Sessions', description: 'Your next booked session', icon: '📋', tradition: 'general', defaultSize: 'third', category: 'connect' },
]

export const defaultWidgets: WidgetInstance[] = [
  { id: 'w1', type: 'todays-sky', size: 'full' },
  { id: 'w2', type: 'chart-quick-view', size: 'third' },
  { id: 'w3', type: 'current-dasha', size: 'third' },
  { id: 'w4', type: 'ai-chat-access', size: 'third' },
  { id: 'w5', type: 'muhurta-timeline', size: 'half' },
  { id: 'w6', type: 'western-transit', size: 'half' },
  { id: 'w7', type: 'bazi-summary', size: 'third' },
  { id: 'w8', type: 'latest-reading', size: 'third' },
  { id: 'w9', type: 'available-astrologers', size: 'third' },
]

export const widgetCategories = [
  { key: 'daily', label: 'Daily & Timing' },
  { key: 'charts', label: 'Your Charts' },
  { key: 'ai', label: 'AI & Insights' },
  { key: 'multi-tradition', label: 'Multi-Tradition' },
  { key: 'connect', label: 'Connect' },
] as const
```

- [ ] **Step 2: Commit**
```bash
git add web/config/widget-config.ts
git commit -m "feat(web): add widget type definitions, catalog, and default layout"
```

---

## Task 6: Widget Card Wrapper & Tradition Badges

**Files:**
- Create: `web/components/dashboard/widgets/widget-card.tsx`

- [ ] **Step 1: Create shared widget card wrapper**

Every dashboard widget is wrapped in this component. It provides:
- Card styling (bg-card, border, rounded-2xl, shadow)
- Tradition badge (top-right, color-coded)
- Remove button (X, appears on hover, top-right)
- Consistent padding and typography

```typescript
interface WidgetCardProps {
  tradition: TraditionBadge
  onRemove?: () => void
  children: React.ReactNode
  className?: string
}
```

Tradition badge colors:
- vedic: gold bg + gold text
- western: blue bg + blue text
- chinese: red bg + red text (`rgba(196,80,60,0.1)` + `#C45040`)
- celtic: green bg + green text
- ai: purple bg + purple text
- general: muted bg + muted text

- [ ] **Step 2: Commit**
```bash
git add web/components/dashboard/widgets/widget-card.tsx
git commit -m "feat(web): add shared widget card wrapper with tradition badges"
```

---

## Task 7: Individual Widget Components

**Files:**
- Create: `web/components/dashboard/widgets/todays-sky.tsx`
- Create: `web/components/dashboard/widgets/chart-quick-view.tsx`
- Create: `web/components/dashboard/widgets/current-dasha.tsx`
- Create: `web/components/dashboard/widgets/ai-chat-access.tsx`
- Create: `web/components/dashboard/widgets/muhurta-timeline.tsx`
- Create: `web/components/dashboard/widgets/western-transit.tsx`
- Create: `web/components/dashboard/widgets/latest-reading.tsx`
- Create: `web/components/dashboard/widgets/available-astrologers.tsx`
- Create: `web/components/dashboard/widgets/bazi-summary.tsx`

- [ ] **Step 1: Create `todays-sky.tsx` — hero widget (full width)**

Displays: "TODAY'S SKY" gold label, "Shukla Chaturthi in Rohini" title (DM Serif Display), description, pills (Shubh Muhurta, Moon in Taurus, Wednesday - Mercury). Uses hero gradient background. Refer to the mockup's hero card styling.

- [ ] **Step 2: Create `chart-quick-view.tsx` — mini chart + key placements**

Displays: Mini South Indian chart (CSS grid, 4x4 with fixed sign positions), "Sun Pisces, Moon Scorpio", "Ascendant Cancer · Anuradha Pada 3", "Explore full chart →" link. All with static/placeholder data for now.

- [ ] **Step 3: Create `current-dasha.tsx` — dasha period with progress bar**

Displays: "Venus Maha Dasha · Saturn Antar Dasha", progress bar (35%), "Until March 2027", "Chat about this →" link.

- [ ] **Step 4: Create `ai-chat-access.tsx` — chat quick access**

Displays: Josi AI avatar (gold gradient circle with ✦), "Ask Josi AI about your chart", text input preview (non-functional), 2 suggestion chips.

- [ ] **Step 5: Create `muhurta-timeline.tsx` — horizontal time bar**

Displays: Horizontal color-coded timeline (6AM-6PM), segments colored green/red/gold/gray for good/rahu/shubh/neutral, current time marker, "Rahu Kalam: 12:00 - 1:30 PM" label.

- [ ] **Step 6: Create `western-transit.tsx` — western transit card**

Displays: "Mercury enters Aries in 3 days", brief transit description, [Western] badge. Static data.

- [ ] **Step 7: Create `latest-reading.tsx` — AI reading preview**

Displays: "The Water Within" title, 2-line excerpt, "Generated 2 days ago", "Read more →" and "Chat about this →" links.

- [ ] **Step 8: Create `available-astrologers.tsx` — astrologer mini card**

Displays: Astrologer avatar, "Priya Shankar", "Vedic · 15 years", "● Available now", "Book" gold button.

- [ ] **Step 9: Create `bazi-summary.tsx` — Chinese four pillars preview**

Displays: "Day Master: Yang Fire (丙)", mini 4-pillar display (4 columns), "Strong fire element this month", [Chinese] badge.

- [ ] **Step 10: Commit all widget components**
```bash
git add web/components/dashboard/widgets/
git commit -m "feat(web): add 9 dashboard widget components with placeholder data"
```

---

## Task 8: Widget Grid & Add Widget Modal

**Files:**
- Create: `web/components/dashboard/widget-grid.tsx`
- Create: `web/components/dashboard/add-widget-modal.tsx`

- [ ] **Step 1: Create `widget-grid.tsx` — responsive widget layout**

Manages widget state (array of WidgetInstance), renders widgets in a responsive grid:
- `full` widgets: span full width (col-span-3)
- `half` widgets: span 2 columns (col-span-2 on lg, full on mobile)
- `third` widgets: span 1 column (col-span-1 on lg, full on mobile)

Uses a 3-column CSS grid on desktop (`grid-cols-3`), 1 column on mobile.

State management:
- Initialize from localStorage (`josi-dashboard-widgets`) or `defaultWidgets`
- `addWidget(type)`: add to end, generate unique ID
- `removeWidget(id)`: remove by ID
- Save to localStorage on every change

Renders each WidgetInstance by looking up the component from a registry map:
```typescript
const widgetComponents: Record<WidgetType, React.ComponentType<{ onRemove: () => void }>> = {
  'todays-sky': TodaysSky,
  'chart-quick-view': ChartQuickView,
  // ...
}
```

- [ ] **Step 2: Create `add-widget-modal.tsx`**

Triggered by the "+ Add Widget" button. Shows:
- Overlay backdrop (semi-transparent)
- Modal panel (max-w-lg, centered)
- Title: "Add Widget"
- Categories listed with items grouped under each
- Each widget option: icon + name + description + "Add" button
- Already-added widgets show "Added ✓" instead of "Add"
- Close on backdrop click or X button

- [ ] **Step 3: Commit**
```bash
git add web/components/dashboard/widget-grid.tsx web/components/dashboard/add-widget-modal.tsx
git commit -m "feat(web): add widget grid layout and add-widget modal"
```

---

## Task 9: Dashboard Page — Final Assembly

**Files:**
- Modify: `web/app/(dashboard)/dashboard/page.tsx`

- [ ] **Step 1: Rewrite dashboard page**

Replace the current static stats page with the widget dashboard:
```typescript
'use client'

import { WidgetGrid } from '@/components/dashboard/widget-grid'

export default function DashboardPage() {
  return <WidgetGrid />
}
```

The greeting, date, and "+ Add Widget" button live in the layout's header (Task 4), not the page.

- [ ] **Step 2: Full integration test**

Run: `cd web && npm run dev`
Open: `http://localhost:4000/dashboard`

Verify in DARK mode:
- Observatory sidebar with colored icons, colored badges, gold top line
- Dark content area with widget cards
- "+ Add Widget" button is gold with white text
- Click "+ Add Widget" — modal opens with categorized widgets
- Close modal
- Hover on widget cards — remove button appears

Toggle to LIGHT mode (via avatar dropdown → theme):
- Stripe + Gold sidebar (#F8F9FB, gold active row, black bold active text)
- Pure white content area with white cards + subtle shadow
- "+ Add Widget" button is gold with black text
- All colored icons visible
- Colored counter badges visible

Toggle to AUTO mode — follows system preference.

Reload page — theme and widget layout persist.

- [ ] **Step 3: Commit**
```bash
git add web/app/(dashboard)/dashboard/page.tsx
git commit -m "feat(web): assemble widget-based dashboard with theme-aware layout"
```

---

## Task 10: Cleanup & Polish

**Files:**
- Various

- [ ] **Step 1: Remove dead code**

Remove old files/imports that are no longer used:
- `predictions` and `remedies` are intentionally removed from sidebar navigation. Their page files remain but are accessible only by direct URL (they're "Coming Soon" placeholders). Do NOT delete the page files.
- Clean up any unused CSS variables from `globals.css` (the old `.light` class is now replaced by `:root`)
- Remove the old `navMode` state and top-nav toggle logic if any remnants exist
- Verify no other files import `sidebarMenuItems` as an array (it's now a Record)

- [ ] **Step 2: Verify `npm run build` succeeds**

Run: `cd web && npm run build`
Fix any TypeScript errors or build warnings.

- [ ] **Step 3: Final commit**
```bash
git add -A
git commit -m "chore(web): clean up dead code and verify build"
```

---

## Summary

| Task | What | Files | Est. |
|------|------|-------|------|
| 1 | Theme system (CSS vars + ThemeProvider) | globals.css, ThemeContext, layout, providers | Medium |
| 2 | Sidebar config (icon/counter colors) | sidebar-config.ts | Small |
| 3 | Sidebar component rewrite | app-sidebar.tsx | Medium |
| 4 | Dashboard layout + theme toggle wiring | layout.tsx, user-dropdown.tsx | Small |
| 5 | Widget types & config | widget-config.ts | Small |
| 6 | Widget card wrapper | widget-card.tsx | Small |
| 7 | 9 widget components | widgets/*.tsx | Large |
| 8 | Widget grid + add modal | widget-grid.tsx, add-widget-modal.tsx | Medium |
| 9 | Dashboard page assembly | dashboard/page.tsx | Small |
| 10 | Cleanup & build verify | Various | Small |
