'use client';

import { Plus, User } from 'lucide-react';
import type { Person } from '@/types/api';
import { ProfileCard } from './person-card';

/* ---------- Loading Skeleton ---------- */

export function LoadingGrid() {
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

export function EmptyState({ onAdd }: { onAdd: () => void }) {
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

export function DeleteConfirmDialog({
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
              background: 'var(--red)',
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

/* ---------- Person Grid ---------- */

export function PersonGrid({
  persons,
  onEdit,
  onDelete,
}: {
  persons: Person[];
  onEdit: (person: Person) => void;
  onDelete: (person: Person) => void;
}) {
  return (
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
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
