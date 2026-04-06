export interface Astrologer {
  astrologer_id: string; user_id: string; professional_name: string;
  bio: string | null; years_experience: number; specializations: string[];
  languages: string[]; hourly_rate: number; currency: string; rating: number;
  total_consultations: number; total_reviews: number; verification_status_id: number;
  verification_status_name: string; is_active: boolean; is_featured: boolean;
  profile_image_url: string | null; joined_at: string;
}

export interface SearchResponse { astrologers: Astrologer[]; total: number; limit: number; offset: number; }

export const AVATAR_COLORS = [
  'bg-amber-600', 'bg-indigo-600', 'bg-emerald-600', 'bg-rose-600',
  'bg-sky-600', 'bg-violet-600', 'bg-teal-600', 'bg-orange-600',
];

export function avatarColor(name: string) {
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length];
}

export function fmtRate(cur: string, r: number) {
  return cur === 'USD' ? `$${r}` : cur === 'INR' ? `\u20B9${r.toLocaleString('en-IN')}` : `${cur} ${r}`;
}

/* Demo data */
const mk = (id: string, uid: string, name: string, bio: string, yrs: number, specs: string[], langs: string[], rate: number, cur: string, rat: number, cons: number, revs: number, feat: boolean, joined: string): Astrologer => ({
  astrologer_id: id, user_id: uid, professional_name: name, bio, years_experience: yrs,
  specializations: specs, languages: langs, hourly_rate: rate, currency: cur, rating: rat,
  total_consultations: cons, total_reviews: revs, verification_status_id: 2,
  verification_status_name: 'Verified', is_active: true, is_featured: feat,
  profile_image_url: null, joined_at: joined,
});

export const DEMO_ASTROLOGERS: Astrologer[] = [
  mk('demo-1','u1','Priya Shankar','Renowned Vedic astrologer specializing in predictive techniques and relationship compatibility analysis with a deep foundation in Parashari and Jaimini systems.',15,['Vedic','Predictive','Relationship'],['Tamil','English'],1500,'INR',4.9,2340,487,false,'2023-06-15'),
  mk('demo-2','u2','Dr. Rajesh Sharma','PhD in Jyotish Shastra with dual expertise in Vedic and Western systems. Specializes in career timing, medical astrology, and karmic pattern analysis.',22,['Career','Medical','Karmic'],['Hindi','English'],2000,'INR',4.8,3120,612,false,'2022-11-01'),
  mk('demo-3','u3','Sarah Chen','Bridging Eastern and Western traditions with expertise in Chinese BaZi, Zi Wei Dou Shu, and modern Western psychological astrology.',10,['Chinese','Western','Spiritual'],['English','Mandarin'],75,'USD',4.7,1250,298,false,'2024-01-20'),
  mk('demo-4','u4','Meenakshi Iyer','Third-generation Vedic astrologer with deep expertise in Nadi astrology and relationship counseling rooted in classical Jyotish traditions.',18,['Vedic','Relationship','Spiritual'],['Tamil','Malayalam','English'],1200,'INR',4.9,1870,401,false,'2023-03-10'),
  mk('demo-5','u5','David Williams','Classical astrologer blending Hellenistic time-lord techniques with modern Western chart interpretation for precise life-event timing.',12,['Western','Hellenistic','Predictive'],['English'],60,'USD',4.6,980,215,false,'2023-09-05'),
  mk('demo-6','u6','Lakshmi Narayanan','One of India\u2019s most respected Vedic astrologers with 25 years of practice. Known for precise karmic analysis and medical astrology consultations.',25,['Vedic','Karmic','Medical'],['Tamil','Hindi','English'],2500,'INR',5.0,5200,1038,true,'2022-05-01'),
];

export const TRADITIONS = ['Vedic', 'Western', 'Chinese', 'Hellenistic'];
export const LANGUAGES = ['English', 'Hindi', 'Tamil', 'Malayalam', 'Mandarin'];
export const RATINGS = ['4.5+', '4.0+', '3.5+'];

export const AVATAR_GRAD: Record<string, string> = {
  P: 'var(--gradient-chat)', D: 'linear-gradient(135deg,#0891B2,#22D3EE)',
  S: 'var(--gradient-voice)', M: 'linear-gradient(135deg,var(--pink),var(--pink-light))',
  L: 'var(--gradient-email)',
};

export const TAG_CLR: Record<string, [string, string]> = {
  Vedic: ['var(--gold-bg)','var(--gold-bright)'], Western: ['var(--blue-bg)','var(--blue)'],
  Chinese: ['var(--red-bg)','var(--red)'], Hellenistic: ['var(--ct-ai-bg)','var(--ic-transits)'],
  Medical: ['var(--green-bg)','var(--green)'], Karmic: ['var(--purple-bg)','var(--purple)'],
  Relationship: ['rgba(218,122,148,0.12)','var(--pink)'], Career: ['var(--blue-bg)','var(--blue)'],
  Spiritual: ['var(--green-bg)','var(--green)'], Predictive: ['var(--gold-bg)','var(--gold-bright)'],
};
