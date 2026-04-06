'use client';

import { useEffect, useRef } from 'react';
import { CONSTELLATIONS, drawSvgPath } from './constellation-data';
import {
  type CosmicConfig, PRESETS, srand,
  type Star, type AuroraOrb, type Particle,
  AURORA_ORBS, initStars, initParticles,
} from './cosmic-config';

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

    /* ═══ Initialize scene objects ═══ */
    const stars = initStars(500);
    const orbs = AURORA_ORBS;
    const particles = initParticles(50);

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
