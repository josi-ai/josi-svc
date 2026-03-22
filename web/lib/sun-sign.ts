// Client-side sun sign calculation — no API needed
// Based on tropical zodiac date ranges

export interface SunSignData {
  sign: string;
  symbol: string;
  element: string;
  quality: string;
  ruling: string;
  snippet: string;
}

// Ordered by calendar year: Capricorn (Dec 22) wraps to start of year
const SIGNS: { startMonth: number; startDay: number; sign: SunSignData }[] = [
  { startMonth: 1, startDay: 20, sign: { sign: 'Aquarius', symbol: '♒', element: 'Air', quality: 'Fixed', ruling: 'Uranus', snippet: 'You think in systems and futures. Independent, inventive, humanitarian — you see what could be, not just what is.' } },
  { startMonth: 2, startDay: 19, sign: { sign: 'Pisces', symbol: '♓', element: 'Water', quality: 'Mutable', ruling: 'Neptune', snippet: 'You feel the world before you see it. Intuitive, empathic, creative — boundaries dissolve and meaning flows through you.' } },
  { startMonth: 3, startDay: 21, sign: { sign: 'Aries', symbol: '♈', element: 'Fire', quality: 'Cardinal', ruling: 'Mars', snippet: 'You lead with courage and instinct. An initiator by nature — you start things that others are afraid to begin.' } },
  { startMonth: 4, startDay: 20, sign: { sign: 'Taurus', symbol: '♉', element: 'Earth', quality: 'Fixed', ruling: 'Venus', snippet: 'You build with patience and intention. Rooted in the senses — beauty, comfort, and lasting value matter deeply to you.' } },
  { startMonth: 5, startDay: 21, sign: { sign: 'Gemini', symbol: '♊', element: 'Air', quality: 'Mutable', ruling: 'Mercury', snippet: 'You think in connections and questions. A mind that never stops exploring — language and ideas are your native element.' } },
  { startMonth: 6, startDay: 21, sign: { sign: 'Cancer', symbol: '♋', element: 'Water', quality: 'Cardinal', ruling: 'Moon', snippet: 'You feel before you think. Emotional intelligence runs deep — you create safety for yourself and everyone around you.' } },
  { startMonth: 7, startDay: 23, sign: { sign: 'Leo', symbol: '♌', element: 'Fire', quality: 'Fixed', ruling: 'Sun', snippet: 'You shine without trying. Creative, warm, and generous — your presence fills a room and your heart fills a life.' } },
  { startMonth: 8, startDay: 23, sign: { sign: 'Virgo', symbol: '♍', element: 'Earth', quality: 'Mutable', ruling: 'Mercury', snippet: 'You notice what others miss. Precision and care define your approach — you improve everything you touch.' } },
  { startMonth: 9, startDay: 23, sign: { sign: 'Libra', symbol: '♎', element: 'Air', quality: 'Cardinal', ruling: 'Venus', snippet: 'You seek harmony in everything. Relationships, aesthetics, justice — balance isn\'t just a preference, it\'s your purpose.' } },
  { startMonth: 10, startDay: 23, sign: { sign: 'Scorpio', symbol: '♏', element: 'Water', quality: 'Fixed', ruling: 'Pluto', snippet: 'You transform through intensity. Nothing surface-level satisfies you — depth, truth, and emotional alchemy are your domain.' } },
  { startMonth: 11, startDay: 22, sign: { sign: 'Sagittarius', symbol: '♐', element: 'Fire', quality: 'Mutable', ruling: 'Jupiter', snippet: 'You expand through experience. Philosophy, travel, meaning — your arrow points toward something larger than yourself.' } },
  { startMonth: 12, startDay: 22, sign: { sign: 'Capricorn', symbol: '♑', element: 'Earth', quality: 'Cardinal', ruling: 'Saturn', snippet: 'You build with discipline and time. Ambition tempered by patience — you understand that lasting things are built slowly.' } },
];

export function getSunSign(month: number, day: number): SunSignData {
  // Walk backwards through the calendar-ordered list
  // Find the last sign whose start date is on or before the given date
  for (let i = SIGNS.length - 1; i >= 0; i--) {
    const s = SIGNS[i];
    if (month > s.startMonth || (month === s.startMonth && day >= s.startDay)) {
      return s.sign;
    }
  }
  // If nothing matched (date is Jan 1-19), it's Capricorn (started Dec 22)
  return SIGNS[11].sign; // Capricorn
}

export function parseDateToMonthDay(dateStr: string): { month: number; day: number } | null {
  const parts = dateStr.split(/[-/]/);
  if (parts.length < 3) return null;

  let month: number, day: number;
  if (parts[0].length === 4) {
    // YYYY-MM-DD
    month = parseInt(parts[1], 10);
    day = parseInt(parts[2], 10);
  } else {
    // MM/DD/YYYY
    month = parseInt(parts[0], 10);
    day = parseInt(parts[1], 10);
  }

  if (isNaN(month) || isNaN(day) || month < 1 || month > 12 || day < 1 || day > 31) return null;
  return { month, day };
}
