/* ─── Sky Map types and projection ─── */

export interface SkyData {
  stars: { n?: string; ra: number; dec: number; mag: number; con?: string; c?: number[] }[];
  faint: { ra: number; dec: number; mag: number; c?: number[] }[];
  lines: Record<string, string[][]>;
  illustrations: { con: string; ra: number; dec: number; size: number; file: string }[];
  center: { ra: number; dec: number };
}

export interface ViewState {
  ra: number;
  dec: number;
  _velRA: number;
  _velDec: number;
}

/* ─── Stereographic projection (centered on arbitrary RA/Dec) ─── */
export function project(
  ra: number, dec: number,
  centerRA: number, centerDec: number,
  scale: number,
  cx: number, cy: number
): { x: number; y: number } {
  const ra1 = (ra / 24) * Math.PI * 2;
  const dec1 = (dec / 180) * Math.PI;
  const ra0 = (centerRA / 24) * Math.PI * 2;
  const dec0 = (centerDec / 180) * Math.PI;

  const cosDec1 = Math.cos(dec1);
  const sinDec1 = Math.sin(dec1);
  const cosDec0 = Math.cos(dec0);
  const sinDec0 = Math.sin(dec0);
  const cosDRA = Math.cos(ra1 - ra0);
  const sinDRA = Math.sin(ra1 - ra0);

  const d = 1 + sinDec0 * sinDec1 + cosDec0 * cosDec1 * cosDRA;
  if (d < 0.01) return { x: -9999, y: -9999 };

  const x = (cosDec1 * sinDRA) / d;
  const y = (cosDec0 * sinDec1 - sinDec0 * cosDec1 * cosDRA) / d;

  return {
    x: cx - x * scale,
    y: cy - y * scale,
  };
}

/* ─── Edge-based panning logic ─── */
const EDGE_THRESHOLD = 0.75;
const AUTO_PAN_SPEED = 0.00055;

export function updatePanning(
  view: ViewState,
  mouseX: number, mouseY: number,
  w: number, h: number,
): void {
  const normX = (mouseX - w / 2) / (w / 2);
  const normY = (mouseY - h / 2) / (h / 2);
  const edgeActive = Math.abs(normX) > EDGE_THRESHOLD || Math.abs(normY) > EDGE_THRESHOLD;

  let targetDeltaRA = edgeActive ? 0 : AUTO_PAN_SPEED;
  let targetDeltaDec = 0;

  if (Math.abs(normX) > EDGE_THRESHOLD) {
    const edgeFactor = (Math.abs(normX) - EDGE_THRESHOLD) / (1 - EDGE_THRESHOLD);
    targetDeltaRA = Math.sign(normX) * edgeFactor * edgeFactor * 0.004;
  }
  if (Math.abs(normY) > EDGE_THRESHOLD) {
    const edgeFactor = (Math.abs(normY) - EDGE_THRESHOLD) / (1 - EDGE_THRESHOLD);
    targetDeltaDec = Math.sign(normY) * edgeFactor * edgeFactor * 0.02;
  }

  view.ra -= targetDeltaRA * 0.3 + view._velRA * 0.7;
  view.dec -= targetDeltaDec * 0.3 + view._velDec * 0.7;
  view._velRA = targetDeltaRA * 0.3 + (view._velRA || 0) * 0.7;
  view._velDec = targetDeltaDec * 0.3 + (view._velDec || 0) * 0.7;

  view.dec = Math.max(-70, Math.min(90, view.dec));
  if (view.ra < 0) view.ra += 24;
  if (view.ra >= 24) view.ra -= 24;
}
