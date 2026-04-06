'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import PlaceAutocomplete from '@/components/ui/place-autocomplete';
import type { PersonFormData } from '@/types/api';

export function ProfileFormModal({
  mode,
  initialData,
  onClose,
  onSubmit,
  isSubmitting,
  error,
}: {
  mode: 'add' | 'edit';
  initialData: PersonFormData;
  onClose: () => void;
  onSubmit: (data: PersonFormData) => void;
  isSubmitting: boolean;
  error: string;
}) {
  const [name, setName] = useState(initialData.name);
  const [dateOfBirth, setDateOfBirth] = useState(initialData.date_of_birth);
  const [timeOfBirth, setTimeOfBirth] = useState(initialData.time_of_birth);
  const [placeOfBirth, setPlaceOfBirth] = useState(initialData.place_of_birth);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      name,
      date_of_birth: dateOfBirth,
      time_of_birth: timeOfBirth,
      place_of_birth: placeOfBirth,
    });
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: 10,
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '1.5px',
    color: 'var(--text-faint)',
    marginBottom: 6,
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '10px 14px',
    fontSize: 14,
    color: 'var(--text-primary)',
    background: 'var(--background)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    outline: 'none',
    transition: 'border-color 0.2s',
    boxSizing: 'border-box',
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: 24,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: 14,
          padding: '20px 24px',
          maxWidth: 520,
          width: '100%',
          maxHeight: '80vh',
          overflowY: 'auto',
          animation: 'fadeIn 0.2s ease-out',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 16,
          }}
        >
          <h3
            className="font-display"
            style={{
              fontSize: 20,
              color: 'var(--text-primary)',
              fontWeight: 400,
            }}
          >
            {mode === 'add' ? 'Add Birth Profile' : 'Edit Profile'}
          </h3>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 4,
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <X style={{ width: 20, height: 20 }} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* Name */}
            <div>
              <label style={labelStyle}>Name *</label>
              <input
                type="text"
                required
                placeholder="Enter name (e.g., John Doe)"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={inputStyle}
                onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              />
            </div>

            {/* Date of Birth */}
            <div>
              <label style={labelStyle}>Date of Birth *</label>
              <input
                type="date"
                required
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                style={inputStyle}
                onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              />
            </div>

            {/* Time of Birth */}
            <div>
              <label style={labelStyle}>Time of Birth</label>
              <input
                type="time"
                value={timeOfBirth}
                onChange={(e) => setTimeOfBirth(e.target.value)}
                style={inputStyle}
                onFocus={(e) => (e.target.style.borderColor = 'var(--gold)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--border)')}
              />
              <p
                style={{
                  fontSize: 12,
                  color: 'var(--text-faint)',
                  marginTop: 6,
                  lineHeight: 1.4,
                }}
              >
                Birth time affects house positions. Leave empty if unknown.
              </p>
            </div>

            {/* Place of Birth */}
            <div>
              <label style={labelStyle}>Place of Birth</label>
              <PlaceAutocomplete
                value={placeOfBirth}
                onChange={setPlaceOfBirth}
                placeholder="City, Country"
                className=""
                style={inputStyle}
              />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div
              style={{
                marginTop: 20,
                padding: '10px 14px',
                borderRadius: 8,
                fontSize: 13,
                color: 'var(--red)',
                background: 'rgba(229,72,77,0.08)',
                border: '1px solid rgba(229,72,77,0.2)',
              }}
            >
              {error}
            </div>
          )}

          {/* Buttons */}
          <div
            style={{
              display: 'flex',
              gap: 12,
              marginTop: 24,
              justifyContent: 'flex-end',
            }}
          >
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 500,
                background: 'var(--background)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border)',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !name || !dateOfBirth}
              style={{
                padding: '10px 24px',
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 600,
                background:
                  isSubmitting || !name || !dateOfBirth
                    ? 'var(--gold-bright)'
                    : 'var(--gold)',
                color: 'var(--btn-add-text, #060A14)',
                border: 'none',
                cursor:
                  isSubmitting || !name || !dateOfBirth
                    ? 'not-allowed'
                    : 'pointer',
                opacity: isSubmitting || !name || !dateOfBirth ? 0.7 : 1,
                transition: 'opacity 0.2s, background 0.2s',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
              }}
            >
              {isSubmitting ? (
                <>
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    style={{ animation: 'spin 1s linear infinite' }}
                  >
                    <circle
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeDasharray="31.42 31.42"
                    />
                  </svg>
                  {mode === 'add' ? 'Creating...' : 'Saving...'}
                </>
              ) : mode === 'add' ? (
                'Create Profile'
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
