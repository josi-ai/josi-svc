/**
 * Types and constants for the Compatibility page.
 */

export interface GunaResult {
  points: number;
  max_points: number;
  description?: string;
  [key: string]: unknown;
}

export interface ManglikStatus {
  person1: boolean;
  person2: boolean;
  manglik_match: boolean;
}

export interface CompatibilityData {
  person1: { id: string; name: string };
  person2: { id: string; name: string };
  total_score: number;
  max_score: number;
  compatibility_percentage: number;
  gunas: Record<string, GunaResult>;
  manglik_status: ManglikStatus;
  recommendations: string[];
  detailed_analysis: string;
  compatibility_level: string;
  doshas: unknown;
}

export interface GunaDetail {
  label: string;
  description: string;
  measures: string;
  lowScore: string;
  highScore: string;
}

export const GUNA_INFO: Record<string, GunaDetail> = {
  varna: {
    label: 'Varna',
    description: 'Spiritual compatibility and ego level',
    measures: 'Varna reflects the spiritual and intellectual compatibility between partners. It classifies individuals into four categories (Brahmin, Kshatriya, Vaishya, Shudra) based on their Moon sign, representing their innate spiritual development and ego alignment.',
    lowScore: 'A low Varna score suggests differing spiritual wavelengths. Partners may struggle to understand each other\'s core values, life priorities, and approach to personal growth. Mutual respect and conscious effort to appreciate different perspectives are key.',
    highScore: 'A high Varna score indicates natural alignment in spiritual outlook and ego compatibility. Partners share similar values around duty, purpose, and self-development, creating an effortless understanding at the deepest level.',
  },
  vashya: {
    label: 'Vashya',
    description: 'Mutual attraction and dominance',
    measures: 'Vashya evaluates the power dynamics and mutual magnetic attraction between partners. It measures who holds influence in the relationship and whether the dominance balance is harmonious, assessing natural affinity and willingness to accommodate each other.',
    lowScore: 'A low Vashya score can indicate power struggles or a lack of natural attraction. One partner may feel dominated or unheard. Conscious balance of give-and-take is essential to maintain harmony.',
    highScore: 'A high Vashya score shows strong mutual attraction and a healthy balance of influence. Both partners naturally gravitate toward each other and willingly accommodate, creating a relationship of equals.',
  },
  tara: {
    label: 'Tara',
    description: 'Birth star compatibility and destiny',
    measures: 'Tara (Dina) compatibility examines the destiny alignment between two birth stars (nakshatras). It calculates the wellness and health implications of the pairing, revealing whether the cosmic rhythms of both individuals are in sync.',
    lowScore: 'A low Tara score warns of potential health concerns or a sense of fatigue in the relationship. The partners\' cosmic rhythms may clash, leading to periodic friction or a general feeling of unease together.',
    highScore: 'A high Tara score indicates excellent destiny alignment. Partners feel energized and uplifted in each other\'s presence. Their birth stars create a harmonious cosmic rhythm that supports mutual well-being.',
  },
  yoni: {
    label: 'Yoni',
    description: 'Physical and sexual compatibility',
    measures: 'Yoni kuta assesses physical and sexual compatibility by mapping each nakshatra to an animal nature (14 animal types). It evaluates the instinctive physical connection, intimacy potential, and sexual harmony between partners.',
    lowScore: 'A low Yoni score suggests potential mismatches in physical needs and intimacy styles. Partners may have different expectations around closeness, affection, and sexual expression. Open communication about needs is important.',
    highScore: 'A high Yoni score indicates excellent physical chemistry and natural intimacy. Partners share compatible instinctive drives, leading to a deeply satisfying physical connection and mutual comfort.',
  },
  graha_maitri: {
    label: 'Graha Maitri',
    description: 'Mental wavelength and friendship',
    measures: 'Graha Maitri (planetary friendship) measures the mental and intellectual compatibility between partners. It compares the lords of each person\'s Moon sign to determine if their thought patterns, communication styles, and decision-making approaches align.',
    lowScore: 'A low Graha Maitri score indicates different mental wavelengths. Partners may frequently misunderstand each other, disagree on decisions, or feel intellectually disconnected. Patience and active listening become crucial.',
    highScore: 'A high Graha Maitri score shows excellent mental rapport. Partners think alike, communicate effortlessly, and share similar approaches to problem-solving. This creates a strong friendship foundation for the marriage.',
  },
  gana: {
    label: 'Gana',
    description: 'Temperament and nature match',
    measures: 'Gana kuta classifies temperaments into three types: Deva (divine/gentle), Manushya (human/balanced), and Rakshasa (demonic/intense). It evaluates whether the fundamental natures and behavioral tendencies of two people can coexist harmoniously.',
    lowScore: 'A low Gana score suggests clashing temperaments. One partner may find the other too aggressive or too passive. A Deva-Rakshasa pairing, for instance, may experience frequent conflicts over lifestyle and social behavior.',
    highScore: 'A high Gana score indicates matching temperaments. Partners share similar social dispositions and behavioral patterns, reducing friction in daily interactions and creating a natural comfort zone.',
  },
  bhakoot: {
    label: 'Bhakoot',
    description: 'Love, emotional bond and health',
    measures: 'Bhakoot (Rashyadhipati) is one of the most important gunas, carrying 7 points. It examines the Moon sign positions of both partners to evaluate emotional compatibility, mutual love potential, financial prosperity, and the overall health of the relationship.',
    lowScore: 'A low Bhakoot score is a significant concern. It can indicate emotional distance, financial strain, or health issues in the marriage. Certain sign combinations (like 6-8 or 2-12 positions) are considered particularly challenging and may require remedial measures.',
    highScore: 'A high Bhakoot score is very auspicious. It indicates deep emotional bonding, financial harmony, and mutual love that grows over time. Partners naturally support each other\'s emotional and material well-being.',
  },
  nadi: {
    label: 'Nadi',
    description: 'Genetic compatibility and health',
    measures: 'Nadi is the most critical guna, carrying the maximum 8 points. It classifies individuals into Aadi (Vata), Madhya (Pitta), or Antya (Kapha) based on their nakshatra. It assesses genetic compatibility and the health prospects of offspring, making it the single most weighted factor in Ashtakoota matching.',
    lowScore: 'A zero Nadi score (Nadi Dosha) is the most serious defect in guna matching. It warns of potential health issues for offspring and fundamental physiological incompatibility. Traditional astrology considers this a significant obstacle, though specific nakshatra exceptions (Nadi Dosha cancellation) may apply.',
    highScore: 'A full 8-point Nadi score indicates excellent genetic compatibility. Partners belong to different Nadi types, ensuring complementary physiological constitutions and healthy prospects for the next generation.',
  },
};
