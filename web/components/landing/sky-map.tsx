'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface SkyData {
  stars: { n?: string; ra: number; dec: number; mag: number; con?: string; c?: number[] }[];
  faint: { ra: number; dec: number; mag: number; c?: number[] }[];
  lines: Record<string, string[][]>;
  illustrations: { con: string; ra: number; dec: number; size: number; file: string }[];
  center: { ra: number; dec: number };
}

/* ─── Stereographic projection (centered on arbitrary RA/Dec) ─── */
function project(
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

export default function SkyMap() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [skyData, setSkyData] = useState<SkyData | null>(null);
  const viewRef = useRef({ ra: 18.7, dec: -30, _velRA: 0, _velDec: 0 } as any); // Start at Sagittarius
  const imagesRef = useRef<Map<string, HTMLImageElement>>(new Map());
  const animRef = useRef<number>(0);
  const timeRef = useRef(0);

  // Load sky data
  useEffect(() => {
    fetch('/constellations/sky-data.json')
      .then(r => r.json())
      .then(data => {
        setSkyData(data);
        // Preload illustration images
        for (const ill of data.illustrations) {
          const img = new Image();
          img.src = `/constellations/${ill.file}`;
          imagesRef.current.set(ill.file, img);
        }
      });
  }, []);

  // Canvas rendering
  useEffect(() => {
    if (!skyData) return;
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

    const cW = () => W / devicePixelRatio;
    const cH = () => H / devicePixelRatio;

    // Mouse movement pans the sky — no click needed
    // The further the mouse is from center, the faster the sky pans
    const mousePos = { x: 0, y: 0 };
    const onMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mousePos.x = e.clientX - rect.left;
      mousePos.y = e.clientY - rect.top;
    };

    // Touch support — touch position drives panning (same as mouse)
    const onTouchStart = (e: TouchEvent) => {
      const t = e.touches[0];
      const rect = canvas.getBoundingClientRect();
      mousePos.x = t.clientX - rect.left;
      mousePos.y = t.clientY - rect.top;
    };
    const onTouchEnd = () => {
      // Reset to center so panning stops
      mousePos.x = cW() / 2;
      mousePos.y = cH() / 2;
    };
    const onTouchMove = (e: TouchEvent) => {
      e.preventDefault();
      const t = e.touches[0];
      const rect = canvas.getBoundingClientRect();
      mousePos.x = t.clientX - rect.left;
      mousePos.y = t.clientY - rect.top;
    };

    canvas.addEventListener('mousemove', onMove);
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchend', onTouchEnd);
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });

    // Star name index for constellation lines
    const starByName: Record<string, typeof skyData.stars[0]> = {};
    for (const s of skyData.stars) {
      if (s.n) starByName[s.n] = s;
    }

    /* ═══ Draw loop ═══ */
    const draw = () => {
      const w = cW();
      const h = cH();
      ctx.resetTransform();
      ctx.scale(devicePixelRatio, devicePixelRatio);

      // Black sky background
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, w, h);

      const cx = w / 2;
      const cy = h / 2;
      const scale = Math.min(w, h) * 1.2;
      timeRef.current++;
      const time = timeRef.current;

      // Edge-only panning: only the outer 25% of the screen triggers movement
      const mx = mousePos.x || w / 2;
      const my = mousePos.y || h / 2;
      const normX = (mx - w / 2) / (w / 2); // -1 to 1
      const normY = (my - h / 2) / (h / 2); // -1 to 1

      const edgeThreshold = 0.75; // only pan when cursor is in outer 25%
      // Edge panning overrides auto-pan; auto-pan is just the idle state
      const autoPanSpeed = 0.0004;
      const edgeActive = Math.abs(normX) > edgeThreshold || Math.abs(normY) > edgeThreshold;

      let targetDeltaRA = edgeActive ? 0 : autoPanSpeed;
      let targetDeltaDec = 0;

      if (Math.abs(normX) > edgeThreshold) {
        const edgeFactor = (Math.abs(normX) - edgeThreshold) / (1 - edgeThreshold);
        targetDeltaRA = Math.sign(normX) * edgeFactor * edgeFactor * 0.004;
      }
      if (Math.abs(normY) > edgeThreshold) {
        const edgeFactor = (Math.abs(normY) - edgeThreshold) / (1 - edgeThreshold);
        targetDeltaDec = Math.sign(normY) * edgeFactor * edgeFactor * 0.02;
      }

      // Smooth lerp — ease toward target speed (no jerky starts/stops)
      viewRef.current.ra -= targetDeltaRA * 0.3 + (viewRef.current as any)._velRA * 0.7;
      viewRef.current.dec -= targetDeltaDec * 0.3 + (viewRef.current as any)._velDec * 0.7;
      (viewRef.current as any)._velRA = targetDeltaRA * 0.3 + ((viewRef.current as any)._velRA || 0) * 0.7;
      (viewRef.current as any)._velDec = targetDeltaDec * 0.3 + ((viewRef.current as any)._velDec || 0) * 0.7;

      // Clamp and wrap
      viewRef.current.dec = Math.max(-70, Math.min(90, viewRef.current.dec));
      if (viewRef.current.ra < 0) viewRef.current.ra += 24;
      if (viewRef.current.ra >= 24) viewRef.current.ra -= 24;

      const viewRA = viewRef.current.ra;
      const viewDec = viewRef.current.dec;

      /* ─── Faint background stars ─── */
      for (const s of skyData.faint) {
        const p = project(s.ra, s.dec, viewRA, viewDec, scale, cx, cy);
        if (p.x < -10 || p.x > w + 10 || p.y < -10 || p.y > h + 10) continue;

        const size = Math.max(0.3, (6.5 - s.mag) * 0.35);
        const alpha = Math.max(0.08, (6.5 - s.mag) / 6.5) * 0.6;
        const twinkle = 0.7 + 0.3 * Math.sin(time * 0.015 + s.ra * 100 + s.dec * 50);

        const c = s.c || [0.88, 0.90, 0.95];
        const r = Math.round(c[0] * 255), g = Math.round(c[1] * 255), b = Math.round(c[2] * 255);
        const a = alpha * twinkle;

        // Soft halo for stars brighter than mag 5
        if (s.mag < 5) {
          const glow = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 3);
          glow.addColorStop(0, `rgba(${r},${g},${b},${a * 0.3})`);
          glow.addColorStop(1, 'transparent');
          ctx.fillStyle = glow;
          ctx.fillRect(p.x - size * 3, p.y - size * 3, size * 6, size * 6);
        }

        // Core dot
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r},${g},${b},${a})`;
        ctx.fill();
      }

      /* ─── Named stars ─── */
      for (const s of skyData.stars) {
        const p = project(s.ra, s.dec, viewRA, viewDec, scale, cx, cy);
        if (p.x < -30 || p.x > w + 30 || p.y < -30 || p.y > h + 30) continue;

        const size = Math.max(0.8, (6.5 - s.mag) * 0.8);
        const alpha = Math.min(1, (6.5 - s.mag) / 5);
        const twinkle = 0.6 + 0.4 * Math.sin(time * 0.02 + s.ra * 80);
        const isVeryBright = s.mag < 1.5;

        const c = s.c || [0.88, 0.90, 0.95];
        const r = Math.round(c[0] * 255), g = Math.round(c[1] * 255), b = Math.round(c[2] * 255);
        const a = alpha * twinkle;

        // Outer soft halo (all named stars)
        const haloSize = isVeryBright ? size * 8 : size * 4;
        const halo = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, haloSize);
        halo.addColorStop(0, `rgba(${r},${g},${b},${a * (isVeryBright ? 0.35 : 0.15)})`);
        halo.addColorStop(0.4, `rgba(${r},${g},${b},${a * (isVeryBright ? 0.12 : 0.05)})`);
        halo.addColorStop(1, 'transparent');
        ctx.fillStyle = halo;
        ctx.fillRect(p.x - haloSize, p.y - haloSize, haloSize * 2, haloSize * 2);

        // Diffraction spikes for bright stars (4-point cross)
        if (s.mag < 2.5) {
          const spikeLen = size * (isVeryBright ? 12 : 6);
          const spikeAlpha = a * (isVeryBright ? 0.25 : 0.12);
          ctx.strokeStyle = `rgba(${r},${g},${b},${spikeAlpha})`;
          ctx.lineWidth = 0.5;
          // Horizontal spike
          const hGrad = ctx.createLinearGradient(p.x - spikeLen, p.y, p.x + spikeLen, p.y);
          hGrad.addColorStop(0, 'transparent');
          hGrad.addColorStop(0.4, `rgba(${r},${g},${b},${spikeAlpha})`);
          hGrad.addColorStop(0.5, `rgba(${r},${g},${b},${spikeAlpha * 2})`);
          hGrad.addColorStop(0.6, `rgba(${r},${g},${b},${spikeAlpha})`);
          hGrad.addColorStop(1, 'transparent');
          ctx.strokeStyle = hGrad;
          ctx.beginPath(); ctx.moveTo(p.x - spikeLen, p.y); ctx.lineTo(p.x + spikeLen, p.y); ctx.stroke();
          // Vertical spike
          const vGrad = ctx.createLinearGradient(p.x, p.y - spikeLen, p.x, p.y + spikeLen);
          vGrad.addColorStop(0, 'transparent');
          vGrad.addColorStop(0.4, `rgba(${r},${g},${b},${spikeAlpha})`);
          vGrad.addColorStop(0.5, `rgba(${r},${g},${b},${spikeAlpha * 2})`);
          vGrad.addColorStop(0.6, `rgba(${r},${g},${b},${spikeAlpha})`);
          vGrad.addColorStop(1, 'transparent');
          ctx.strokeStyle = vGrad;
          ctx.beginPath(); ctx.moveTo(p.x, p.y - spikeLen); ctx.lineTo(p.x, p.y + spikeLen); ctx.stroke();
        }

        // Bright core dot (true color)
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r},${g},${b},${a})`;
        ctx.fill();
        // White-hot center for very bright stars
        if (isVeryBright) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, size * 0.4, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(255,255,255,${a * 0.6})`;
          ctx.fill();
        }

        // Star name label for bright stars
        if (s.mag < 1.5 && s.n) {
          ctx.font = '9px Inter, sans-serif';
          ctx.textAlign = 'left';
          ctx.fillStyle = `rgba(200,145,58,${alpha * 0.4})`;
          ctx.fillText(s.n, p.x + size + 4, p.y + 3);
        }
      }

      /* ─── Constellation lines ─── */
      for (const [con, lines] of Object.entries(skyData.lines)) {
        for (const pair of lines) {
          const s1 = starByName[pair[0]];
          const s2 = starByName[pair[1]];
          if (!s1 || !s2) continue;

          const p1 = project(s1.ra, s1.dec, viewRA, viewDec, scale, cx, cy);
          const p2 = project(s2.ra, s2.dec, viewRA, viewDec, scale, cx, cy);

          if (p1.x < -100 && p2.x < -100) continue;
          if (p1.x > w + 100 && p2.x > w + 100) continue;

          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = 'rgba(200,145,58,0.12)';
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }

      /* ─── Constellation illustrations ─── */
      for (const ill of skyData.illustrations) {
        const p = project(ill.ra, ill.dec, viewRA, viewDec, scale, cx, cy);
        if (p.x < -300 || p.x > w + 300 || p.y < -300 || p.y > h + 300) continue;

        const img = imagesRef.current.get(ill.file);
        if (!img || !img.complete) continue;

        const imgSize = ill.size * scale / 180; // angular size to pixels
        const halfSize = imgSize / 2;

        ctx.globalAlpha = 0.50;
        ctx.drawImage(img, p.x - halfSize, p.y - halfSize, imgSize, imgSize);
        ctx.globalAlpha = 1;
      }

      /* ─── Compass indicator ─── */
      ctx.font = '10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillStyle = 'rgba(200,145,58,0.3)';
      const raHours = Math.floor(viewRA);
      const raMin = Math.floor((viewRA - raHours) * 60);
      ctx.fillText(`RA ${raHours}h${raMin.toString().padStart(2, '0')}m  Dec ${viewDec.toFixed(0)}°`, w / 2, h - 12);

      /* ─── Drag hint ─── */
      if (time < 180) { // show for first 3 seconds
        const hintAlpha = Math.max(0, 1 - time / 180);
        ctx.font = '13px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillStyle = `rgba(200,145,58,${hintAlpha * 0.5})`;
        ctx.fillText('Move your cursor to explore the night sky', w / 2, h - 35);
      }

      animRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
      canvas.removeEventListener('mousemove', onMove);
      canvas.removeEventListener('touchstart', onTouchStart);
      canvas.removeEventListener('touchend', onTouchEnd);
      canvas.removeEventListener('touchmove', onTouchMove);
    };
  }, [skyData]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full"
      style={{ touchAction: 'none' }}
    />
  );
}
