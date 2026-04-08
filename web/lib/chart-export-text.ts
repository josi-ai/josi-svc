/**
 * Generates a 1991-format ASCII text export of an astrology chart.
 * Reference: test_data/chart-export-format-govindarajan.txt
 */
import type { ChartDetail, ChartDetailPlanetData, ChartDetailPerson, ChartDetailDashaPeriod } from '@/types';

// --- Constants ---
const P_ABBR: Record<string, string> = {
  Sun: 'SURY', Moon: 'CHAN', Mars: 'KUJA', Mercury: 'BUDH', Jupiter: 'GURU',
  Venus: 'SUKR', Saturn: 'SANI', Rahu: 'RAHU', Ketu: 'KETU', Ascendant: 'LAGN',
};
const P_SHORT: Record<string, string> = {
  Sun: 'SUR', Moon: 'CHA', Mars: 'KUJ', Mercury: 'BUD', Jupiter: 'GUR',
  Venus: 'SUK', Saturn: 'SAN', Rahu: 'RAH', Ketu: 'KET', Ascendant: 'LAG',
};
const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
  'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const S_LORD: Record<string, string> = {
  Aries:'KUJA',Taurus:'SUKR',Gemini:'BUDH',Cancer:'CHAN',Leo:'SURY',Virgo:'BUDH',
  Libra:'SUKR',Scorpio:'KUJA',Sagittarius:'GURU',Capricorn:'SANI',Aquarius:'SANI',Pisces:'GURU',
};
const NAK_RULER: Record<string, string> = {
  Ashwini:'KETU',Bharani:'SUKR',Krittika:'SURY',Rohini:'CHAN',Mrigashira:'KUJA',
  Ardra:'RAHU',Arudra:'RAHU',Punarvasu:'GURU',Pushya:'SANI',Ashlesha:'BUDH',Aslesha:'BUDH',
  Magha:'KETU','Purva Phalguni':'SUKR','Uttara Phalguni':'SURY',Hasta:'CHAN',Chitra:'KUJA',
  Swati:'RAHU',Vishakha:'GURU',Anuradha:'SANI',Jyeshtha:'BUDH',Mula:'KETU',
  'Purva Ashadha':'SUKR','Uttara Ashadha':'SURY',Shravana:'CHAN',Dhanishta:'KUJA',
  Shatabhisha:'RAHU','Purva Bhadrapada':'GURU','Uttara Bhadrapada':'SANI',Revati:'BUDH',
};
const P_ORD = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'];
const WDAYS = ['SUNDAY','MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'];
// South Indian fixed-sign cell map: sign index -> [row, col]
const SI: Record<number, [number, number]> = {
  11:[0,0],0:[0,1],1:[0,2],2:[0,3],10:[1,0],3:[1,3],9:[2,0],4:[2,3],
  8:[3,0],7:[3,1],6:[3,2],5:[3,3],
};

// --- Helpers ---
function fmtDeg(lng: number): string {
  const d = Math.floor(lng), m = Math.round((lng - d) * 60);
  return `${String(d).padStart(3)}:${String(m).padStart(2, ' ')}`;
}
function fmtDM(deg: number): string {
  const d = Math.floor(deg), m = Math.round((deg - d) * 60);
  return `${d}:${String(m).padStart(2, '0')}`;
}
function ab(n: string) { return P_ABBR[n] || n.slice(0, 4).toUpperCase(); }
function sh(n: string) { return P_SHORT[n] || n.slice(0, 3).toUpperCase(); }
function nakR(nak?: string): string {
  if (!nak) return '    ';
  for (const [k, v] of Object.entries(NAK_RULER))
    if (nak.toLowerCase().startsWith(k.toLowerCase())) return v;
  return '    ';
}
function si(sign?: string): number {
  if (!sign) return -1;
  return SIGNS.findIndex(s => s.toLowerCase() === sign.toLowerCase());
}
function sStr(v: unknown): string {
  if (v == null) return '';
  if (typeof v === 'object' && 'name' in (v as Record<string, unknown>))
    return String((v as Record<string, unknown>).name);
  return String(v);
}
function shortDate(iso: string): string {
  try {
    const d = new Date(iso);
    const ms = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
    return `${String(d.getUTCDate()).padStart(2)}${ms[d.getUTCMonth()]}${d.getUTCFullYear()}`;
  } catch { return iso; }
}

// --- South Indian ASCII Grid ---
function buildGrid(
  planets: Record<string, ChartDetailPlanetData>, ascSign?: string, label = 'R A S I'
): string[] {
  const cells: Record<number, string[]> = {};
  for (let i = 0; i < 12; i++) cells[i] = [];
  if (ascSign) { const idx = si(ascSign); if (idx >= 0) cells[idx].push('LAG'); }
  for (const [name, data] of Object.entries(planets)) {
    const idx = si(data.sign);
    if (idx >= 0) cells[idx].push(sh(name));
  }
  const W = 7, H = 5;
  const grid: string[][] = Array.from({ length: 4 }, () => Array(4).fill(''));
  for (let s = 0; s < 12; s++) {
    const [r, c] = SI[s];
    const names = cells[s];
    const lines: string[] = []; let cur = '';
    for (const n of names) {
      if (cur.length + (cur ? 1 : 0) + n.length > W) { lines.push(cur); cur = n; }
      else cur = cur ? cur + ' ' + n : n;
    }
    if (cur) lines.push(cur);
    grid[r][c] = lines.join('\n');
  }
  const out: string[] = [], sep = '+' + '-------+'.repeat(4);
  for (let r = 0; r < 4; r++) {
    out.push(sep);
    for (let line = 0; line < H; line++) {
      let row = '';
      for (let c = 0; c < 4; c++) {
        const isCenter = (r === 1 || r === 2) && (c === 1 || c === 2);
        if (isCenter) {
          if (c === 1) {
            if (r === 1 && line === Math.floor(H / 2))
              row += '!' + ('    ' + label).padEnd(15);
            else row += '!' + ' '.repeat(15);
          }
          if (c === 2) continue;
        } else {
          const cl = grid[r][c].split('\n');
          const st = Math.floor((H - cl.length) / 2);
          const idx = line - st;
          row += '!' + (idx >= 0 && idx < cl.length ? cl[idx] : '').padEnd(W);
        }
      }
      row += '!'; out.push(row);
    }
  }
  out.push(sep);
  return out;
}

// --- Header ---
function buildHeader(chart: ChartDetail, person?: ChartDetailPerson | null): string[] {
  const name = person?.name?.toUpperCase() || 'UNKNOWN';
  const dob = person?.date_of_birth ? new Date(person.date_of_birth) : null;
  const dateStr = dob
    ? `${dob.getUTCDate().toString().padStart(2,'0')}-${(dob.getUTCMonth()+1).toString().padStart(2,'0')}-${dob.getUTCFullYear()}`
    : '--';
  const wd = dob ? WDAYS[dob.getUTCDay()] : '';
  const time = person?.time_of_birth?.slice(0, 5) || '--:--';
  const place = person?.place_of_birth || '';
  const pg = chart.chart_data?.panchang;
  const ti = pg?.tithi;
  const pak = ti && typeof ti === 'object' && ti.paksha ? ti.paksha.toUpperCase() : '';
  const ay = pg?.ayanamsa;
  const ayS = ay != null
    ? `${Math.floor(ay)}\u00B0${Math.round((ay - Math.floor(ay)) * 60).toString().padStart(2,'0')}'`
    : chart.ayanamsa || '';
  const sr = pg?.sunrise || '', ss = pg?.sunset || '';
  const sunStr = sr && ss ? `${sr}/${ss} (IST)` : '';
  const nak = pg?.nakshatra;
  const nakN = sStr(nak).toUpperCase(), nakP = nak && typeof nak === 'object' ? nak.pada : '';
  const tiN = sStr(ti).toUpperCase();
  const yoga = sStr(pg?.yoga).toUpperCase(), karana = sStr(pg?.karana).toUpperCase();
  return [
    `  (VER 6:1 9/91)          HOROSCOPE OF ${name}`, '',
    ` DATE OF BIRTH: ${dateStr} ${wd.padEnd(12)} TIME:${time}HRS(IST) TIME ZONE: 5.50 HRS`,
    ` ${pak.padEnd(9)}${' '.repeat(30)}PLACE:${place}`,
    ` SIDR.TIME:--:--:-- AYANAMSA:${ayS.padEnd(12)} SUNRISE/SET: ${sunStr}`,
    ` STAR:${nakN.padEnd(12)} PADA ${nakP || '-'}    THITHI:${tiN}`,
    ` YOGA:${yoga.padEnd(35)}KARANA:${karana}`, '',
  ];
}

// --- Nirayana Longitudes ---
function buildLongitudes(planets: Record<string, ChartDetailPlanetData>): string[] {
  const lines = [
    ' NIRAYANA LONGITUDES:', ' -------------------',
    ' PLANET DEG:MIN  STAR   PADA  RULER      PLANET DEG:MIN  STAR   PADA  RULER     ', '',
  ];
  const ordered = P_ORD.filter(p => planets[p]);
  const extra = Object.keys(planets).filter(p => !P_ORD.includes(p) && p !== 'Ascendant');
  const all = [...ordered, ...extra, 'Ascendant'].filter(p => planets[p] || p === 'Ascendant');
  const fmt = (name: string): string => {
    const d = name === 'Ascendant' ? null : planets[name];
    if (!d && name !== 'Ascendant') return ' '.repeat(40);
    const deg = d ? fmtDeg(d.longitude).padEnd(8) : '       ';
    const nk = d ? (d.nakshatra || '').toUpperCase().slice(0, 8).padEnd(10) : '          ';
    const pd = String(d?.nakshatra_pada ?? d?.pada ?? ' ').padEnd(2);
    const rl = d ? nakR(d.nakshatra).padEnd(6) : '      ';
    return ` ${ab(name).padEnd(6)}${deg}${nk}${pd}  ${rl}`;
  };
  for (let i = 0; i < all.length; i += 2) {
    lines.push(fmt(all[i]) + (i + 1 < all.length ? fmt(all[i + 1]) : ''));
  }
  const retro = Object.entries(planets)
    .filter(([, d]) => d.is_retrograde || (d.speed != null && d.speed < 0))
    .map(([n]) => ab(n));
  if (retro.length) { lines.push(''); lines.push(` PLANETS UNDER RETROGRESSION : ${retro.join('; ')};`); }
  return lines;
}

// --- Dasha ---
function buildDasha(chart: ChartDetail): string[] {
  const dasha = chart.chart_data?.dasha;
  if (!dasha) return [];
  const lines: string[] = [];
  const cur = dasha.current_dasha;
  if (cur?.mahadasha) {
    const r = cur.mahadasha.remaining_days ?? 0;
    const y = Math.floor(r / 365.25), mo = Math.floor((r % 365.25) / 30.44), d = Math.round(r % 30.44);
    lines.push('', ` ${ab(cur.mahadasha.planet)} DASA REMAINING AT TIME OF BIRTH   ${y} YEARS  ${mo} MONTHS  ${d} DAYS`);
  }
  const mds = dasha.mahadashas as ChartDetailDashaPeriod[] | undefined;
  if (mds?.length) {
    lines.push('', ' DASA-BHUKTHI DETAILS', ' -------------------',
      ' DASA ENDS ON   BHUKTHI FROM - TO    BHUKTHI FROM - TO    BHUKTHI FROM - TO    ');
    for (const md of mds)
      lines.push(` ${ab(md.planet).padEnd(4)} ${md.end_date ? shortDate(md.end_date) : ''}`);
  }
  return lines;
}

// --- Bhava Cusps ---
function buildCusps(chart: ChartDetail): string[] {
  const houses = chart.chart_data?.houses, cusps = chart.house_cusps;
  const degs: number[] = [];
  if (Array.isArray(cusps) && cusps.length >= 12) for (let i = 0; i < 12; i++) degs.push(cusps[i]);
  else if (Array.isArray(houses) && houses.length >= 12) for (let i = 0; i < 12; i++) degs.push((houses as number[])[i]);
  if (degs.length < 12) return [];
  const lines = [
    '  BHAVA   MIDDLE     START    RASI  STAR  BHAVA   MIDDLE     START    RASI  STAR',
    '          DEG:MN     DEG:MN   LORD  LORD          DEG:MN     DEG:MN   LORD  LORD',
  ];
  const fh = (i: number) => {
    const d = degs[i], s = SIGNS[Math.floor(d / 30) % 12];
    return `  ${String(i + 1).padStart(2)}   ${fmtDM(d).padStart(7)}   ${' '.repeat(8)} ${(S_LORD[s] || '    ').padEnd(5)} ----`;
  };
  for (let i = 0; i < 12; i += 2) lines.push(fh(i) + fh(i + 1));
  return lines;
}

// --- Main Export ---
export function generateChartText(chart: ChartDetail, person?: ChartDetailPerson | null): string {
  const planets = (chart.chart_data?.planets || chart.planet_positions || {}) as Record<string, ChartDetailPlanetData>;
  const ascSign = chart.chart_data?.ascendant?.sign;
  const out: string[] = [];
  out.push(...buildHeader(chart, person));
  out.push(...buildLongitudes(planets));
  out.push('');
  for (const l of buildGrid(planets, ascSign, 'R A S I')) out.push(' ' + l);
  out.push(...buildDasha(chart));
  out.push('');
  for (const l of buildGrid(planets, ascSign, 'BHAVA')) out.push('                     ' + l);
  out.push(...buildCusps(chart));
  return out.join('\n');
}

export function getExportFilename(person?: ChartDetailPerson | null): string {
  const name = person?.name?.replace(/[^a-zA-Z0-9]/g, '_') || 'chart';
  return `horoscope_${name}_${new Date().toISOString().slice(0, 10)}.txt`;
}
