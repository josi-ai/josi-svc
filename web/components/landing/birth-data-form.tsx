'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import PlaceAutocomplete from '@/components/ui/place-autocomplete';

export default function BirthDataForm() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [dob, setDob] = useState('');
  const [tob, setTob] = useState('');
  const [place, setPlace] = useState('');

  const inputStyle = {
    background: '#0A0F1E',
    border: '1px solid #1A2340',
  };

  const inputClass =
    'w-full rounded-lg px-4 py-3 text-sm text-white placeholder-[#3A4A6A] outline-none transition-all focus:border-[#C8913A] focus:shadow-[0_0_0_2px_rgba(200,145,58,0.2)]';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!dob) return;
    // Store birth data for the preview page and post-sign-up chart creation
    sessionStorage.setItem('josi-birth-data', JSON.stringify({ name, dob, tob, place }));
    window.location.href = '/chart-preview';
  };

  return (
    <form onSubmit={handleSubmit}>
      <div
        className="rounded-2xl p-8 max-w-md mx-auto"
        style={{
          background: 'rgba(17,24,40,0.25)',
          border: '1px solid rgba(200,145,58,0.12)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <h3 className="text-xl font-display mb-6 text-center" style={{ color: '#D4DAE6' }}>
          Reveal Your Cosmic Story
        </h3>
        <div className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="Your name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={inputClass}
            style={inputStyle}
          />
          <input
            type="date"
            value={dob}
            onChange={(e) => setDob(e.target.value)}
            className={inputClass}
            style={inputStyle}
          />
          <input
            type="time"
            placeholder="Time of birth"
            value={tob}
            onChange={(e) => setTob(e.target.value)}
            className={inputClass}
            style={inputStyle}
          />
          <PlaceAutocomplete
            value={place}
            onChange={setPlace}
            placeholder="City, Country"
            className={inputClass}
            style={inputStyle}
          />
        </div>
        <p className="text-xs mt-3 mb-5 text-center" style={{ color: '#3A4A6A' }}>
          Birth time affects house positions. If unknown, we&rsquo;ll use sunrise.
        </p>
        <button
          type="submit"
          className="w-full rounded-xl px-8 py-3 font-semibold transition-all hover:opacity-90"
          style={{ background: '#C8913A', color: '#060A14' }}
        >
          Reveal Your Cosmic Story &rarr;
        </button>
      </div>
      <p className="text-xs text-center mt-4" style={{ color: '#3A4A6A' }}>
        Free. No account required. Swiss Ephemeris precision.
      </p>
    </form>
  );
}
