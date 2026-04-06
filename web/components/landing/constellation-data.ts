/* ─── Constellation data with SVG illustration paths ─── */

export interface ConstellationStar {
  x: number;
  y: number;
  b: number;
}

export interface ConstellationDef {
  name: string;
  stars: ConstellationStar[];
  lines: [number, number][];
  illustration: string[];
}

export const CONSTELLATIONS: ConstellationDef[] = [
  {
    name: 'Orion',
    stars: [
      { x: 0.38, y: 0.22, b: 0.9 },  // Betelgeuse (left shoulder)
      { x: 0.44, y: 0.22, b: 0.7 },   // Bellatrix (right shoulder)
      { x: 0.39, y: 0.32, b: 0.8 },   // Alnitak (belt left)
      { x: 0.41, y: 0.31, b: 0.9 },   // Alnilam (belt center)
      { x: 0.43, y: 0.30, b: 0.8 },   // Mintaka (belt right)
      { x: 0.37, y: 0.42, b: 0.6 },   // Saiph (left foot)
      { x: 0.45, y: 0.40, b: 0.9 },   // Rigel (right foot)
    ],
    lines: [[0,1],[0,2],[1,4],[2,3],[3,4],[2,5],[4,6]],
    // Simplified hunter figure
    illustration: [
      'M 0.41 0.16 A 0.02 0.02 0 1 1 0.41 0.15 A 0.02 0.02 0 1 1 0.41 0.16',
      'M 0.41 0.18 L 0.41 0.20 L 0.38 0.22 M 0.41 0.20 L 0.44 0.22',
      'M 0.41 0.20 L 0.41 0.32',
      'M 0.38 0.22 L 0.35 0.17 L 0.34 0.13',
      'M 0.44 0.22 L 0.47 0.19 L 0.48 0.22 L 0.47 0.26 L 0.44 0.28',
      'M 0.41 0.32 L 0.37 0.42',
      'M 0.41 0.32 L 0.45 0.40',
    ],
  },
  {
    name: 'Scorpius',
    stars: [
      { x: 0.78, y: 0.15, b: 0.6 },
      { x: 0.80, y: 0.22, b: 1.0 },   // Antares
      { x: 0.82, y: 0.30, b: 0.5 },
      { x: 0.85, y: 0.36, b: 0.5 },
      { x: 0.88, y: 0.40, b: 0.6 },
      { x: 0.90, y: 0.44, b: 0.5 },
      { x: 0.89, y: 0.48, b: 0.7 },
    ],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]],
    illustration: [
      'M 0.78 0.15 L 0.75 0.12 L 0.73 0.10 M 0.75 0.12 L 0.73 0.14',
      'M 0.78 0.15 L 0.77 0.11 L 0.79 0.09 M 0.77 0.11 L 0.75 0.10',
      'M 0.78 0.15 Q 0.79 0.18 0.80 0.22 Q 0.81 0.26 0.82 0.30 Q 0.84 0.33 0.85 0.36 Q 0.87 0.38 0.88 0.40 Q 0.89 0.42 0.90 0.44',
      'M 0.90 0.44 Q 0.91 0.46 0.89 0.48 L 0.88 0.50 L 0.87 0.49',
      'M 0.80 0.22 L 0.77 0.25 M 0.80 0.22 L 0.83 0.25',
      'M 0.82 0.30 L 0.79 0.33 M 0.82 0.30 L 0.85 0.33',
      'M 0.85 0.36 L 0.82 0.39 M 0.85 0.36 L 0.88 0.37',
    ],
  },
  {
    name: 'Ursa Major',
    stars: [
      { x: 0.12, y: 0.10, b: 0.8 },
      { x: 0.17, y: 0.08, b: 0.7 },
      { x: 0.22, y: 0.11, b: 0.75 },
      { x: 0.25, y: 0.16, b: 0.7 },
      { x: 0.30, y: 0.15, b: 0.65 },
      { x: 0.33, y: 0.12, b: 0.7 },
      { x: 0.36, y: 0.14, b: 0.6 },
    ],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]],
    illustration: [
      'M 0.10 0.10 Q 0.09 0.08 0.11 0.07 Q 0.13 0.06 0.14 0.08 L 0.12 0.10',
      'M 0.10 0.07 L 0.09 0.05 L 0.10 0.06',
      'M 0.12 0.10 Q 0.15 0.09 0.17 0.08 Q 0.20 0.09 0.22 0.11 Q 0.24 0.13 0.25 0.16 Q 0.28 0.16 0.30 0.15',
      'M 0.30 0.15 Q 0.32 0.13 0.33 0.12 Q 0.35 0.13 0.36 0.14',
      'M 0.12 0.10 Q 0.14 0.14 0.18 0.15 Q 0.22 0.16 0.25 0.16',
      'M 0.14 0.14 L 0.13 0.18 M 0.18 0.15 L 0.17 0.19',
      'M 0.28 0.16 L 0.27 0.20 M 0.32 0.15 L 0.31 0.19',
    ],
  },
  {
    name: 'Leo',
    stars: [
      { x: 0.55, y: 0.60, b: 0.9 },   // Regulus
      { x: 0.52, y: 0.54, b: 0.6 },
      { x: 0.56, y: 0.50, b: 0.65 },
      { x: 0.60, y: 0.53, b: 0.7 },
      { x: 0.63, y: 0.58, b: 0.6 },
      { x: 0.61, y: 0.64, b: 0.55 },
    ],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,0]],
    illustration: [
      'M 0.50 0.52 Q 0.49 0.50 0.50 0.48 Q 0.52 0.46 0.54 0.47 Q 0.56 0.48 0.55 0.50 Q 0.54 0.52 0.52 0.54',
      'M 0.51 0.49 L 0.50 0.48 M 0.53 0.49 L 0.54 0.48',
      'M 0.54 0.52 Q 0.57 0.53 0.60 0.53 Q 0.62 0.54 0.63 0.56',
      'M 0.55 0.55 L 0.54 0.62 L 0.55 0.63 M 0.57 0.55 L 0.56 0.62 L 0.57 0.63',
      'M 0.62 0.56 L 0.61 0.64 L 0.62 0.65 M 0.64 0.57 L 0.63 0.64 L 0.64 0.65',
      'M 0.63 0.53 Q 0.66 0.50 0.68 0.48 Q 0.69 0.47 0.68 0.49',
    ],
  },
];

/* ─── Parse SVG path to canvas commands ─── */
export function drawSvgPath(ctx: CanvasRenderingContext2D, path: string, w: number, h: number, scrollOffset: number) {
  const tokens = path.match(/[MLQAHZ]|[-+]?\d*\.?\d+/gi) || [];
  let i = 0;
  const n = () => parseFloat(tokens[i++]);

  ctx.beginPath();
  while (i < tokens.length) {
    const cmd = tokens[i++];
    switch (cmd) {
      case 'M': ctx.moveTo(n() * w, n() * h - scrollOffset); break;
      case 'L': ctx.lineTo(n() * w, n() * h - scrollOffset); break;
      case 'Q': { const cx = n() * w, cy = n() * h - scrollOffset, ex = n() * w, ey = n() * h - scrollOffset; ctx.quadraticCurveTo(cx, cy, ex, ey); break; }
      case 'A': {
        const rx = n(), ry = n(); n(); n(); n(); // skip rotation, large-arc, sweep
        const ax = n() * w, ay = n() * h - scrollOffset;
        ctx.arc(ax, ay, rx * w, 0, Math.PI * 2);
        break;
      }
      case 'Z': ctx.closePath(); break;
      default: i--; i++; break;
    }
  }
}
