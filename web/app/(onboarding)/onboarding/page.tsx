'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import PlaceAutocomplete from '@/components/ui/place-autocomplete';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MOTHER_TONGUE_OPTIONS = [
  'Tamil', 'Telugu', 'Kannada', 'Hindi', 'Malayalam', 'Bengali', 'English', 'Other',
];

const APP_LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'ta', label: 'Tamil' },
  { value: 'te', label: 'Telugu' },
  { value: 'kn', label: 'Kannada' },
  { value: 'hi', label: 'Hindi' },
  { value: 'ml', label: 'Malayalam' },
  { value: 'bn', label: 'Bengali' },
  { value: 'sa', label: 'Sanskrit' },
];

const ETHNICITY_OPTIONS = [
  'Tamil', 'Telugu', 'Kannada', 'North Indian', 'Bengali', 'Keralite',
  'Maharashtrian', 'Gujarati', 'Punjabi', 'Marwari', 'Assamese',
  'Odia', 'Rajasthani', 'Kashmiri', 'Other',
];

const RELIGION_OPTIONS = [
  'Hindu', 'Muslim', 'Christian', 'Sikh', 'Buddhist', 'Jain',
  'Zoroastrian', 'Spiritual (Non-religious)', 'Other',
];

const GENDER_OPTIONS = ['Male', 'Female', 'Other', 'Prefer not to say'];

const TRADITION_OPTIONS = [
  { value: 'vedic', label: 'Vedic (Jyotish)' },
  { value: 'western', label: 'Western' },
  { value: 'chinese', label: 'Chinese' },
];

const HOUSE_SYSTEM_OPTIONS = [
  { value: 'whole_sign', label: 'Whole Sign' },
  { value: 'placidus', label: 'Placidus' },
  { value: 'koch', label: 'Koch' },
  { value: 'equal', label: 'Equal' },
];

const AYANAMSA_OPTIONS = [
  { value: 'lahiri', label: 'Lahiri' },
  { value: 'raman', label: 'Raman' },
  { value: 'kp', label: 'KP (Krishnamurti)' },
];

const CHART_FORMAT_OPTIONS = [
  { value: 'South Indian', label: 'South Indian' },
  { value: 'North Indian', label: 'North Indian' },
  { value: 'Western Wheel', label: 'Western Wheel' },
];

const PROGRESS_STEPS = [
  'Creating your birth profile...',
  'Calculating planetary positions...',
  'Computing house cusps...',
  'Analysing nakshatra placements...',
  'Preparing your dashboard...',
];

// ---------------------------------------------------------------------------
// Shared styles
// ---------------------------------------------------------------------------

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 10,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '1.5px',
  color: '#5B6A8A',
  marginBottom: 6,
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  fontSize: 14,
  color: '#D4DAE6',
  background: '#060A14',
  border: '1px solid #1A2340',
  borderRadius: 8,
  outline: 'none',
  transition: 'border-color 0.2s',
  boxSizing: 'border-box',
};

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  appearance: 'none',
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235B6A8A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 12px center',
  paddingRight: 36,
};

const focusHandlers = {
  onFocus: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.target.style.borderColor = '#C8913A';
  },
  onBlur: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.target.style.borderColor = '#1A2340';
  },
};

const goldButtonStyle: React.CSSProperties = {
  width: '100%',
  padding: '13px 0',
  fontSize: 15,
  fontWeight: 600,
  color: '#000',
  background: 'linear-gradient(135deg, #C8913A, #D4A04A)',
  border: 'none',
  borderRadius: 10,
  cursor: 'pointer',
  transition: 'opacity 0.2s',
  marginTop: 8,
};

// ---------------------------------------------------------------------------
// Step indicator
// ---------------------------------------------------------------------------

function StepIndicator({ current, total }: { current: number; total: number }) {
  return (
    <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginBottom: 32 }}>
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: i <= current ? '#C8913A' : '#1A2340',
            transition: 'background 0.3s',
          }}
        />
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Multi-select pills
// ---------------------------------------------------------------------------

function PillSelect({
  options,
  selected,
  onChange,
}: {
  options: string[];
  selected: string[];
  onChange: (val: string[]) => void;
}) {
  const toggle = (opt: string) => {
    onChange(selected.includes(opt) ? selected.filter((s) => s !== opt) : [...selected, opt]);
  };
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
      {options.map((opt) => {
        const active = selected.includes(opt);
        return (
          <button
            key={opt}
            type="button"
            onClick={() => toggle(opt)}
            style={{
              padding: '6px 14px',
              fontSize: 13,
              borderRadius: 20,
              border: `1px solid ${active ? '#C8913A' : '#1A2340'}`,
              background: active ? 'rgba(200,145,58,0.15)' : 'transparent',
              color: active ? '#D4A04A' : '#8B99B5',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Step 1: About You
// ---------------------------------------------------------------------------

interface Step1Data {
  fullName: string;
  gender: string;
  dateOfBirth: string;
  timeOfBirth: string;
  unknownBirthTime: boolean;
  placeOfBirth: string;
  latitude: number | null;
  longitude: number | null;
}

function StepAboutYou({
  data,
  onChange,
  onNext,
}: {
  data: Step1Data;
  onChange: (d: Step1Data) => void;
  onNext: () => void;
}) {
  // Ref to always access latest data — prevents stale closures in Google Maps listener
  const dataRef = useRef(data);
  dataRef.current = data;

  const handlePlaceChange = useCallback(
    (val: string) => onChange({ ...dataRef.current, placeOfBirth: val }),
    [onChange],
  );

  const handlePlaceSelect = useCallback(
    (place: { name: string; lat: number; lng: number }) =>
      onChange({ ...dataRef.current, placeOfBirth: place.name, latitude: place.lat, longitude: place.lng }),
    [onChange],
  );

  const canProceed = data.fullName.trim() && data.dateOfBirth && data.placeOfBirth;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ textAlign: 'center', marginBottom: 4 }}>
        <h1
          className="font-display"
          style={{ fontSize: 26, color: '#D4DAE6', fontWeight: 400, margin: 0 }}
        >
          About You
        </h1>
        <p style={{ fontSize: 14, color: '#5B6A8A', marginTop: 6 }}>
          We need your birth details to cast an accurate chart.
        </p>
      </div>

      {/* Full name */}
      <div>
        <label style={labelStyle}>Full Name</label>
        <input
          type="text"
          value={data.fullName}
          onChange={(e) => onChange({ ...data, fullName: e.target.value })}
          placeholder="Your full name"
          style={inputStyle}
          {...focusHandlers}
        />
      </div>

      {/* Gender */}
      <div>
        <label style={labelStyle}>Gender</label>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {GENDER_OPTIONS.map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => onChange({ ...data, gender: g })}
              style={{
                padding: '8px 16px',
                fontSize: 13,
                borderRadius: 8,
                border: `1px solid ${data.gender === g ? '#C8913A' : '#1A2340'}`,
                background: data.gender === g ? 'rgba(200,145,58,0.15)' : 'transparent',
                color: data.gender === g ? '#D4A04A' : '#8B99B5',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {/* Date of birth */}
      <div>
        <label style={labelStyle}>Date of Birth</label>
        <input
          type="date"
          value={data.dateOfBirth}
          onChange={(e) => onChange({ ...data, dateOfBirth: e.target.value })}
          style={{ ...inputStyle, colorScheme: 'dark' }}
          {...focusHandlers}
        />
      </div>

      {/* Time of birth */}
      <div>
        <label style={labelStyle}>Time of Birth</label>
        <input
          type="time"
          value={data.unknownBirthTime ? '' : data.timeOfBirth}
          onChange={(e) => onChange({ ...data, timeOfBirth: e.target.value })}
          disabled={data.unknownBirthTime}
          style={{
            ...inputStyle,
            colorScheme: 'dark',
            opacity: data.unknownBirthTime ? 0.4 : 1,
          }}
          {...focusHandlers}
        />
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginTop: 8,
            fontSize: 13,
            color: '#8B99B5',
            cursor: 'pointer',
          }}
        >
          <input
            type="checkbox"
            checked={data.unknownBirthTime}
            onChange={(e) =>
              onChange({ ...data, unknownBirthTime: e.target.checked, timeOfBirth: '' })
            }
            style={{ accentColor: '#C8913A' }}
          />
          I don&apos;t know my birth time
        </label>
        {data.unknownBirthTime && (
          <p style={{ fontSize: 12, color: '#5B6A8A', marginTop: 4, fontStyle: 'italic' }}>
            We&apos;ll use sunrise time as per Vedic convention.
          </p>
        )}
      </div>

      {/* Place of birth */}
      <div>
        <label style={labelStyle}>Place of Birth</label>
        <PlaceAutocomplete
          value={data.placeOfBirth}
          onChange={handlePlaceChange}
          onSelect={handlePlaceSelect}
          placeholder="City, Country"
          style={inputStyle}
        />
      </div>

      <button
        type="button"
        onClick={onNext}
        disabled={!canProceed}
        style={{
          ...goldButtonStyle,
          opacity: canProceed ? 1 : 0.45,
          cursor: canProceed ? 'pointer' : 'not-allowed',
        }}
      >
        Next &rarr;
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Step 2: Language & Culture
// ---------------------------------------------------------------------------

interface Step2Data {
  motherTongue: string;
  languagesSpoken: string[];
  appLanguage: string;
  ethnicity: string;
  religion: string;
}

interface Step3Data {
  tradition: string;
  houseSystem: string;
  ayanamsa: string;
  chartFormat: string;
}

function StepCulture({
  data,
  onChange,
  onBack,
  onNext,
}: {
  data: Step2Data;
  onChange: (d: Step2Data) => void;
  onBack: () => void;
  onNext: () => void;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ textAlign: 'center', marginBottom: 4 }}>
        <h1
          className="font-display"
          style={{ fontSize: 26, color: '#D4DAE6', fontWeight: 400, margin: 0 }}
        >
          Language &amp; Culture
        </h1>
        <p style={{ fontSize: 14, color: '#5B6A8A', marginTop: 6 }}>
          Helps us personalise interpretations for your tradition.
        </p>
      </div>

      {/* Mother tongue */}
      <div>
        <label style={labelStyle}>Mother Tongue</label>
        <select
          value={data.motherTongue}
          onChange={(e) => onChange({ ...data, motherTongue: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          <option value="">Select...</option>
          {MOTHER_TONGUE_OPTIONS.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
      </div>

      {/* Languages spoken */}
      <div>
        <label style={labelStyle}>Languages Spoken</label>
        <PillSelect
          options={MOTHER_TONGUE_OPTIONS}
          selected={data.languagesSpoken}
          onChange={(val) => onChange({ ...data, languagesSpoken: val })}
        />
      </div>

      {/* App language */}
      <div>
        <label style={labelStyle}>App Language</label>
        <select
          value={data.appLanguage}
          onChange={(e) => onChange({ ...data, appLanguage: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          {APP_LANGUAGE_OPTIONS.map((l) => (
            <option key={l.value} value={l.value}>
              {l.label}
            </option>
          ))}
        </select>
      </div>

      {/* Ethnicity */}
      <div>
        <label style={labelStyle}>Ethnicity</label>
        <select
          value={data.ethnicity}
          onChange={(e) => onChange({ ...data, ethnicity: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          <option value="">Select...</option>
          {ETHNICITY_OPTIONS.map((e) => (
            <option key={e} value={e}>
              {e}
            </option>
          ))}
        </select>
      </div>

      {/* Religion */}
      <div>
        <label style={labelStyle}>Religion</label>
        <select
          value={data.religion}
          onChange={(e) => onChange({ ...data, religion: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          <option value="">Select...</option>
          {RELIGION_OPTIONS.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
        <button
          type="button"
          onClick={onBack}
          style={{
            flex: 1,
            padding: '13px 0',
            fontSize: 14,
            fontWeight: 600,
            color: '#8B99B5',
            background: 'transparent',
            border: '1px solid #1A2340',
            borderRadius: 10,
            cursor: 'pointer',
          }}
        >
          &larr; Back
        </button>
        <button type="button" onClick={onNext} style={{ ...goldButtonStyle, flex: 2 }}>
          Next &rarr;
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Step 3: Chart Preferences
// ---------------------------------------------------------------------------

function StepChartPreferences({
  data,
  onChange,
  onBack,
  onComplete,
}: {
  data: Step3Data;
  onChange: (d: Step3Data) => void;
  onBack: () => void;
  onComplete: () => void;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ textAlign: 'center', marginBottom: 4 }}>
        <h1
          className="font-display"
          style={{ fontSize: 26, color: '#D4DAE6', fontWeight: 400, margin: 0 }}
        >
          Chart Preferences
        </h1>
        <p style={{ fontSize: 14, color: '#5B6A8A', marginTop: 6 }}>
          Choose your preferred astrological system and defaults.
        </p>
      </div>

      {/* Tradition */}
      <div>
        <label style={labelStyle}>Default Tradition</label>
        <select
          value={data.tradition}
          onChange={(e) => onChange({ ...data, tradition: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          {TRADITION_OPTIONS.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {/* House System */}
      <div>
        <label style={labelStyle}>House System</label>
        <select
          value={data.houseSystem}
          onChange={(e) => onChange({ ...data, houseSystem: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          {HOUSE_SYSTEM_OPTIONS.map((h) => (
            <option key={h.value} value={h.value}>
              {h.label}
            </option>
          ))}
        </select>
      </div>

      {/* Ayanamsa */}
      <div>
        <label style={labelStyle}>Ayanamsa</label>
        <select
          value={data.ayanamsa}
          onChange={(e) => onChange({ ...data, ayanamsa: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          {AYANAMSA_OPTIONS.map((a) => (
            <option key={a.value} value={a.value}>
              {a.label}
            </option>
          ))}
        </select>
      </div>

      {/* Chart Format */}
      <div>
        <label style={labelStyle}>Chart Format</label>
        <select
          value={data.chartFormat}
          onChange={(e) => onChange({ ...data, chartFormat: e.target.value })}
          style={selectStyle}
          onFocus={focusHandlers.onFocus}
          onBlur={focusHandlers.onBlur}
        >
          {CHART_FORMAT_OPTIONS.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
        <button
          type="button"
          onClick={onBack}
          style={{
            flex: 1,
            padding: '13px 0',
            fontSize: 14,
            fontWeight: 600,
            color: '#8B99B5',
            background: 'transparent',
            border: '1px solid #1A2340',
            borderRadius: 10,
            cursor: 'pointer',
          }}
        >
          &larr; Back
        </button>
        <button type="button" onClick={onComplete} style={{ ...goldButtonStyle, flex: 2 }}>
          Complete Setup &rarr;
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Step 3: Calculating (auto-step)
// ---------------------------------------------------------------------------

function StepCalculating({ completedSteps }: { completedSteps: number }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
        textAlign: 'center',
        gap: 32,
      }}
    >
      {/* Pulsing ring */}
      <div
        style={{
          width: 72,
          height: 72,
          borderRadius: '50%',
          border: '3px solid transparent',
          borderTopColor: '#C8913A',
          borderRightColor: '#C8913A',
          animation: 'onboarding-spin 1.2s linear infinite',
          position: 'relative',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 8,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(200,145,58,0.15), transparent 70%)',
          }}
        />
      </div>

      <div>
        <h1
          className="font-display"
          style={{ fontSize: 24, color: '#D4DAE6', fontWeight: 400, margin: 0 }}
        >
          Generating your Vedic birth chart...
        </h1>
        <p style={{ fontSize: 14, color: '#5B6A8A', marginTop: 8 }}>This only takes a moment.</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14, minWidth: 280 }}>
        {PROGRESS_STEPS.map((label, i) => {
          const done = i < completedSteps;
          const active = i === completedSteps;
          return (
            <div
              key={label}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                fontSize: 14,
                color: done ? '#6AAF7A' : active ? '#D4DAE6' : '#3A4A6A',
                transition: 'color 0.4s',
              }}
            >
              <span style={{ width: 20, textAlign: 'center', fontSize: 15 }}>
                {done ? '\u2713' : active ? '\u2022' : '\u00B7'}
              </span>
              {label}
            </div>
          );
        })}
      </div>

      <style>{`
        @keyframes onboarding-spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main onboarding page
// ---------------------------------------------------------------------------

export default function OnboardingPage() {
  const router = useRouter();
  const { user, isAuthReady } = useAuth();

  const [step, setStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(0);
  const [error, setError] = useState('');

  // Step 1 state
  const [step1, setStep1] = useState<Step1Data>({
    fullName: '',
    gender: '',
    dateOfBirth: '',
    timeOfBirth: '',
    unknownBirthTime: false,
    placeOfBirth: '',
    latitude: null,
    longitude: null,
  });

  // Step 2 state
  const [step2, setStep2] = useState<Step2Data>({
    motherTongue: '',
    languagesSpoken: [],
    appLanguage: 'en',
    ethnicity: '',
    religion: '',
  });

  // Step 3 state — chart preferences (with sensible defaults)
  const [step3, setStep3] = useState<Step3Data>({
    tradition: 'vedic',
    houseSystem: 'whole_sign',
    ayanamsa: 'lahiri',
    chartFormat: 'South Indian',
  });

  // Pre-fill from Clerk user name
  useEffect(() => {
    if (user?.full_name && !step1.fullName) {
      setStep1((prev) => ({ ...prev, fullName: user.full_name }));
    }
  }, [user?.full_name]); // eslint-disable-line react-hooks/exhaustive-deps

  // Format time for the API: "HH:MM" -> "HH:MM:SS"
  const formatTimeForApi = useCallback((time: string): string | null => {
    if (!time) return null;
    // Backend expects just the time portion: HH:MM or HH:MM:SS
    return time.length === 5 ? `${time}:00` : time;
  }, []);

  // Step 3: run API calls with animated progress
  const runOnboarding = useCallback(async () => {
    setStep(3);
    setCompletedSteps(0);
    setError('');

    // Timer that reveals progress steps one at a time
    let progressIdx = 0;
    const progressInterval = setInterval(() => {
      progressIdx += 1;
      if (progressIdx <= PROGRESS_STEPS.length) {
        setCompletedSteps(progressIdx);
      }
    }, 1200);

    try {
      // 1. Save user preferences + chart defaults
      await apiClient.put('/api/v1/me', {
        language_preference: step2.appLanguage,
        ethnicity: step2.ethnicity || undefined,
        religion: step2.religion || undefined,
        is_onboarded: true,
        preferences: {
          mother_tongue: step2.motherTongue || undefined,
          languages_spoken: step2.languagesSpoken.length > 0 ? step2.languagesSpoken : undefined,
        },
      });

      // Save chart preferences
      await apiClient.put('/api/v1/me/preferences', {
        chart: {
          default_tradition: step3.tradition,
          default_house_system: step3.houseSystem,
          default_ayanamsa: step3.ayanamsa,
          default_format: step3.chartFormat,
        },
      });

      // 2. Save/create person profile with birth details
      const timeValue = step1.unknownBirthTime
        ? formatTimeForApi('06:00') // sunrise default
        : formatTimeForApi(step1.timeOfBirth);

      const personPayload = {
        name: step1.fullName,
        date_of_birth: step1.dateOfBirth,
        time_of_birth: timeValue,
        place_of_birth: step1.placeOfBirth,
        // Round to 6 decimal places to satisfy backend Decimal(max_digits=9, decimal_places=6)
        latitude: step1.latitude != null ? Math.round(step1.latitude * 1e6) / 1e6 : null,
        longitude: step1.longitude != null ? Math.round(step1.longitude * 1e6) / 1e6 : null,
        gender: step1.gender || undefined,
        is_default: true,
      };

      // Always create a new profile (no auto-profile on signup anymore)
      const res = await apiClient.post<{ person_id: string }>('/api/v1/persons/', personPayload);
      const personId = res.data!.person_id;

      // 3. Calculate chart using user-selected preferences
      const params = new URLSearchParams({
        person_id: personId,
        systems: step3.tradition,
        house_system: step3.houseSystem,
        ayanamsa: step3.ayanamsa,
      });
      await apiClient.post(`/api/v1/charts/calculate?${params.toString()}`);

      // Ensure all progress steps show as complete
      clearInterval(progressInterval);
      setCompletedSteps(PROGRESS_STEPS.length);

      // Short delay so user sees final checkmarks
      await new Promise((r) => setTimeout(r, 800));
      router.push('/dashboard');
    } catch (err) {
      clearInterval(progressInterval);
      const msg = err instanceof Error ? err.message : 'Something went wrong.';
      setError(msg);
      // Fall back to step 1 so user can retry
      setStep(0);
    }
  }, [step1, step2, step3, formatTimeForApi, router]);

  // Card wrapper
  const cardStyle: React.CSSProperties = {
    position: 'relative',
    zIndex: 1,
    width: '100%',
    maxWidth: 520,
    margin: '0 auto',
    padding: step === 3 ? '48px 32px' : '40px 32px',
    background: step === 3 ? 'transparent' : 'rgba(17,24,40,0.7)',
    border: step === 3 ? 'none' : '1px solid #1A2340',
    borderRadius: 16,
    backdropFilter: step === 3 ? 'none' : 'blur(20px)',
  };

  return (
    <div style={cardStyle}>
      {step < 3 && <StepIndicator current={step} total={4} />}

      {error && (
        <div
          style={{
            padding: '10px 14px',
            marginBottom: 16,
            fontSize: 13,
            color: '#C45D4A',
            background: 'rgba(196,93,74,0.1)',
            border: '1px solid rgba(196,93,74,0.2)',
            borderRadius: 8,
          }}
        >
          {error}
        </div>
      )}

      {step === 0 && (
        <StepAboutYou data={step1} onChange={setStep1} onNext={() => setStep(1)} />
      )}

      {step === 1 && (
        <StepCulture
          data={step2}
          onChange={setStep2}
          onBack={() => setStep(0)}
          onNext={() => setStep(2)}
        />
      )}

      {step === 2 && (
        <StepChartPreferences
          data={step3}
          onChange={setStep3}
          onBack={() => setStep(1)}
          onComplete={runOnboarding}
        />
      )}

      {step === 3 && <StepCalculating completedSteps={completedSteps} />}
    </div>
  );
}
