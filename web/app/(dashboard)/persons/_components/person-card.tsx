'use client';

import Link from 'next/link';
import { Pencil, Trash2, MapPin, Calendar, Clock } from 'lucide-react';
import type { Person } from '@/types/api';
import { formatDateOfBirth, formatTimeOfBirth } from './person-helpers';

export function ProfileCard({
  person,
  onEdit,
  onDelete,
}: {
  person: Person;
  onEdit: (person: Person) => void;
  onDelete: (person: Person) => void;
}) {
  const formattedDob = person.date_of_birth
    ? formatDateOfBirth(person.date_of_birth)
    : null;
  const formattedTime = person.time_of_birth
    ? formatTimeOfBirth(person.time_of_birth)
    : null;

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
            <span style={{ color: 'var(--gold-bright)', marginRight: 6 }}>{'\u2605'}</span>
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
              color: 'var(--gold-bright)',
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
