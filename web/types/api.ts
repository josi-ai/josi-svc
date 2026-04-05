/**
 * Centralized API response types for the Josi web frontend.
 *
 * These types mirror the backend Pydantic/SQLModel response schemas so the
 * frontend has a single source of truth.  When the backend changes a response
 * shape, update this file and TypeScript will surface every callsite that needs
 * attention.
 *
 * ─── Files with inline type definitions that should be migrated ────────────
 * web/hooks/use-default-profile.ts                  — Person
 * web/hooks/use-widget-layout.ts                    — UserPreferences
 * web/contexts/AuthContext.tsx                       — UserProfile
 * web/components/charts/chart-visualizations.tsx     — PlanetData, ChartProps
 * web/components/layout/user-dropdown.tsx            — UserDropdownProps
 * web/components/remedies/remedy-card.tsx            — RemedyCatalog, Recommendation
 * web/components/consultations/booking-modal.tsx     — Astrologer
 * web/components/consultations/chat-components.tsx   — ConsultationBase, ChatMessage
 * web/components/dashboard/widgets/latest-reading.tsx — ChartInterpretation, Chart
 * web/components/dashboard/widgets/chart-quick-view.tsx — PlanetData, ChartData, Chart
 * web/components/dashboard/widgets/current-dasha.tsx — DashaPeriod
 * web/components/dashboard/widgets/western-transit.tsx — Transit
 * web/components/dashboard/widgets/todays-sky.tsx    — PanchangDetail, PanchangResponse
 * web/components/dashboard/widgets/bazi-summary.tsx  — ChartData, Chart
 * web/components/ui/location-picker.tsx              — Person
 * web/components/ui/profile-selector.tsx             — Person
 * web/app/(dashboard)/persons/page.tsx               — Person, PersonFormData
 * web/app/(dashboard)/charts/page.tsx                — Person, PlanetData, ChartDataInner, ChartItem
 * web/app/(dashboard)/charts/[chartId]/page.tsx      — PlanetData, PanchangItem, DashaPeriod, ChartData, Chart, Person
 * web/app/(dashboard)/charts/new/page.tsx            — Person
 * web/app/(dashboard)/panchang/page.tsx              — PanchangElement, PanchangData
 * web/app/(dashboard)/predictions/page.tsx           — PredictionData
 * web/app/(dashboard)/dasha/page.tsx                 — DashaPeriod
 * web/app/(dashboard)/transits/page.tsx              — PlanetPosition, TransitData
 * web/app/(dashboard)/consultations/page.tsx         — Consultation, ConsultationsResponse
 * web/app/(dashboard)/consultations/[consultationId]/page.tsx — Consultation, ConsultationDetailResponse
 * web/app/(dashboard)/astrologers/page.tsx           — Astrologer
 * web/app/(dashboard)/astrologers/[astrologerId]/page.tsx — Astrologer, Review, ProfileResponse
 * web/app/(dashboard)/muhurta/page.tsx               — PanchangDetail, DayQuality, MuhurtaWindow, MuhurtaResult
 * web/app/(dashboard)/remedies/page.tsx              — ChartItem, RecommendResponse, ProgressRecord
 * web/app/(dashboard)/events/page.tsx                — CulturalEvent, UserProfile
 * web/app/(dashboard)/settings/page.tsx              — UserProfile, SubscriptionInfo, UsageInfo
 * web/app/(dashboard)/ai/page.tsx                    — Chart, Transit, DashaResponse, Message
 * web/app/(dashboard)/compatibility/page.tsx         — GunaResult, ManglikStatus, CompatibilityData
 * web/app/(developer)/developer/keys/page.tsx        — ApiKeyResponse, ApiKeyCreatedResponse
 * web/components/predictions/category-card.tsx       — Category
 * web/components/dashboard/widgets/ai-chat-access.tsx — AiHistoryItem
 * web/types/auth.ts                                  — User (old shape)
 * web/types/chart.ts                                 — PlanetPosition, HouseCusp, Chart, CalculateChartRequest
 * web/types/person.ts                                — Person, CreatePersonRequest
 * ───────────────────────────────────────────────────────────────────────────
 */

// =============================================================================
// Generic API Response
// =============================================================================

/** Standard envelope returned by every REST endpoint. */
export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data?: T | null;
  error?: string | null;
  errors?: string[];
}

// =============================================================================
// User / Auth
// =============================================================================

/** User profile returned by GET /api/v1/me. */
export interface UserResponse {
  user_id: string;
  email: string;
  full_name: string;
  phone: string | null;
  avatar_url: string | null;
  ethnicity: string[] | null;
  subscription_tier_id: number | null;
  subscription_tier_name: string | null;
  subscription_end_date: string | null;
  roles: string[];
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  preferences: Record<string, unknown>;
  notification_settings: Record<string, unknown>;
}

/** Body for PUT /api/v1/me. All fields optional (partial update). */
export interface UserUpdate {
  full_name?: string;
  phone?: string | null;
  avatar_url?: string | null;
  date_of_birth?: string | null;
  birth_location?: Record<string, unknown> | null;
  preferences?: Record<string, unknown>;
  notification_settings?: Record<string, unknown>;
  ethnicity?: string[] | null;
}

/** Tier limits included in usage and subscription responses. */
export interface TierLimits {
  charts_per_month: number;
  ai_interpretations_per_month: number;
  saved_charts: number;
  consultations_per_month: number;
}

/** Monthly usage counters returned by GET /api/v1/me/usage. */
export interface UserUsageResponse {
  period: string;
  charts_calculated: number;
  ai_interpretations_used: number;
  consultations_booked: number;
  saved_charts_count: number;
  limits: TierLimits;
}

/** Subscription info returned by GET /api/v1/me/subscription. */
export interface UserSubscriptionInfo {
  subscription_tier_id: number | null;
  subscription_tier_name: string | null;
  subscription_end_date: string | null;
  is_active: boolean;
  has_premium: boolean;
  limits: TierLimits;
}

/**
 * User preferences object (nested keys).
 * Returned by GET /api/v1/me/preferences, updated via PUT.
 */
export interface PreferencesData {
  dashboard?: {
    widget_layout?: unknown[];
    active_widgets?: string[];
  };
  chart?: {
    default_tradition?: string;
    default_house_system?: string;
    default_ayanamsa?: string;
    default_format?: string;
  };
  theme?: string;
  [key: string]: unknown;
}

// =============================================================================
// API Keys
// =============================================================================

/** API key metadata returned by GET /api/v1/api-keys (never includes full key). */
export interface ApiKeyResponse {
  api_key_id: string;
  key_prefix: string;
  name: string;
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

/** Returned once at creation time — includes the plaintext key. */
export interface ApiKeyCreatedResponse {
  api_key_id: string;
  key: string;
  key_prefix: string;
  name: string;
}

// =============================================================================
// Person
// =============================================================================

/** Person profile as returned by the API. */
export interface Person {
  person_id: string;
  organization_id?: string | null;
  user_id?: string | null;
  name: string;
  email?: string | null;
  phone?: string | null;
  date_of_birth: string | null;
  time_of_birth: string | null;
  place_of_birth: string | null;
  latitude: number | string | null;
  longitude: number | string | null;
  timezone: string | null;
  is_default?: boolean;
  gender?: string | null;
  birth_certificate_id?: string | null;
  notes?: string | null;
  external_id?: string | null;
  source_system?: string | null;
  created_at: string;
  updated_at: string;
}

/** Body for POST /api/v1/persons. */
export interface CreatePersonRequest {
  name: string;
  email?: string | null;
  phone?: string | null;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  is_default?: boolean;
  gender?: string | null;
  notes?: string | null;
}

/** Body for PUT /api/v1/persons/:id. */
export interface UpdatePersonRequest {
  name?: string;
  email?: string | null;
  phone?: string | null;
  date_of_birth?: string;
  time_of_birth?: string;
  place_of_birth?: string;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  is_default?: boolean;
  gender?: string | null;
  notes?: string | null;
}

/** Form data for creating/editing a person. */
export interface PersonFormData {
  name: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
}

/** Resolved location from a person profile. */
export interface ProfileLocation {
  latitude: number;
  longitude: number;
  timezone: string;
}

// =============================================================================
// Chart
// =============================================================================

/** Planet position within a chart (DB model shape). */
export interface PlanetPosition {
  planet_position_id?: string;
  chart_id?: string;
  planet_name: string;
  longitude: number;
  latitude: number;
  distance?: number | null;
  speed: number;
  sign: string;
  sign_degree: number;
  house: number;
  house_degree?: number | null;
  nakshatra?: string | null;
  nakshatra_pada?: number | null;
  dignity?: string | null;
  is_retrograde: boolean;
  is_combust: boolean;
}

/**
 * Inline planet data as returned inside chart_data.planets (calculation output).
 * This differs from PlanetPosition (the DB model) — it uses the raw calculator
 * keys (e.g. "degree_in_sign" vs "sign_degree").
 */
export interface PlanetData {
  planet: string;
  longitude: number;
  latitude: number;
  speed: number;
  sign: string;
  sign_index?: number;
  degree_in_sign: number;
  nakshatra?: string;
  nakshatra_pada?: number;
  house: number;
  is_retrograde: boolean;
}

/** House cusp entry. */
export interface HouseCusp {
  house: number;
  longitude: number;
  sign: string;
  degree_in_sign: number;
}

/** Aspect between two planets. */
export interface Aspect {
  planet1: string;
  planet2: string;
  aspect_type: string;
  angle: number;
  orb: number;
  is_applying: boolean;
}

/** Full astrology chart as stored in the DB and returned by the API. */
export interface AstrologyChart {
  chart_id: string;
  person_id: string;
  organization_id?: string;
  user_id?: string;
  chart_type: string;
  house_system: string | null;
  ayanamsa: string | null;
  calculated_at: string;
  calculation_version: string;
  chart_data: Record<string, unknown>;
  planet_positions: Record<string, unknown>;
  house_cusps: number[];
  aspects: Aspect[];
  divisional_chart_type?: number | null;
  progression_type?: string | null;
  created_at: string;
  updated_at: string;
}

/** Shorthand chart item used in list views (charts listing page, remedies, etc.). */
export interface ChartItem {
  chart_id: string;
  person_id: string;
  chart_type: string;
  house_system?: string | null;
  ayanamsa?: string | null;
  calculated_at: string;
  chart_data: Record<string, unknown>;
  planet_positions: Record<string, unknown>;
  house_cusps?: number[];
  aspects?: Aspect[];
  created_at: string;
}

/** Chart interpretation (AI-generated or expert). */
export interface ChartInterpretation {
  chart_interpretation_id: string;
  chart_id: string;
  interpretation_type: string;
  language: string;
  title: string;
  summary: string;
  detailed_text: Record<string, unknown>;
  interpreter_version: string;
  confidence_score: number;
  keywords: string[];
  created_at: string;
  updated_at: string;
}

/** Body for POST /api/v1/charts/calculate-chart (stateless calculation). */
export interface CalculateChartRequest {
  name?: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  calculation_system?: string;
  ayanamsa?: string;
  house_system?: string;
}

// =============================================================================
// Panchang
// =============================================================================

/** A single panchang element (tithi, nakshatra, yoga, karana). */
export interface PanchangElement {
  name: string;
  deity?: string;
  ruler?: string;
  pada?: number;
  percentage?: number;
  end_time?: string;
  type?: string;
  effect?: string;
}

/** Inauspicious time windows within a day. */
export interface InauspiciousTimes {
  rahu_kaal: string;
  gulika_kaal: string;
  yamaganda: string;
}

/** Auspicious time windows within a day. */
export interface AuspiciousTimes {
  abhijit_muhurta: string;
  brahma_muhurta: string;
}

/** Full panchang detail for a given date/location. */
export interface PanchangDetail {
  sunrise: string;
  sunset: string;
  tithi?: PanchangElement | { name?: string };
  nakshatra?: PanchangElement | { name?: string };
  yoga?: PanchangElement | { name?: string };
  karana?: PanchangElement | { name?: string };
  vara?: string;
  inauspicious_times: InauspiciousTimes;
  auspicious_times: AuspiciousTimes;
}

/** Data envelope from GET /api/v1/panchang. */
export interface PanchangResponse {
  date: string;
  location: {
    latitude: number;
    longitude: number;
    timezone: string;
  };
  tithi: string;
  nakshatra: string;
  yoga: string;
  karana: string;
  detailed_panchang: PanchangDetail;
  auspicious_periods: unknown[];
}

// =============================================================================
// Muhurta
// =============================================================================

/** A single muhurta (auspicious time window). */
export interface MuhurtaWindow {
  start_time?: string;
  end_time?: string;
  date?: string;
  quality?: string;
  nakshatra?: string;
  tithi?: string;
  yoga?: string;
  special_factors?: string[];
  avoid_factors?: string[];
  overall_score?: number;
  score?: number;
  reason?: string;
  explanation?: string;
  [key: string]: unknown;
}

/** Data envelope from POST /api/v1/panchang/muhurta. */
export interface MuhurtaResponse {
  purpose: string;
  location: {
    latitude: number;
    longitude: number;
    timezone: string;
  };
  search_period: {
    start: string;
    end: string;
  };
  auspicious_times: MuhurtaWindow[];
  total_found: number;
}

/** Day quality used in muhurta calendar views. */
export interface DayQuality {
  date: string;
  quality: string;
  score?: number;
  tithi?: string;
  nakshatra?: string;
}

// =============================================================================
// Transits
// =============================================================================

/** A single transit aspect between a transiting planet and a natal position. */
export interface TransitAspect {
  planet: string;
  current_sign: string;
  current_degree: number;
  natal_sign: string;
  natal_degree: number;
  aspect: string;
  orb: number;
  intensity: string;
  effects: string;
}

/** Current planetary position snapshot (used in transit response). */
export interface CurrentPlanetaryPosition {
  sign: string;
  degree: number;
  retrograde: boolean;
}

/** Data envelope from GET /api/v1/transits/current/:person_id. */
export interface CurrentTransitsData {
  person_id: string;
  current_date: string;
  major_transits: TransitAspect[];
  current_planetary_positions: Record<string, CurrentPlanetaryPosition>;
}

/** Forecast events from GET /api/v1/transits/forecast/:person_id. */
export interface TransitForecastData {
  person_id: string;
  forecast_period: {
    start: string;
    end: string;
    days: number;
  };
  forecast: {
    exact_transits: Array<{
      date: string;
      planet: string;
      aspect: string;
      natal_planet: string;
      interpretation: string;
    }>;
    sign_changes: Array<{
      date: string;
      planet: string;
      from_sign: string;
      to_sign: string;
      duration?: string;
    }>;
    retrograde_periods: Array<{
      planet: string;
      date: string;
      sign: string;
      type?: string;
    }>;
  };
}

// =============================================================================
// Dasha
// =============================================================================

/** A single dasha (planetary period). */
export interface DashaPeriod {
  planet: string;
  start_date: string;
  end_date: string;
  duration_years?: number;
  is_current?: boolean;
  level?: string;
}

/** Current dasha breakdown (mahadasha / antardasha / pratyantardasha). */
export interface CurrentDasha {
  mahadasha?: DashaPeriod | null;
  antardasha?: DashaPeriod | null;
  pratyantardasha?: DashaPeriod | null;
  sookshma?: DashaPeriod | null;
  prana?: DashaPeriod | null;
}

/** Data envelope from GET /api/v1/dasha/vimshottari/:person_id. */
export interface VimshottariDashaData {
  person_id: string;
  birth_nakshatra: string;
  current_dasha: CurrentDasha | null;
  dasha_sequence: DashaPeriod[];
  detailed_periods: {
    current_mahadasha: DashaPeriod | null;
    current_antardasha: DashaPeriod | null;
    current_pratyantardasha: DashaPeriod | null;
    upcoming_changes: DashaPeriod[];
  };
  life_timeline: DashaPeriod[];
}

/** Data envelope from GET /api/v1/dasha/yogini/:person_id. */
export interface YoginiDashaData {
  person_id: string;
  moon_nakshatra: string;
  yogini_cycle: string;
  current_yogini: unknown;
  yogini_sequence: Record<string, number>;
}

// =============================================================================
// Predictions
// =============================================================================

/**
 * A prediction category (one of 10 life areas).
 * Returned by daily/weekly/monthly/quarterly/half-yearly/yearly endpoints.
 */
export interface PredictionCategory {
  name: string;
  slug: string;
  houses: number[];
  score: number;
  summary: string;
  details: string;
  advice: string;
  caution: string | null;
}

/** Sign change event within a prediction period. */
export interface SignChange {
  planet: string;
  date: string;
  from_sign: string;
  to_sign: string;
}

/** Data envelope from GET /api/v1/predictions/{timeframe}/:person_id. */
export interface PredictionData {
  timeframe: string;
  period: {
    start: string;
    end: string;
  };
  overall_score: number;
  overall_summary: string;
  categories: PredictionCategory[];
  sign_changes?: SignChange[];
  auspicious_times?: string[];
  caution_periods?: string[];
  /** Person ID is always present. */
  person_id: string;
  /** Daily-only fields. */
  moon_sign?: string;
  ascendant_sign?: string;
  current_moon_transit?: string;
  /** Weekly+ fields. */
  month?: number;
  year?: number;
  quarter?: number;
  half?: number;
  dasha_lord?: string | null;
  antardasha_lord?: string | null;
}

// =============================================================================
// Astrologer
// =============================================================================

/** Astrologer profile returned by marketplace endpoints. */
export interface AstrologerResponse {
  astrologer_id: string;
  user_id: string;
  professional_name: string;
  bio: string;
  years_experience: number;
  specializations: string[];
  languages: string[];
  hourly_rate: number;
  currency: string;
  rating: number;
  total_consultations: number;
  total_reviews: number;
  verification_status_id: number | null;
  verification_status_name: string | null;
  is_active: boolean;
  is_featured: boolean;
  profile_image_url: string | null;
  joined_at: string;
}

/** Review for an astrologer. */
export interface AstrologerReview {
  review_id: string;
  astrologer_id: string;
  user_id: string;
  rating: number;
  title: string | null;
  review_text: string | null;
  accuracy_rating: number | null;
  communication_rating: number | null;
  empathy_rating: number | null;
  is_verified: boolean;
  helpful_votes: number;
  created_at: string;
}

/** Data envelope from GET /api/v1/astrologers/:id. */
export interface AstrologerProfileResponse {
  astrologer: AstrologerResponse;
  recent_reviews: AstrologerReview[];
  specialization_display: string[];
}

/** Data envelope from GET /api/v1/astrologers/search. */
export interface SearchAstrologersData {
  astrologers: AstrologerResponse[];
  total: number;
  page: number;
  page_size: number;
}

// =============================================================================
// Consultation
// =============================================================================

/** Consultation as returned by the API. */
export interface ConsultationResponse {
  consultation_id: string;
  user_id: string;
  astrologer_id: string;
  chart_id: string;
  consultation_type_id: number | null;
  consultation_type_name: string | null;
  status_id: number | null;
  status_name: string | null;
  user_questions: string[];
  focus_areas: string[];
  special_requests?: string | null;
  scheduled_at: string | null;
  duration_minutes: number;
  total_amount: number;
  currency: string;
  payment_status_id: number | null;
  payment_status_name: string | null;
  ai_summary: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at: string | null;
}

/** A message within a consultation chat. */
export interface ConsultationMessage {
  message_id: string;
  consultation_id: string;
  sender_id: string;
  message_type: string;
  content: string;
  attachment_url: string | null;
  attachment_type?: string | null;
  message_metadata?: Record<string, unknown> | null;
  is_read: boolean;
  read_at?: string | null;
  created_at: string;
}

/** Full consultation detail (consultation + messages). */
export interface ConsultationDetailsData {
  consultation: ConsultationResponse;
  messages: ConsultationMessage[];
  astrologer?: AstrologerResponse;
}

/** List response for GET /api/v1/consultations. */
export interface MyConsultationsData {
  consultations: ConsultationResponse[];
  total: number;
}

/** Body for POST /api/v1/consultations. */
export interface ConsultationRequest {
  astrologer_id: string;
  chart_id: string;
  consultation_type_id?: number | null;
  consultation_type_name?: string | null;
  user_questions: string[];
  focus_areas?: string[];
  special_requests?: string | null;
  preferred_times?: string[];
  duration_minutes?: number;
  timezone?: string;
}

/** Consultation statistics (astrologer dashboard). */
export interface ConsultationStats {
  total_consultations: number;
  completed_consultations: number;
  average_rating: number;
  total_revenue: number;
  response_time_hours: number;
  completion_rate: number;
}

// =============================================================================
// Cultural Events
// =============================================================================

/** A cultural or religious event from the events calendar. */
export interface CulturalEvent {
  name: string;
  date_2026: string;
  end_date_2026: string | null;
  ethnicity_tags: string[];
  tradition: string;
  description: string;
  significance: string;
  rituals: string[];
  astrological_significance: string;
}

/** Data envelope from GET /api/v1/events/cultural. */
export interface CulturalEventsData {
  events: CulturalEvent[];
  total: number;
  filters: {
    ethnicity: string[] | null;
    year: number;
    month: number | null;
  };
}

// =============================================================================
// Remedies
// =============================================================================

/** A remedy from the catalog. */
export interface RemedyResponse {
  remedy_id: string;
  name: string;
  type_id: number | null;
  type_name: string | null;
  tradition_id: number | null;
  tradition_name: string | null;
  planet: string | null;
  dosha_type_id: number | null;
  dosha_type_name: string | null;
  description: Record<string, string>;
  instructions: Record<string, string>;
  benefits: Record<string, string>;
  precautions: Record<string, string>;
  duration_days: number | null;
  frequency: string | null;
  best_time: string | null;
  materials_needed: string[];
  effectiveness_rating: number;
  difficulty_level: number;
  cost_level: number;
  mantra_text: string | null;
  mantra_audio_url: string | null;
  instruction_video_url: string | null;
  yantra_image_url: string | null;
  created_at: string;
}

/** AI/expert remedy recommendation. */
export interface RemedyRecommendation {
  recommendation_id: string;
  remedy: RemedyResponse;
  relevance_score: number;
  priority_level: number;
  issue_description: string;
  expected_timeline: string | null;
  personalized_instructions: string | null;
  confidence_score: number | null;
  created_at: string;
}

/** User's progress tracking for a specific remedy. */
export interface RemedyProgress {
  remedy_progress_id: string;
  person_id: string;
  remedy_type: string;
  remedy_name: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
}

/** Detailed progress tracking (from the user_remedy_progress table). */
export interface UserRemedyProgress {
  progress_id: string;
  remedy_id: string;
  started_at: string;
  current_day: number;
  total_days: number | null;
  completion_percentage: number;
  is_completed: boolean;
  effectiveness_rating: number | null;
  would_recommend: boolean | null;
}

// =============================================================================
// AI Interpretations
// =============================================================================

/** Body for POST /api/v1/ai/interpret. */
export interface InterpretationRequest {
  chart_id: string;
  question: string;
  style?: 'balanced' | 'traditional' | 'modern' | 'psychological' | 'spiritual';
  provider?: string | null;
  user_context?: Record<string, unknown> | null;
}

/** Body for POST /api/v1/ai/neural-pathway. */
export interface NeuralPathwayRequest {
  chart_id: string;
  previous_responses?: Record<string, unknown>[];
  focus_area?: string | null;
}

// =============================================================================
// Location / Geocoding
// =============================================================================

/** A single geocoded location result. */
export interface LocationResult {
  place: string;
  formatted_address: string;
  latitude: number;
  longitude: number;
  timezone: string;
  components: {
    city?: string;
    state?: string;
    country?: string;
    country_code?: string;
  };
  confidence: number;
}

/** Data envelope from GET /api/v1/location/search. */
export interface LocationSearchData {
  results: LocationResult[];
  count: number;
}

// =============================================================================
// Compatibility / Synastry
// =============================================================================

/** Data envelope from POST /api/v1/charts/synastry. */
export interface SynastryData {
  person1: { person_id: string; name: string };
  person2: { person_id: string; name: string };
  inter_aspects: Aspect[];
  compatibility_score: number;
  summary: string;
  composite_chart?: Record<string, unknown>;
}

// =============================================================================
// Lookups / Enums
// =============================================================================

/** A single enum entry from GET /api/v1/lookups/:type. */
export interface LookupEntry {
  id: number;
  name: string;
  description?: string;
}

/** Data envelope from GET /api/v1/lookups. */
export interface LookupsData {
  [enumType: string]: LookupEntry[];
}
