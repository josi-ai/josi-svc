/* ─── Cosmic Canvas configuration and initialization data ─── */

export interface CosmicConfig {
  aurora: boolean;
  stars: boolean;
  constellations: boolean;
  particles: boolean;
}

export const PRESETS: Record<string, CosmicConfig> = {
  aurora: { aurora: true, stars: false, constellations: false, particles: false },
  starfield: { aurora: false, stars: true, constellations: false, particles: false },
  constellation: { aurora: false, stars: true, constellations: true, particles: false },
  cosmic: { aurora: true, stars: true, constellations: true, particles: true },
};

/* ─── Seeded PRNG ─── */
export function srand(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

/* ─── Types ─── */
export interface Star { x: number; y: number; size: number; brightness: number; twinkleSpeed: number; twinkleOffset: number; isGold: boolean; }
export interface AuroraOrb { x: number; y: number; radius: number; r: number; g: number; b: number; alpha: number; driftX: number; driftY: number; speed: number; phase: number; }
export interface Particle { x: number; y: number; vx: number; vy: number; size: number; baseAlpha: number; alpha: number; isGold: boolean; depth: number; }

/* ─── Aurora Orbs initialization ─── */
export const AURORA_ORBS: AuroraOrb[] = [
  { x: 0.4, y: 0.3, radius: 0.4, r: 200, g: 145, b: 58, alpha: 0.18, driftX: 50, driftY: -30, speed: 0.0004, phase: 0 },
  { x: 0.15, y: 0.5, radius: 0.35, r: 20, g: 50, b: 140, alpha: 0.14, driftX: -40, driftY: 35, speed: 0.00033, phase: 1 },
  { x: 0.75, y: 0.35, radius: 0.3, r: 90, g: 40, b: 150, alpha: 0.11, driftX: 30, driftY: 30, speed: 0.00045, phase: 2 },
  { x: 0.25, y: 0.75, radius: 0.3, r: 20, g: 130, b: 110, alpha: 0.10, driftX: -25, driftY: -25, speed: 0.00052, phase: 3 },
  { x: 0.7, y: 0.7, radius: 0.28, r: 210, g: 160, b: 50, alpha: 0.14, driftX: 35, driftY: 25, speed: 0.00036, phase: 4 },
  { x: 0.5, y: 0.8, radius: 0.4, r: 30, g: 20, b: 100, alpha: 0.12, driftX: -20, driftY: -35, speed: 0.00042, phase: 5 },
];

/* ─── Star field initializer ─── */
export function initStars(count: number): Star[] {
  const stars: Star[] = [];
  for (let i = 0; i < count; i++) {
    stars.push({
      x: srand(i + 1000), y: srand(i + 2000),
      size: 0.4 + srand(i + 3000) * 2.5,
      brightness: 0.2 + srand(i + 4000) * 0.8,
      twinkleSpeed: 0.3 + srand(i + 5000) * 2.5,
      twinkleOffset: srand(i + 6000) * Math.PI * 2,
      isGold: srand(i + 7000) < 0.18,
    });
  }
  return stars;
}

/* ─── Particle initializer ─── */
export function initParticles(count: number): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < count; i++) {
    const depth = srand(i + 8000);
    particles.push({
      x: srand(i + 9000) * 1440, y: srand(i + 10000) * 900,
      vx: (srand(i + 11000) - 0.5) * 0.3, vy: (srand(i + 12000) - 0.5) * 0.2,
      size: 1 + depth * 3, baseAlpha: 0.1 + depth * 0.5, alpha: 0.1 + depth * 0.5,
      isGold: srand(i + 13000) < 0.35, depth,
    });
  }
  return particles;
}
