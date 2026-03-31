'use client';

import { useEffect, useRef } from 'react';

interface CosmicConfig {
  aurora: boolean;
  stars: boolean;
  constellations: boolean;
  particles: boolean;
}

const PRESETS: Record<string, CosmicConfig> = {
  aurora: { aurora: true, stars: false, constellations: false, particles: false },
  starfield: { aurora: false, stars: true, constellations: false, particles: false },
  constellation: { aurora: false, stars: true, constellations: true, particles: false },
  cosmic: { aurora: true, stars: true, constellations: true, particles: true },
};

/* ─── Seeded PRNG ─── */
function srand(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

/* ─── Constellation data with SVG illustration paths ─── */
const CONSTELLATIONS = [
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
    lines: [[0,1],[0,2],[1,4],[2,3],[3,4],[2,5],[4,6]] as [number,number][],
    // Simplified hunter figure — head, torso, arms, shield, legs (normalized to constellation bounds)
    illustration: [
      // Head (circle indicated by arc path)
      'M 0.41 0.16 A 0.02 0.02 0 1 1 0.41 0.15 A 0.02 0.02 0 1 1 0.41 0.16',
      // Neck to shoulders
      'M 0.41 0.18 L 0.41 0.20 L 0.38 0.22 M 0.41 0.20 L 0.44 0.22',
      // Torso
      'M 0.41 0.20 L 0.41 0.32',
      // Left arm raised (holding club)
      'M 0.38 0.22 L 0.35 0.17 L 0.34 0.13',
      // Right arm (holding shield)
      'M 0.44 0.22 L 0.47 0.19 L 0.48 0.22 L 0.47 0.26 L 0.44 0.28',
      // Left leg
      'M 0.41 0.32 L 0.37 0.42',
      // Right leg
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
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]] as [number,number][],
    // Scorpion body — claws, body segments, curved tail with stinger
    illustration: [
      // Left claw
      'M 0.78 0.15 L 0.75 0.12 L 0.73 0.10 M 0.75 0.12 L 0.73 0.14',
      // Right claw
      'M 0.78 0.15 L 0.77 0.11 L 0.79 0.09 M 0.77 0.11 L 0.75 0.10',
      // Body curve
      'M 0.78 0.15 Q 0.79 0.18 0.80 0.22 Q 0.81 0.26 0.82 0.30 Q 0.84 0.33 0.85 0.36 Q 0.87 0.38 0.88 0.40 Q 0.89 0.42 0.90 0.44',
      // Tail curl with stinger
      'M 0.90 0.44 Q 0.91 0.46 0.89 0.48 L 0.88 0.50 L 0.87 0.49',
      // Legs (3 pairs)
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
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]] as [number,number][],
    // Bear figure — head, body, legs, tail
    illustration: [
      // Head
      'M 0.10 0.10 Q 0.09 0.08 0.11 0.07 Q 0.13 0.06 0.14 0.08 L 0.12 0.10',
      // Ear
      'M 0.10 0.07 L 0.09 0.05 L 0.10 0.06',
      // Body outline
      'M 0.12 0.10 Q 0.15 0.09 0.17 0.08 Q 0.20 0.09 0.22 0.11 Q 0.24 0.13 0.25 0.16 Q 0.28 0.16 0.30 0.15',
      // Back/tail
      'M 0.30 0.15 Q 0.32 0.13 0.33 0.12 Q 0.35 0.13 0.36 0.14',
      // Belly
      'M 0.12 0.10 Q 0.14 0.14 0.18 0.15 Q 0.22 0.16 0.25 0.16',
      // Front legs
      'M 0.14 0.14 L 0.13 0.18 M 0.18 0.15 L 0.17 0.19',
      // Back legs
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
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,0]] as [number,number][],
    // Lion figure — mane, body, legs, tail
    illustration: [
      // Mane (rough circle around head area)
      'M 0.50 0.52 Q 0.49 0.50 0.50 0.48 Q 0.52 0.46 0.54 0.47 Q 0.56 0.48 0.55 0.50 Q 0.54 0.52 0.52 0.54',
      // Head features
      'M 0.51 0.49 L 0.50 0.48 M 0.53 0.49 L 0.54 0.48',
      // Body
      'M 0.54 0.52 Q 0.57 0.53 0.60 0.53 Q 0.62 0.54 0.63 0.56',
      // Front legs
      'M 0.55 0.55 L 0.54 0.62 L 0.55 0.63 M 0.57 0.55 L 0.56 0.62 L 0.57 0.63',
      // Back legs
      'M 0.62 0.56 L 0.61 0.64 L 0.62 0.65 M 0.64 0.57 L 0.63 0.64 L 0.64 0.65',
      // Tail
      'M 0.63 0.53 Q 0.66 0.50 0.68 0.48 Q 0.69 0.47 0.68 0.49',
    ],
  },
];

/* ─── Types ─── */
interface Star { x: number; y: number; size: number; brightness: number; twinkleSpeed: number; twinkleOffset: number; isGold: boolean; }
interface AuroraOrb { x: number; y: number; radius: number; r: number; g: number; b: number; alpha: number; driftX: number; driftY: number; speed: number; phase: number; }
interface Particle { x: number; y: number; vx: number; vy: number; size: number; baseAlpha: number; alpha: number; isGold: boolean; depth: number; }

/* ─── Parse SVG path to canvas commands ─── */
function drawSvgPath(ctx: CanvasRenderingContext2D, path: string, w: number, h: number, scrollOffset: number) {
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
        // Simplified arc handling for head circles
        const rx = n(), ry = n(); n(); n(); n(); // skip rotation, large-arc, sweep
        const ax = n() * w, ay = n() * h - scrollOffset;
        ctx.arc(ax, ay, rx * w, 0, Math.PI * 2);
        break;
      }
      case 'Z': ctx.closePath(); break;
      default: i--; i++; break; // skip unknowns
    }
  }
}

export default function CosmicCanvas({ preset = 'cosmic' }: { preset?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const configRef = useRef<CosmicConfig>(PRESETS[preset] || PRESETS.cosmic);
  const mouseRef = useRef({ x: -1000, y: -1000 });

  useEffect(() => {
    configRef.current = PRESETS[preset] || PRESETS.cosmic;
  }, [preset]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let W = 0, H = 0;
    const resize = () => {
      W = canvas.offsetWidth * devicePixelRatio;
      H = canvas.offsetHeight * devicePixelRatio;
      canvas.width = W;
      canvas.height = H;
    };
    resize();
    window.addEventListener('resize', resize);

    const onMouse = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };
    window.addEventListener('mousemove', onMouse);

    let scrollY = 0;
    const onScroll = () => { scrollY = window.scrollY; };
    window.addEventListener('scroll', onScroll, { passive: true });

    const cW = () => W / devicePixelRatio;
    const cH = () => H / devicePixelRatio;

    /* ═══ Initialize Stars — FIXED POSITIONS, twinkle only ═══ */
    const stars: Star[] = [];
    for (let i = 0; i < 500; i++) {
      stars.push({
        x: srand(i + 1000),  // 0-1 normalized
        y: srand(i + 2000),
        size: 0.4 + srand(i + 3000) * 2.5,
        brightness: 0.2 + srand(i + 4000) * 0.8,
        twinkleSpeed: 0.3 + srand(i + 5000) * 2.5,
        twinkleOffset: srand(i + 6000) * Math.PI * 2,
        isGold: srand(i + 7000) < 0.18,
      });
    }

    /* ═══ Aurora Orbs ═══ */
    const orbs: AuroraOrb[] = [
      { x: 0.4, y: 0.3, radius: 0.4, r: 200, g: 145, b: 58, alpha: 0.18, driftX: 50, driftY: -30, speed: 0.0004, phase: 0 },
      { x: 0.15, y: 0.5, radius: 0.35, r: 20, g: 50, b: 140, alpha: 0.14, driftX: -40, driftY: 35, speed: 0.00033, phase: 1 },
      { x: 0.75, y: 0.35, radius: 0.3, r: 90, g: 40, b: 150, alpha: 0.11, driftX: 30, driftY: 30, speed: 0.00045, phase: 2 },
      { x: 0.25, y: 0.75, radius: 0.3, r: 20, g: 130, b: 110, alpha: 0.10, driftX: -25, driftY: -25, speed: 0.00052, phase: 3 },
      { x: 0.7, y: 0.7, radius: 0.28, r: 210, g: 160, b: 50, alpha: 0.14, driftX: 35, driftY: 25, speed: 0.00036, phase: 4 },
      { x: 0.5, y: 0.8, radius: 0.4, r: 30, g: 20, b: 100, alpha: 0.12, driftX: -20, driftY: -35, speed: 0.00042, phase: 5 },
    ];

    /* ═══ Particles ═══ */
    const particles: Particle[] = [];
    for (let i = 0; i < 50; i++) {
      const depth = srand(i + 8000);
      particles.push({
        x: srand(i + 9000) * 1440,
        y: srand(i + 10000) * 900,
        vx: (srand(i + 11000) - 0.5) * 0.3,
        vy: (srand(i + 12000) - 0.5) * 0.2,
        size: 1 + depth * 3,
        baseAlpha: 0.1 + depth * 0.5,
        alpha: 0.1 + depth * 0.5,
        isGold: srand(i + 13000) < 0.35,
        depth,
      });
    }

    /* ═══ Constellation timing ═══ */
    const constellationStartTime = performance.now();

    /* ═══ Animation Loop ═══ */
    let frame: number;
    let time = 0;

    const draw = () => {
      const w = cW();
      const h = cH();
      ctx.resetTransform();
      ctx.scale(devicePixelRatio, devicePixelRatio);
      ctx.clearRect(0, 0, w, h);

      const cfg = configRef.current;
      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;
      time++;

      /* ─── AURORA ─── */
      if (cfg.aurora) {
        const t = performance.now();
        for (const orb of orbs) {
          const ox = (orb.x + Math.sin(t * orb.speed + orb.phase) * orb.driftX / w) * w;
          const oy = (orb.y + Math.cos(t * orb.speed * 0.7 + orb.phase) * orb.driftY / h) * h;
          const r = orb.radius * Math.max(w, h);
          const grad = ctx.createRadialGradient(ox, oy, 0, ox, oy, r);
          grad.addColorStop(0, `rgba(${orb.r},${orb.g},${orb.b},${orb.alpha})`);
          grad.addColorStop(0.5, `rgba(${orb.r},${orb.g},${orb.b},${orb.alpha * 0.3})`);
          grad.addColorStop(1, 'transparent');
          ctx.fillStyle = grad;
          ctx.fillRect(0, 0, w, h);
        }
      }

      /* ─── STARS — twinkle in place, mouse parallax only ─── */
      if (cfg.stars) {
        const parallaxX = (mx - w / 2) / w;
        const parallaxY = (my - h / 2) / h;

        for (const star of stars) {
          // Mouse parallax only (no drift)
          const px = star.size > 1.5 ? 25 : star.size > 0.8 ? 12 : 4;
          const sx = star.x * w + parallaxX * px;
          const sy = star.y * h + parallaxY * px;

          // Twinkle
          const twinkle = 0.5 + 0.5 * Math.sin(time * 0.02 * star.twinkleSpeed + star.twinkleOffset);
          const alpha = star.brightness * (0.5 + twinkle * 0.5);

          if (star.isGold) {
            // Gold glow halo
            const glow = ctx.createRadialGradient(sx, sy, 0, sx, sy, star.size * 5);
            glow.addColorStop(0, `rgba(200,145,58,${alpha * 0.5})`);
            glow.addColorStop(1, 'transparent');
            ctx.fillStyle = glow;
            ctx.fillRect(sx - star.size * 5, sy - star.size * 5, star.size * 10, star.size * 10);

            ctx.beginPath();
            ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(220,170,70,${alpha})`;
            ctx.fill();
          } else {
            ctx.beginPath();
            ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(200,210,230,${alpha * 0.8})`;
            ctx.fill();
          }
        }
      }

      /* ─── CONSTELLATIONS — draw lines, then fade in illustration ─── */
      if (cfg.constellations) {
        const elapsed = (performance.now() - constellationStartTime) / 1000;
        const cScrollOffset = scrollY * 0.12;

        CONSTELLATIONS.forEach((c, ci) => {
          const startDelay = ci * 2.5;
          const linePhase = Math.min(1, Math.max(0, (elapsed - startDelay) / 3));
          // Illustration fades in AFTER lines finish drawing
          const illustrationPhase = Math.min(1, Math.max(0, (elapsed - startDelay - 3) / 2));

          if (linePhase <= 0) return;

          // Compute center for label
          let centerX = 0, centerY = 0;
          for (const star of c.stars) { centerX += star.x; centerY += star.y; }
          centerX = (centerX / c.stars.length) * w;
          centerY = (centerY / c.stars.length) * h - cScrollOffset;

          const totalLines = c.lines.length;
          const linesComplete = linePhase * totalLines;

          // Draw constellation lines
          for (let li = 0; li < totalLines; li++) {
            const lp = Math.min(1, Math.max(0, linesComplete - li));
            if (lp <= 0) continue;

            const [si, ei] = c.lines[li];
            const s = c.stars[si], e = c.stars[ei];
            const sx = s.x * w, sy = s.y * h - cScrollOffset;
            const ex = e.x * w, ey = e.y * h - cScrollOffset;

            if (sy > h + 50 && ey > h + 50) continue;
            if (sy < -50 && ey < -50) continue;

            const cx = sx + (ex - sx) * lp;
            const cy = sy + (ey - sy) * lp;

            // Line
            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.lineTo(cx, cy);
            ctx.strokeStyle = 'rgba(200,145,58,0.15)';
            ctx.lineWidth = 0.8;
            ctx.stroke();

            // Spark head
            if (lp < 1) {
              const spark = ctx.createRadialGradient(cx, cy, 0, cx, cy, 8);
              spark.addColorStop(0, 'rgba(220,170,60,0.9)');
              spark.addColorStop(1, 'transparent');
              ctx.fillStyle = spark;
              ctx.fillRect(cx - 8, cy - 8, 16, 16);
            }
          }

          // Draw constellation star dots
          for (const star of c.stars) {
            const sx = star.x * w, sy = star.y * h - cScrollOffset;
            if (sy > h + 20 || sy < -20) continue;
            const starAlpha = Math.min(1, linePhase * 2);
            const starSize = 1 + star.b * 2;

            const glow = ctx.createRadialGradient(sx, sy, 0, sx, sy, starSize * 4);
            glow.addColorStop(0, `rgba(200,145,58,${starAlpha * star.b * 0.4})`);
            glow.addColorStop(1, 'transparent');
            ctx.fillStyle = glow;
            ctx.fillRect(sx - starSize * 4, sy - starSize * 4, starSize * 8, starSize * 8);

            ctx.beginPath();
            ctx.arc(sx, sy, starSize, 0, Math.PI * 2);
            ctx.fillStyle = star.b > 0.7 ? `rgba(220,180,80,${starAlpha})` : `rgba(200,210,230,${starAlpha * 0.9})`;
            ctx.fill();
          }

          // Draw mythological illustration (fades in after lines complete)
          if (illustrationPhase > 0 && c.illustration) {
            const illAlpha = illustrationPhase * 0.2; // very subtle
            ctx.strokeStyle = `rgba(200,145,58,${illAlpha})`;
            ctx.lineWidth = 0.6;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';

            for (const path of c.illustration) {
              drawSvgPath(ctx, path, w, h, cScrollOffset);
              ctx.stroke();
            }
          }

          // Constellation name label
          if (linePhase > 0.8 && centerY > -50 && centerY < h + 50) {
            const labelAlpha = Math.min(0.25, (linePhase - 0.8) * 1.25);
            ctx.textAlign = 'center';
            ctx.font = '600 9px Inter, sans-serif';
            ctx.fillStyle = `rgba(200,145,58,${labelAlpha})`;
            ctx.fillText(c.name.toUpperCase(), centerX, centerY - 15);
          }
        });
      }

      /* ─── PARTICLES — gentle wander, mouse repulsion ─── */
      if (cfg.particles) {
        for (const p of particles) {
          const dx = p.x - mx, dy = p.y - my;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150 && dist > 0) {
            const force = (1 - dist / 150) * 6;
            p.vx += (dx / dist) * force * 0.08;
            p.vy += (dy / dist) * force * 0.08;
            p.alpha = Math.min(p.baseAlpha * 2.5, 1);
          } else {
            p.alpha += (p.baseAlpha - p.alpha) * 0.03;
          }

          p.x += p.vx;
          p.y += p.vy;
          p.vx *= 0.985;
          p.vy *= 0.985;
          // Gentle random wander (no directional drift)
          p.vx += (srand(time + p.x) - 0.5) * 0.02;
          p.vy += (srand(time + p.y) - 0.5) * 0.02;

          // Wrap
          if (p.x < -20) p.x = w + 20;
          if (p.x > w + 20) p.x = -20;
          if (p.y < -20) p.y = h + 20;
          if (p.y > h + 20) p.y = -20;

          // Glow
          if (p.size > 1.5) {
            const glow = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 4);
            glow.addColorStop(0, p.isGold ? `rgba(200,145,58,${p.alpha * 0.4})` : `rgba(200,210,230,${p.alpha * 0.2})`);
            glow.addColorStop(1, 'transparent');
            ctx.fillStyle = glow;
            ctx.fillRect(p.x - p.size * 4, p.y - p.size * 4, p.size * 8, p.size * 8);
          }

          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fillStyle = p.isGold ? `rgba(220,170,60,${p.alpha})` : `rgba(200,210,230,${p.alpha * 0.7})`;
          ctx.fill();
        }
      }

      frame = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', onMouse);
      window.removeEventListener('scroll', onScroll);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full"
      style={{ pointerEvents: 'none' }}
    />
  );
}
