'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useDefaultProfile } from '@/hooks/use-default-profile'
import { WidgetCard } from './widget-card'

/* ---------- Types ---------- */

interface PlanetData {
  longitude: number
  sign: string
  house: number
  nakshatra?: string
  pada?: number
}

interface ChartData {
  chart_type: string
  ayanamsa_name?: string
  ascendant: {
    longitude: number
    sign: string
    nakshatra?: string
    pada?: number
  }
  planets: Record<string, PlanetData>
}

interface Chart {
  chart_id: string
  chart_type: string
  chart_data: ChartData
  person_id: string
}

/* ---------- Sign abbreviation map ---------- */

const PLANET_ABBREV: Record<string, string> = {
  Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me',
  Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke',
}

const SIGN_ORDER = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
]

/* ---------- South Indian chart helpers ---------- */

function buildCellData(chartData: ChartData) {
  // Map planets to signs
  const signPlanets: Record<string, string[]> = {}
  for (const sign of SIGN_ORDER) signPlanets[sign] = []

  for (const [name, data] of Object.entries(chartData.planets)) {
    if (data.sign && signPlanets[data.sign]) {
      signPlanets[data.sign].push(PLANET_ABBREV[name] || name.slice(0, 2))
    }
  }

  // Mark ascendant sign
  const ascSign = chartData.ascendant?.sign

  return { signPlanets, ascSign }
}

/* ---------- Skeleton ---------- */

function Skeleton() {
  return (
    <div className="p-5 animate-pulse space-y-3">
      <div className="h-3 w-28 rounded" style={{ background: 'var(--border)' }} />
      <div className="flex gap-4 items-start">
        <div
          className="w-[100px] h-[100px] flex-shrink-0 rounded"
          style={{ background: 'var(--border-subtle)' }}
        />
        <div className="space-y-2 flex-1">
          <div className="h-4 w-40 rounded" style={{ background: 'var(--border)' }} />
          <div className="h-3 w-48 rounded" style={{ background: 'var(--border-subtle)' }} />
          <div className="h-3 w-28 rounded" style={{ background: 'var(--border-subtle)' }} />
        </div>
      </div>
    </div>
  )
}

/* ---------- Component ---------- */

export default function ChartQuickView({ onRemove }: { onRemove: () => void }) {
  const { defaultProfile, isLoading: profileLoading } = useDefaultProfile()

  const {
    data: chartsResponse,
    isLoading: chartsLoading,
    isError,
  } = useQuery({
    queryKey: ['person-charts', defaultProfile?.person_id],
    queryFn: () =>
      apiClient.get<Chart[]>(
        `/api/v1/charts/person/${defaultProfile!.person_id}`
      ),
    enabled: !profileLoading && !!defaultProfile?.person_id,
    staleTime: 1000 * 60 * 60, // 1 hour
    retry: 1,
  })

  const isLoading = profileLoading || chartsLoading

  const charts = chartsResponse?.data || []
  // Prefer a vedic chart; fall back to first chart
  const chart = charts.find((c) => c.chart_type === 'vedic') || charts[0] || null
  const chartData = chart?.chart_data

  // Extract display info
  const sunSign = chartData?.planets?.Sun?.sign
  const moonSign = chartData?.planets?.Moon?.sign
  const ascSign = chartData?.ascendant?.sign
  const ascNak = chartData?.ascendant?.nakshatra
  const ascPada = chartData?.ascendant?.pada
  const ayanamsa = chartData?.ayanamsa_name

  // Build grid data
  const cellData = chartData ? buildCellData(chartData) : null

  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      {isLoading ? (
        <Skeleton />
      ) : !defaultProfile ? (
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Chart Quick View
          </div>
          <p className="text-sm text-[var(--text-secondary)] mb-3">
            Create a birth profile to see your chart.
          </p>
          <a
            href="/profiles"
            className="text-xs font-semibold"
            style={{ color: 'var(--gold)' }}
          >
            Add profile &rarr;
          </a>
        </div>
      ) : isError || !chartData ? (
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Chart Quick View
          </div>
          <p className="text-sm text-[var(--text-secondary)] mb-3">
            {charts.length === 0
              ? 'No charts calculated yet.'
              : 'Unable to load chart data.'}
          </p>
          <a
            href="/charts/new"
            className="text-xs font-semibold"
            style={{ color: 'var(--gold)' }}
          >
            Calculate your first chart &rarr;
          </a>
        </div>
      ) : (
        <div className="p-5">
          <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
            Chart Quick View
          </div>

          <div className="flex gap-4 items-start">
            {/* South Indian Chart Grid */}
            <div className="w-[100px] h-[100px] flex-shrink-0 border-[1.5px] border-[var(--border-strong)]">
              <div className="grid grid-cols-4 grid-rows-4 w-full h-full">
                {/* Row 1 */}
                <Cell sign="Pis" planets={cellData!.signPlanets['Pisces']} isAsc={cellData!.ascSign === 'Pisces'} />
                <Cell sign="Ari" planets={cellData!.signPlanets['Aries']} isAsc={cellData!.ascSign === 'Aries'} />
                <Cell sign="Tau" planets={cellData!.signPlanets['Taurus']} isAsc={cellData!.ascSign === 'Taurus'} />
                <Cell sign="Gem" planets={cellData!.signPlanets['Gemini']} isAsc={cellData!.ascSign === 'Gemini'} />

                {/* Row 2 */}
                <Cell sign="Aqu" planets={cellData!.signPlanets['Aquarius']} isAsc={cellData!.ascSign === 'Aquarius'} />
                <div className="col-span-2 row-span-2 border border-[var(--border)] flex items-center justify-center text-[7px] font-semibold text-[var(--text-muted)] bg-[var(--card)]">
                  Rasi
                </div>
                <Cell sign="Can" planets={cellData!.signPlanets['Cancer']} isAsc={cellData!.ascSign === 'Cancer'} />

                {/* Row 3 */}
                <Cell sign="Cap" planets={cellData!.signPlanets['Capricorn']} isAsc={cellData!.ascSign === 'Capricorn'} />
                <Cell sign="Leo" planets={cellData!.signPlanets['Leo']} isAsc={cellData!.ascSign === 'Leo'} />

                {/* Row 4 */}
                <Cell sign="Sag" planets={cellData!.signPlanets['Sagittarius']} isAsc={cellData!.ascSign === 'Sagittarius'} />
                <Cell sign="Sco" planets={cellData!.signPlanets['Scorpio']} isAsc={cellData!.ascSign === 'Scorpio'} />
                <Cell sign="Lib" planets={cellData!.signPlanets['Libra']} isAsc={cellData!.ascSign === 'Libra'} />
                <Cell sign="Vir" planets={cellData!.signPlanets['Virgo']} isAsc={cellData!.ascSign === 'Virgo'} />
              </div>
            </div>

            {/* Chart info */}
            <div>
              <div className="font-display text-sm text-[var(--text-primary)] mb-1">
                {sunSign && moonSign
                  ? `Sun ${sunSign}, Moon ${moonSign}`
                  : 'Chart calculated'}
              </div>
              <div className="text-[11px] text-[var(--text-muted)] leading-relaxed mb-0.5">
                Ascendant {ascSign || '—'}
                {ascNak ? ` \u00B7 ${ascNak}` : ''}
                {ascPada ? ` Pada ${ascPada}` : ''}
              </div>
              {ayanamsa && (
                <div className="text-[11px] text-[var(--text-faint)] leading-relaxed">
                  Ayanamsa: {ayanamsa.charAt(0).toUpperCase() + ayanamsa.slice(1)}
                </div>
              )}
              <a
                href={`/charts/${chart.chart_id}`}
                className="text-xs font-semibold mt-3 inline-block cursor-pointer"
                style={{ color: 'var(--gold)' }}
              >
                Explore full chart &rarr;
              </a>
            </div>
          </div>
        </div>
      )}
    </WidgetCard>
  )
}

/* ---------- Cell sub-component ---------- */

function Cell({
  sign,
  planets,
  isAsc,
}: {
  sign: string
  planets: string[]
  isAsc?: boolean
}) {
  const hasPlanets = planets.length > 0
  const label = hasPlanets ? planets.join(' ') : ''

  return (
    <div
      className={`border-[0.5px] border-[var(--border)] flex items-center justify-center p-px text-center leading-tight text-[6px] ${
        hasPlanets ? 'font-semibold' : 'text-[var(--text-faint)]'
      }`}
      style={{
        color: hasPlanets ? 'var(--gold-bright)' : undefined,
        background: isAsc ? 'var(--gold-bg-subtle)' : undefined,
      }}
    >
      <span>
        {sign}
        {isAsc && !hasPlanets && (
          <>
            <br />
            As
          </>
        )}
        {hasPlanets && (
          <>
            <br />
            {isAsc ? `As ${label}` : label}
          </>
        )}
      </span>
    </div>
  )
}
