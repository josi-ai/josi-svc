/**
 * Generates a printable HTML page for chart export via browser Print dialog.
 * Opens in a new window; user prints as PDF via Cmd+P / Ctrl+P.
 */
import type { ChartDetail, ChartDetailPlanetData, ChartDetailPerson } from '@/types';

const P_ORD = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'];
const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
  'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const S_LORD: Record<string, string> = {
  Aries:'Mars',Taurus:'Venus',Gemini:'Mercury',Cancer:'Moon',Leo:'Sun',Virgo:'Mercury',
  Libra:'Venus',Scorpio:'Mars',Sagittarius:'Jupiter',Capricorn:'Saturn',Aquarius:'Saturn',Pisces:'Jupiter',
};

function esc(s: string) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function fmtDeg(deg: number | undefined | null): string {
  if (deg == null || isNaN(deg)) return '\u2014';
  const d = Math.floor(deg), m = Math.round((deg - d) * 60);
  return `${d}\u00B0${m.toString().padStart(2, '0')}\u2032`;
}
function si(sign?: string): number {
  return sign ? SIGNS.findIndex(s => s.toLowerCase() === sign.toLowerCase()) : -1;
}
function sStr(v: unknown): string {
  if (v == null) return '\u2014';
  if (typeof v === 'object' && 'name' in (v as Record<string, unknown>)) return String((v as Record<string, unknown>).name);
  return String(v);
}
function sn(name: string): string {
  const m: Record<string, string> = {Sun:'Su',Moon:'Mo',Mars:'Ma',Mercury:'Me',Jupiter:'Ju',Venus:'Ve',Saturn:'Sa',Rahu:'Ra',Ketu:'Ke',Ascendant:'As'};
  return m[name] || name.slice(0, 2);
}

function buildSVG(planets: Record<string, ChartDetailPlanetData>, ascSign?: string, label = 'Rasi'): string {
  const SZ = 300, C = SZ / 4;
  const SI: Record<number,[number,number]> = {11:[0,0],0:[0,1],1:[0,2],2:[0,3],10:[1,0],3:[1,3],9:[2,0],4:[2,3],8:[3,0],7:[3,1],6:[3,2],5:[3,3]};
  const cells: Record<number, string[]> = {}; for (let i = 0; i < 12; i++) cells[i] = [];
  if (ascSign) { const idx = si(ascSign); if (idx >= 0) cells[idx].push('As'); }
  for (const [n, d] of Object.entries(planets)) { const idx = si(d.sign); if (idx >= 0) cells[idx].push(sn(n)); }
  let svg = `<svg viewBox="0 0 ${SZ} ${SZ}" width="${SZ}" height="${SZ}" xmlns="http://www.w3.org/2000/svg" style="font-family:monospace;font-size:10px">`;
  svg += `<rect x="0" y="0" width="${SZ}" height="${SZ}" fill="none" stroke="#8B7355" stroke-width="1.5"/>`;
  for (let i = 1; i < 4; i++) {
    svg += `<line x1="${i*C}" y1="0" x2="${i*C}" y2="${SZ}" stroke="#8B7355" stroke-width="1"/>`;
    svg += `<line x1="0" y1="${i*C}" x2="${SZ}" y2="${i*C}" stroke="#8B7355" stroke-width="1"/>`;
  }
  svg += `<rect x="${C}" y="${C}" width="${C*2}" height="${C*2}" fill="#faf8f0" stroke="#8B7355"/>`;
  svg += `<text x="${SZ/2}" y="${SZ/2+4}" text-anchor="middle" fill="#8B7355" font-size="14" font-weight="bold">${esc(label)}</text>`;
  for (let s = 0; s < 12; s++) {
    const pos = SI[s]; if (!pos) continue;
    const [r, c] = pos, cx = c*C+C/2, cy = r*C+C/2, names = cells[s];
    if (!names.length) continue;
    const startY = cy - ((names.length - 1) * 11) / 2;
    for (let j = 0; j < names.length; j++)
      svg += `<text x="${cx}" y="${startY+j*11}" text-anchor="middle" fill="#333">${esc(names[j])}</text>`;
  }
  return svg + '</svg>';
}

export function generateChartHTML(chart: ChartDetail, person?: ChartDetailPerson | null): string {
  const planets = (chart.chart_data?.planets || chart.planet_positions || {}) as Record<string, ChartDetailPlanetData>;
  const asc = chart.chart_data?.ascendant;
  const pg = chart.chart_data?.panchang;
  const dasha = chart.chart_data?.dasha?.current_dasha;
  const isV = chart.chart_type === 'vedic';
  const name = person?.name || 'Chart';
  const dob = person?.date_of_birth ? new Date(person.date_of_birth).toLocaleDateString('en-GB',{day:'2-digit',month:'long',year:'numeric'}) : '';
  const tob = person?.time_of_birth || '', pob = person?.place_of_birth || '';
  const svg = buildSVG(planets, asc?.sign, 'Rasi');

  // Planet table rows
  const allP = [...P_ORD.filter(p => planets[p]), ...Object.keys(planets).filter(p => !P_ORD.includes(p))];
  let pRows = '';
  for (const n of allP) {
    const p = planets[n]; if (!p) continue;
    const ret = p.is_retrograde || (p.speed != null && p.speed < 0);
    pRows += `<tr><td style="font-weight:600">${esc(n)}</td><td>${esc(p.sign||'\u2014')}</td><td style="font-family:monospace">${fmtDeg(p.sign_degree)}</td><td>${p.house||'\u2014'}</td>${isV?`<td>${esc(p.nakshatra||'\u2014')}</td><td>${p.nakshatra_pada??p.pada??'\u2014'}</td>`:''}<td>${ret?'\u211E Retro':'\u2014'}</td></tr>`;
  }

  // House rows
  let hRows = '';
  const cusps = chart.house_cusps, houses = chart.chart_data?.houses;
  const hd: number[] = [];
  if (Array.isArray(cusps)&&cusps.length>=12) for(let i=0;i<12;i++) hd.push(cusps[i]);
  else if (Array.isArray(houses)&&houses.length>=12) for(let i=0;i<12;i++) hd.push((houses as number[])[i]);
  if (hd.length >= 12) for (let i=0;i<12;i++) {
    const d=hd[i],s=SIGNS[Math.floor(d/30)%12];
    hRows += `<tr><td style="font-weight:600">${i+1}</td><td>${esc(s)}</td><td style="font-family:monospace">${fmtDeg(d%30)}</td><td>${esc(S_LORD[s]||'\u2014')}</td></tr>`;
  }

  // Panchang
  let pgH = '';
  if (isV && pg) {
    const row = (l:string,v:string) => `<tr><td style="padding:4px 8px;color:#666;width:100px">${l}</td><td style="padding:4px 8px;font-weight:600">${v}</td></tr>`;
    pgH = `<div style="margin-top:20px"><h3 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#8B7355;border-bottom:1px solid #ddd;padding-bottom:4px">Panchang</h3><table style="width:100%;border-collapse:collapse;font-size:12px;margin-top:8px">${row('Tithi',esc(sStr(pg.tithi)))}${row('Nakshatra',esc(sStr(pg.nakshatra)))}${row('Yoga',esc(sStr(pg.yoga)))}${row('Karana',esc(sStr(pg.karana)))}${pg.sunrise?row('Sunrise',esc(pg.sunrise)):''}${pg.sunset?row('Sunset',esc(pg.sunset)):''}</table></div>`;
  }

  // Dasha
  let dH = '';
  if (isV && dasha?.mahadasha) {
    const md = dasha.mahadasha, ad = dasha.antardasha;
    dH = `<div style="margin-top:20px"><h3 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#8B7355;border-bottom:1px solid #ddd;padding-bottom:4px">Current Dasha</h3><table style="border-collapse:collapse;font-size:12px;margin-top:8px"><tr><td style="padding:4px 8px;color:#666;width:120px">Maha Dasha</td><td style="padding:4px 8px;font-weight:600">${esc(md.planet)}</td></tr>${ad?`<tr><td style="padding:4px 8px;color:#666">Antar Dasha</td><td style="padding:4px 8px;font-weight:600">${esc(ad.planet)}</td></tr>`:''}${md.end_date?`<tr><td style="padding:4px 8px;color:#666">Ends</td><td style="padding:4px 8px">${new Date(md.end_date).toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric'})}</td></tr>`:''}</table></div>`;
  }

  const today = new Date().toLocaleDateString('en-GB',{day:'2-digit',month:'long',year:'numeric'});
  return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Horoscope of ${esc(name)}</title>
<style>@media print{body{margin:0;padding:16px}.no-print{display:none!important}}body{font-family:'Georgia','Times New Roman',serif;color:#222;background:#fff;max-width:800px;margin:0 auto;padding:24px;line-height:1.5}h1{font-size:20px;margin:0 0 4px;color:#333}h2{font-size:15px;color:#8B7355;margin:24px 0 8px;text-transform:uppercase;letter-spacing:1px;border-bottom:2px solid #8B7355;padding-bottom:4px}table{border-collapse:collapse;width:100%}th{text-align:left;padding:6px 10px;font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:#666;border-bottom:2px solid #ddd}td{padding:5px 10px;font-size:12px;border-bottom:1px solid #eee}.chart-grid{display:flex;gap:32px;align-items:flex-start;flex-wrap:wrap;margin:16px 0}.print-btn{position:fixed;bottom:20px;right:20px;padding:10px 20px;background:#8B7355;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600}.print-btn:hover{background:#6d5a42}</style></head><body>
<div style="text-align:center;margin-bottom:20px">
<div style="font-size:10px;color:#999;margin-bottom:4px">JOSI ASTROLOGY PLATFORM</div>
<h1>Horoscope of ${esc(name)}</h1>
${dob?`<div style="font-size:12px;color:#666;margin-bottom:2px">${esc(dob)}${tob?` at ${esc(tob)}`:''}${pob?` &mdash; ${esc(pob)}`:''}</div>`:''}
<div style="font-size:11px;color:#aaa">${esc(chart.chart_type.charAt(0).toUpperCase()+chart.chart_type.slice(1))} Chart${chart.ayanamsa?` &middot; ${esc(chart.ayanamsa)}`:''}${chart.house_system?` &middot; ${esc(chart.house_system)}`:''}</div>
</div>
<div class="chart-grid">${svg}<div style="flex:1;min-width:200px"><table>
<tr><td style="color:#666;width:100px">Sun Sign</td><td style="font-weight:600">${esc(planets['Sun']?.sign||'\u2014')}</td></tr>
<tr><td style="color:#666">Moon Sign</td><td style="font-weight:600">${esc(planets['Moon']?.sign||'\u2014')}</td></tr>
<tr><td style="color:#666">Ascendant</td><td style="font-weight:600">${esc(asc?.sign||'\u2014')}</td></tr>
${isV&&asc?.nakshatra?`<tr><td style="color:#666">Nakshatra</td><td style="font-weight:600">${esc(asc.nakshatra)}</td></tr>`:''}</table></div></div>
<h2>Planet Positions</h2><table><thead><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>House</th>${isV?'<th>Nakshatra</th><th>Pada</th>':''}<th>Retro</th></tr></thead><tbody>${pRows}</tbody></table>
${hRows?`<h2>House Cusps</h2><table><thead><tr><th>House</th><th>Sign</th><th>Degree</th><th>Lord</th></tr></thead><tbody>${hRows}</tbody></table>`:''}
${pgH}${dH}
<div style="margin-top:32px;text-align:center;font-size:10px;color:#bbb;border-top:1px solid #eee;padding-top:12px">Generated by Josi &mdash; ${today}</div>
<button class="no-print print-btn" onclick="window.print()">Print / Save PDF</button></body></html>`;
}
