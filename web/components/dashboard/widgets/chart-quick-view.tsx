'use client'

import { WidgetCard } from './widget-card'

/** South Indian chart cell data: [sign abbreviation, planet abbreviation (if any)] */
const CHART_CELLS: Array<{ sign: string; planets?: string; isAsc?: boolean }> = [
  { sign: 'Pis' },
  { sign: 'Ari', planets: 'Ma' },
  { sign: 'Tau', planets: 'Mo' },
  { sign: 'Gem' },
  // row 2 left
  { sign: 'Aqu', planets: 'Sa' },
  // center (2x2) is separate
  // row 2 right
  { sign: 'Can', planets: 'As', isAsc: true },
  // row 3 left
  { sign: 'Cap', planets: 'Ke' },
  // row 3 right
  { sign: 'Leo' },
  // row 4
  { sign: 'Sag' },
  { sign: 'Sco', planets: 'Ju' },
  { sign: 'Lib', planets: 'Su Ve' },
  { sign: 'Vir', planets: 'Me Ra' },
]

export default function ChartQuickView({ onRemove }: { onRemove: () => void }) {
  return (
    <WidgetCard tradition="vedic" onRemove={onRemove}>
      <div className="p-5">
        <div className="text-[10px] uppercase tracking-[1.5px] font-semibold text-[var(--text-muted)] mb-3">
          Chart Quick View
        </div>

        <div className="flex gap-4 items-start">
          {/* South Indian Chart Grid */}
          <div
            className="w-[100px] h-[100px] flex-shrink-0 border-[1.5px] border-[var(--border-strong)]"
          >
            <div className="grid grid-cols-4 grid-rows-4 w-full h-full">
              {/* Row 1: Pi, Ar, Ta, Ge */}
              <Cell sign="Pis" />
              <Cell sign="Ari" planets="Ma" />
              <Cell sign="Tau" planets="Mo" />
              <Cell sign="Gem" />

              {/* Row 2: Aq, [center], [center], Ca */}
              <Cell sign="Aqu" planets="Sa" />
              <div
                className="col-span-2 row-span-2 border border-[var(--border)] flex items-center justify-center text-[7px] font-semibold text-[var(--text-muted)] bg-[var(--card)]"
              >
                Rasi
              </div>
              <Cell sign="Can" planets="As" isAsc />

              {/* Row 3: Cp, [center], [center], Le */}
              <Cell sign="Cap" planets="Ke" />
              <Cell sign="Leo" />

              {/* Row 4: Sg, Sc, Li, Vi */}
              <Cell sign="Sag" />
              <Cell sign="Sco" planets="Ju" />
              <Cell sign="Lib" planets="Su Ve" />
              <Cell sign="Vir" planets="Me Ra" />
            </div>
          </div>

          {/* Chart info */}
          <div>
            <div className="font-display text-sm text-[var(--text-primary)] mb-1">
              Sun Pisces, Moon Scorpio
            </div>
            <div className="text-[11px] text-[var(--text-muted)] leading-relaxed mb-0.5">
              Ascendant Cancer &middot; Anuradha Pada 3
            </div>
            <div className="text-[11px] text-[var(--text-faint)] leading-relaxed">
              Ayanamsa: Lahiri
            </div>
            <div
              className="text-xs font-semibold mt-3 cursor-pointer"
              style={{ color: 'var(--gold)' }}
            >
              Explore full chart &rarr;
            </div>
          </div>
        </div>
      </div>
    </WidgetCard>
  )
}

function Cell({
  sign,
  planets,
  isAsc,
}: {
  sign: string
  planets?: string
  isAsc?: boolean
}) {
  return (
    <div
      className={`border-[0.5px] border-[var(--border)] flex items-center justify-center p-px text-center leading-tight text-[6px] ${
        planets
          ? 'font-semibold'
          : 'text-[var(--text-faint)]'
      }`}
      style={{
        color: planets ? 'var(--gold-bright)' : undefined,
        background: isAsc ? 'var(--gold-bg-subtle)' : undefined,
      }}
    >
      <span>
        {sign}
        {planets && (
          <>
            <br />
            {planets}
          </>
        )}
      </span>
    </div>
  )
}
