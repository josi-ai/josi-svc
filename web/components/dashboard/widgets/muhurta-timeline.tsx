'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { WidgetCard } from './widget-card'
import Link from 'next/link'
import type { PanchangResponse } from '@/types'

/* ---------- Helpers ---------- */

const DS = 360, DE = 1080 // 6AM, 6PM in minutes

function pt(s: string): number {
  if (!s) return 0
  const ap = s.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i)
  if (ap) { let h = +ap[1]; if (ap[3].toUpperCase() === 'PM' && h !== 12) h += 12; if (ap[3].toUpperCase() === 'AM' && h === 12) h = 0; return h * 60 + +ap[2] }
  const h24 = s.match(/^(\d{1,2}):(\d{2})/); return h24 ? +h24[1] * 60 + +h24[2] : 0
}

function ft(m: number) { const h = Math.floor(m / 60), mn = m % 60, p = h >= 12 ? 'PM' : 'AM'; return `${h === 0 ? 12 : h > 12 ? h - 12 : h}:${String(mn).padStart(2, '0')} ${p}` }

function pr(s: string) { const p = s.split(/\s*[-\u2013]\s*/); if (p.length !== 2) return null; const a = pt(p[0].trim()), b = pt(p[1].trim()); return a && b && a < b ? { start: a, end: b } : null }

type Seg = { s: number; e: number; t: string }

interface MuhurtaWidgetData {
  rk: { start: string; end: string } | null
  ab: { start: string; end: string } | null
  sunrise: string
  sunset: string
  segs: Seg[]
}

const COLORS: Record<string, string> = { good: 'var(--bar-good)', rahu: 'var(--bar-avoid)', abhijit: 'var(--bar-special)' }

function buildSegs(rk: { start: number; end: number } | null, ab: { start: number; end: number } | null): Seg[] {
  const ps: { s: number; e: number; t: string }[] = []
  if (rk && rk.start < DE && rk.end > DS) ps.push({ s: Math.max(rk.start, DS), e: Math.min(rk.end, DE), t: 'rahu' })
  if (ab && ab.start < DE && ab.end > DS) ps.push({ s: Math.max(ab.start, DS), e: Math.min(ab.end, DE), t: 'abhijit' })
  ps.sort((a, b) => a.s - b.s)
  const segs: Seg[] = []; let c = DS
  for (const p of ps) { if (c < p.s) segs.push({ s: c, e: p.s, t: 'good' }); segs.push(p); c = p.e }
  if (c < DE) segs.push({ s: c, e: DE, t: 'good' }); return segs
}

/* ---------- Component ---------- */

export default function MuhurtaTimeline({ onRemove }: { onRemove: () => void }) {
  const { location, isLoading: pl } = useDefaultProfile()
  const today = new Date().toISOString().split('T')[0] + 'T06:00:00'

  const { data, isLoading, isError } = useQuery<MuhurtaWidgetData>({
    queryKey: ['muhurta-widget', today, location.latitude, location.longitude],
    queryFn: async () => {
      const res = await apiClient.get<PanchangResponse>(`/api/v1/panchang/?date=${encodeURIComponent(today)}&latitude=${location.latitude}&longitude=${location.longitude}&timezone=${encodeURIComponent(location.timezone)}`)
      const d = res.data?.detailed_panchang ?? null
      const rk = pr(d?.inauspicious_times?.rahu_kaal || ''), ab = pr(d?.auspicious_times?.abhijit_muhurta || '')
      return { rk: rk ? { start: ft(rk.start), end: ft(rk.end) } : null, ab: ab ? { start: ft(ab.start), end: ft(ab.end) } : null, sunrise: d?.sunrise || '', sunset: d?.sunset || '', segs: buildSegs(rk, ab) }
    },
    enabled: !pl, staleTime: 1000 * 60 * 30,
  })

  const now = new Date(), nowMin = now.getHours() * 60 + now.getMinutes()
  const inR = nowMin >= DS && nowMin <= DE, pct = inR ? ((nowMin - DS) / (DE - DS)) * 100 : 0

  const status = !data ? null
    : data.rk && nowMin >= pt(data.rk.start) && nowMin < pt(data.rk.end) ? { label: '\u26A0 Rahu Kalam active', color: 'var(--red)' }
    : data.ab && nowMin >= pt(data.ab.start) && nowMin < pt(data.ab.end) ? { label: '\u2726 Auspicious period', color: 'var(--gold)' }
    : { label: 'Neutral period', color: 'var(--text-faint)' }

  if (isLoading || pl) return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div className="p-5 animate-pulse space-y-3">
        <div className="h-2.5 w-24 rounded" style={{ background: 'var(--border)' }} />
        <div className="h-5 w-40 rounded" style={{ background: 'var(--border-subtle)' }} />
        <div className="h-1.5 w-full rounded-full" style={{ background: 'var(--border-subtle)' }} />
        <div className="grid grid-cols-2 gap-2">{[1,2,3,4].map(i => <div key={i} className="h-8 rounded" style={{ background: 'var(--border-subtle)' }} />)}</div>
      </div>
    </WidgetCard>
  )

  if (isError || !data) return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div className="p-5">
        <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--text-faint)', marginBottom: 8 }}>Today&apos;s Muhurta</div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>Unable to load timing data.</p>
      </div>
    </WidgetCard>
  )

  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div className="p-5">
        <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--text-faint)', marginBottom: 10 }}>Today&apos;s Muhurta</div>
        {status && <div style={{ fontSize: 15, fontWeight: 600, color: status.color, marginBottom: 14, lineHeight: 1.2 }}>{status.label}</div>}

        {/* Continuous bar — 6AM to 6PM */}
        <div style={{ position: 'relative', marginBottom: 16 }}>
          {/* The bar — tall enough to read */}
          <div style={{ position: 'relative', height: 44, borderRadius: 8, overflow: 'hidden', display: 'flex', border: '1px solid rgba(255,255,255,0.12)' }}>
            {data.segs.map((seg, i) => (
              <div key={i} style={{ flex: seg.e - seg.s, background: COLORS[seg.t] || 'rgba(255,255,255,0.05)', minWidth: 1 }} />
            ))}
            {/* Hour dividers — every 2 hours bold, others medium */}
            {Array.from({ length: 11 }, (_, i) => {
              const m = DS + (i + 1) * 60
              const pctVal = ((m - DS) / (DE - DS)) * 100
              const isEven = (i + 1) % 2 === 0
              return (
                <div key={`h${i}`} style={{ position: 'absolute', top: 0, bottom: 0, left: `${pctVal}%`, width: isEven ? 2 : 1, background: isEven ? 'rgba(255,255,255,0.35)' : 'rgba(255,255,255,0.15)', zIndex: 1 }} />
              )
            })}
            {/* 30-min dividers */}
            {Array.from({ length: 12 }, (_, i) => {
              const m = DS + i * 60 + 30
              const pctVal = ((m - DS) / (DE - DS)) * 100
              return (
                <div key={`m${i}`} style={{ position: 'absolute', top: '25%', bottom: '25%', left: `${pctVal}%`, width: 1, background: 'rgba(255,255,255,0.08)', zIndex: 1 }} />
              )
            })}
            {/* Now marker */}
            {inR && <div style={{ position: 'absolute', top: -3, bottom: -3, left: `${pct}%`, width: 3, background: 'var(--gold-bright)', borderRadius: 2, boxShadow: '0 0 10px rgba(212,160,74,0.9)', zIndex: 3 }} />}
          </div>
          {/* Hour labels — every 2 hours only to avoid overlap */}
          <div style={{ position: 'relative', height: 18, marginTop: 4 }}>
            {[0, 2, 4, 6, 8, 10, 12].map(i => {
              const h = i + 6
              const label = h === 6 ? '6 AM' : h === 12 ? '12 PM' : h === 18 ? '6 PM' : h > 12 ? `${h - 12} PM` : `${h} AM`
              const pctVal = (i / 12) * 100
              return (
                <span key={i} style={{ position: 'absolute', left: `${pctVal}%`, transform: 'translateX(-50%)', fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{label}</span>
              )
            })}
          </div>
          {/* Legend */}
          <div style={{ display: 'flex', gap: 14, fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 10, height: 10, borderRadius: 3, background: 'var(--bar-avoid)' }} />Rahu Kaal</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 10, height: 10, borderRadius: 3, background: 'var(--bar-special)' }} />Abhijit</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 10, height: 10, borderRadius: 3, background: 'var(--bar-good)' }} />Good</span>
          </div>
        </div>

        {/* Key times */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {data.rk && <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--red-bg)', border: '1px solid rgba(200,80,60,0.15)' }}>
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.2, color: 'var(--red)', marginBottom: 2 }}>Rahu Kaal</div>
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{data.rk.start} – {data.rk.end}</div>
          </div>}
          {data.ab && <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--gold-bg)', border: '1px solid rgba(200,145,58,0.15)' }}>
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.2, color: 'var(--gold)', marginBottom: 2 }}>Abhijit Muhurta</div>
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{data.ab.start} – {data.ab.end}</div>
          </div>}
          {data.sunrise && <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--surface)' }}>
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.2, color: 'var(--text-faint)', marginBottom: 2 }}>Sunrise</div>
            <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-secondary)' }}>{data.sunrise}</div>
          </div>}
          {data.sunset && <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--surface)' }}>
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.2, color: 'var(--text-faint)', marginBottom: 2 }}>Sunset</div>
            <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-secondary)' }}>{data.sunset}</div>
          </div>}
        </div>

        <Link href="/muhurta" style={{ display: 'inline-block', marginTop: 16, fontSize: 13, fontWeight: 600, color: 'var(--gold)', textDecoration: 'none', letterSpacing: 0.3 }}>View full Muhurta &rarr;</Link>
      </div>
    </WidgetCard>
  )
}
