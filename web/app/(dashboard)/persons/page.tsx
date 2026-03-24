'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import PlaceAutocomplete from '@/components/ui/place-autocomplete';
import {
  Plus,
  User,
  Pencil,
  Trash2,
  MapPin,
  Calendar,
  Clock,
  X,
} from 'lucide-react';
import Link from 'next/link';

/* ---------- Types ---------- */

interface Person {
  person_id: string;
  name: string;
  email: string | null;
  date_of_birth: string | null;
  time_of_birth: string | null;
  place_of_birth: string | null;
  latitude: string | number | null;
  longitude: string | number | null;
  timezone: string | null;
  gender: string | null;
  notes: string | null;
  is_default?: boolean;
  created_at: string;
  updated_at: string;
}

interface PersonFormData {
  name: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
}

/* ---------- Helpers (updated) ---------- */

function formatDateOfBirth(dateStr: string | null): string | null {
  if (!dateStr) return null;
  // dateStr is "YYYY-MM-DD"
  const [year, month, day] = dateStr.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function formatTimeOfBirth(timeStr: string | null): string | null {
  if (!timeStr) return null;
  // timeStr may be "HH:MM", "HH:MM:SS", or a full datetime string
  // Try to extract hours and minutes
  let hours: number;
  let minutes: number;
  if (timeStr.includes('T')) {
    // ISO datetime string
    const d = new Date(timeStr);
    hours = d.getHours();
    minutes = d.getMinutes();
  } else {
    const parts = timeStr.split(':');
    hours = parseInt(parts[0], 10);
    minutes = parseInt(parts[1], 10);
  }
  if (isNaN(hours) || isNaN(minutes)) return timeStr;
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const h = hours % 12 || 12;
  const m = minutes.toString().padStart(2, '0');
  return `${h}:${m} ${ampm}`;
}

/* ---------- Loading Skeleton ---------- */

function LoadingGrid() {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
        gap: 16,
      }}
    >
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          style={{
            background: 'var(--card)',
            border: '1px solid var(--border)',
            borderRadius: 14,
            padding: 24,
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div
              style={{
                height: 20,
                width: '60%',
                borderRadius: 6,
                background: 'var(--border)',
                opacity: 0.4,
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
            <div
              style={{
                height: 14,
                width: '45%',
                borderRadius: 6,
                background: 'var(--border)',
                opacity: 0.35,
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
            <div
              style={{
                height: 14,
                width: '30%',
                borderRadius: 6,
                background: 'var(--border)',
                opacity: 0.3,
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
            <div style={{ flex: 1 }} />
            <div
              style={{
                height: 12,
                width: '35%',
                borderRadius: 6,
                background: 'var(--border)',
                opacity: 0.25,
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
          </div>
        </div>
      ))}
      <style>{`@keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.2; } }`}</style>
    </div>
  );
}

/* ---------- Empty State ---------- */

function EmptyState({ onAdd }: { onAdd: () => void }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 14,
        border: '1px solid var(--border)',
        background: 'var(--card)',
        padding: '64px 24px',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 20,
          background: 'var(--gold-bg)',
        }}
      >
        <User style={{ width: 24, height: 24, color: 'var(--gold)' }} />
      </div>
      <p
        className="font-display"
        style={{
          fontSize: 18,
          color: 'var(--text-primary)',
          marginBottom: 8,
        }}
      >
        No profiles yet
      </p>
      <p
        style={{
          fontSize: 13,
          color: 'var(--text-muted)',
          marginBottom: 24,
          maxWidth: 300,
          lineHeight: 1.5,
        }}
      >
        Add a birth profile to start calculating charts
      </p>
      <button
        onClick={onAdd}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          padding: '10px 20px',
          borderRadius: 8,
          fontSize: 14,
          fontWeight: 600,
          background: 'var(--gold)',
          color: 'var(--btn-add-text)',
          border: 'none',
          cursor: 'pointer',
        }}
      >
        <Plus style={{ width: 16, height: 16 }} />
        Add Your First Profile
      </button>
    </div>
  );
}

/* ---------- Delete Confirm Dialog ---------- */

function DeleteConfirmDialog({
  personName,
  onConfirm,
  onCancel,
  isDeleting,
}: {
  personName: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDeleting: boolean;
}) {
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
        padding: 16,
      }}
      onClick={onCancel}
    >
      <div
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: 14,
          padding: 28,
          maxWidth: 420,
          width: '100%',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3
          className="font-display"
          style={{
            fontSize: 18,
            color: 'var(--text-primary)',
            marginBottom: 12,
          }}
        >
          Delete Profile
        </h3>
        <p
          style={{
            fontSize: 14,
            color: 'var(--text-secondary)',
            lineHeight: 1.5,
            marginBottom: 24,
          }}
        >
          Delete <strong>{personName}</strong>? This will also remove their
          charts.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <button
            onClick={onCancel}
            disabled={isDeleting}
            style={{
              padding: '8px 18px',
              borderRadius: 8,
              fontSize: 13,
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
            onClick={onConfirm}
            disabled={isDeleting}
            style={{
              padding: '8px 18px',
              borderRadius: 8,
              fontSize: 13,
              fontWeight: 600,
              background: '#E5484D',
              color: '#fff',
              border: 'none',
              cursor: isDeleting ? 'not-allowed' : 'pointer',
              opacity: isDeleting ? 0.7 : 1,
            }}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ---------- Profile Form Modal ---------- */

function ProfileFormModal({
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
    onSubmit({ name, date_of_birth: dateOfBirth, time_of_birth: timeOfBirth, place_of_birth: placeOfBirth });
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
        alignItems: 'flex-end',
        justifyContent: 'center',
        zIndex: 1000,
        padding: 0,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: '14px 14px 0 0',
          padding: 28,
          maxWidth: 560,
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          animation: 'slideUp 0.25s ease-out',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 24,
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
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
                color: '#E5484D',
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

/* ---------- Profile Card ---------- */

function ProfileCard({
  person,
  onEdit,
  onDelete,
}: {
  person: Person;
  onEdit: (person: Person) => void;
  onDelete: (person: Person) => void;
}) {
  const formattedDob = person.date_of_birth ? formatDateOfBirth(person.date_of_birth) : null;
  const formattedTime = person.time_of_birth ? formatTimeOfBirth(person.time_of_birth) : null;

  return (
    <div
      className="profile-card"
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 14,
        padding: 24,
        cursor: 'default',
        transition: 'all 0.2s ease',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      {/* Name + Default indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <p
          className="font-display"
          style={{
            fontSize: 18,
            color: 'var(--text-primary)',
            lineHeight: 1.3,
            margin: 0,
          }}
        >
          {person.is_default && (
            <span style={{ color: '#D4A843', marginRight: 6 }}>{'\u2605'}</span>
          )}
          {person.name}
        </p>
        {person.is_default && (
          <span
            style={{
              display: 'inline-block',
              fontSize: 9,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '1px',
              color: '#D4A843',
              background: 'rgba(212, 168, 67, 0.12)',
              border: '1px solid rgba(212, 168, 67, 0.25)',
              borderRadius: 4,
              padding: '2px 6px',
              lineHeight: 1.4,
              flexShrink: 0,
            }}
          >
            Default
          </span>
        )}
      </div>

      {/* Birth details */}
      <div
        style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}
      >
        {/* Date of Birth */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: 13,
            color: 'var(--text-secondary)',
          }}
        >
          <Calendar
            style={{
              width: 14,
              height: 14,
              color: 'var(--text-muted)',
              flexShrink: 0,
            }}
          />
          <span>{formattedDob}</span>
        </div>

        {/* Time of Birth */}
        {formattedTime && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 13,
              color: 'var(--text-secondary)',
            }}
          >
            <Clock
              style={{
                width: 14,
                height: 14,
                color: 'var(--text-muted)',
                flexShrink: 0,
              }}
            />
            <span>{formattedTime}</span>
          </div>
        )}

        {/* Place of Birth */}
        {person.place_of_birth && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 13,
              color: 'var(--text-secondary)',
            }}
          >
            <MapPin
              style={{
                width: 14,
                height: 14,
                color: 'var(--text-muted)',
                flexShrink: 0,
              }}
            />
            <span
              style={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {person.place_of_birth}
            </span>
          </div>
        )}
      </div>

      {/* Footer: View charts link + actions */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: 12,
          borderTop: '1px solid var(--border)',
          marginTop: 4,
        }}
      >
        <Link
          href={`/charts?person_id=${person.person_id}`}
          style={{
            fontSize: 12,
            color: 'var(--gold)',
            textDecoration: 'none',
            fontWeight: 500,
            transition: 'opacity 0.15s',
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLElement).style.opacity = '0.8';
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLElement).style.opacity = '1';
          }}
        >
          View charts &rarr;
        </Link>

        <div style={{ display: 'flex', gap: 4 }}>
          <button
            onClick={() => onEdit(person)}
            title="Edit profile"
            className="action-btn"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 32,
              height: 32,
              borderRadius: 8,
              border: '1px solid var(--border)',
              background: 'var(--background)',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              transition: 'all 0.15s',
            }}
          >
            <Pencil style={{ width: 14, height: 14 }} />
          </button>
          {!person.is_default && (
            <button
              onClick={() => onDelete(person)}
              title="Delete profile"
              className="action-btn action-btn-delete"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 32,
                height: 32,
                borderRadius: 8,
                border: '1px solid var(--border)',
                background: 'var(--background)',
                cursor: 'pointer',
                color: 'var(--text-muted)',
                transition: 'all 0.15s',
              }}
            >
              <Trash2 style={{ width: 14, height: 14 }} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- Main Page ---------- */

export default function PersonsPage() {
  const queryClient = useQueryClient();

  // Modal state
  const [showFormModal, setShowFormModal] = useState(false);
  const [formMode, setFormMode] = useState<'add' | 'edit'>('add');
  const [editingPerson, setEditingPerson] = useState<Person | null>(null);
  const [formError, setFormError] = useState('');

  // Delete dialog state
  const [deletingPerson, setDeletingPerson] = useState<Person | null>(null);

  // Fetch persons
  const { data: personsResponse, isLoading } = useQuery({
    queryKey: ['persons'],
    queryFn: () => apiClient.get<Person[]>('/api/v1/persons/'),
  });

  const persons = personsResponse?.data || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: PersonFormData) =>
      apiClient.post<Person>('/api/v1/persons/', {
        name: data.name,
        date_of_birth: data.date_of_birth,
        time_of_birth: data.time_of_birth || null,
        place_of_birth: data.place_of_birth || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['persons'] });
      setShowFormModal(false);
      setFormError('');
    },
    onError: (err: Error) => {
      setFormError(err.message || 'Failed to create profile.');
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: PersonFormData }) =>
      apiClient.put<Person>(`/api/v1/persons/${id}`, {
        name: data.name,
        date_of_birth: data.date_of_birth,
        time_of_birth: data.time_of_birth || null,
        place_of_birth: data.place_of_birth || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['persons'] });
      setShowFormModal(false);
      setEditingPerson(null);
      setFormError('');
    },
    onError: (err: Error) => {
      setFormError(err.message || 'Failed to update profile.');
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/v1/persons/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['persons'] });
      setDeletingPerson(null);
    },
  });

  // Handlers
  const handleOpenAdd = () => {
    setFormMode('add');
    setEditingPerson(null);
    setFormError('');
    setShowFormModal(true);
  };

  const handleOpenEdit = (person: Person) => {
    setFormMode('edit');
    setEditingPerson(person);
    setFormError('');
    setShowFormModal(true);
  };

  const handleFormSubmit = (data: PersonFormData) => {
    if (formMode === 'edit' && editingPerson) {
      updateMutation.mutate({ id: editingPerson.person_id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDeleteConfirm = () => {
    if (deletingPerson) {
      deleteMutation.mutate(deletingPerson.person_id);
    }
  };

  const getInitialFormData = (): PersonFormData => {
    if (formMode === 'edit' && editingPerson) {
      // Extract time in HH:MM format for the time input
      let timeValue = '';
      if (editingPerson.time_of_birth) {
        const t = editingPerson.time_of_birth;
        if (t.includes('T')) {
          // ISO datetime — extract time portion
          const d = new Date(t);
          timeValue = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
        } else {
          // Already HH:MM or HH:MM:SS
          timeValue = t.substring(0, 5);
        }
      }
      return {
        name: editingPerson.name,
        date_of_birth: editingPerson.date_of_birth,
        time_of_birth: timeValue,
        place_of_birth: editingPerson.place_of_birth || '',
      };
    }
    return { name: '', date_of_birth: '', time_of_birth: '', place_of_birth: '' };
  };

  return (
    <div>
      {/* Hover styles */}
      <style>{`
        .profile-card:hover {
          border-color: var(--gold) !important;
          box-shadow: 0 0 0 1px var(--gold), 0 8px 24px rgba(200,145,58,0.12) !important;
          transform: translateY(-2px);
        }
        .action-btn:hover {
          border-color: var(--gold) !important;
          color: var(--gold) !important;
        }
        .action-btn-delete:hover {
          border-color: #E5484D !important;
          color: #E5484D !important;
        }
        @keyframes slideUp {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>

      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 24,
        }}
      >
        <div>
          <h3
            className="font-display"
            style={{
              fontSize: '1.75rem',
              color: 'var(--text-primary)',
              marginBottom: 4,
            }}
          >
            Birth Profiles
          </h3>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Manage birth profiles for chart calculations
          </p>
        </div>
        <button
          onClick={handleOpenAdd}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '10px 20px',
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 600,
            background: 'var(--gold)',
            color: 'var(--btn-add-text)',
            border: 'none',
            cursor: 'pointer',
            transition: 'opacity 0.15s',
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLElement).style.opacity = '0.9';
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLElement).style.opacity = '1';
          }}
        >
          <Plus style={{ width: 16, height: 16 }} />
          Add Profile
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingGrid />
      ) : persons.length === 0 ? (
        <EmptyState onAdd={handleOpenAdd} />
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: 16,
          }}
        >
          {persons.map((person) => (
            <ProfileCard
              key={person.person_id}
              person={person}
              onEdit={handleOpenEdit}
              onDelete={setDeletingPerson}
            />
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      {showFormModal && (
        <ProfileFormModal
          key={editingPerson?.person_id || 'new'}
          mode={formMode}
          initialData={getInitialFormData()}
          onClose={() => {
            setShowFormModal(false);
            setEditingPerson(null);
            setFormError('');
          }}
          onSubmit={handleFormSubmit}
          isSubmitting={createMutation.isPending || updateMutation.isPending}
          error={formError}
        />
      )}

      {/* Delete Confirm Dialog */}
      {deletingPerson && (
        <DeleteConfirmDialog
          personName={deletingPerson.name}
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeletingPerson(null)}
          isDeleting={deleteMutation.isPending}
        />
      )}
    </div>
  );
}
