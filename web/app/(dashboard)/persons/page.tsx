'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Plus } from 'lucide-react';
import type { Person, PersonFormData } from '@/types/api';
import { extractTimeValue } from './_components/person-helpers';
import { ProfileFormModal } from './_components/person-form-modal';
import {
  LoadingGrid,
  EmptyState,
  DeleteConfirmDialog,
  PersonGrid,
} from './_components/person-list';

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
      return {
        name: editingPerson.name,
        date_of_birth: editingPerson.date_of_birth || '',
        time_of_birth: extractTimeValue(editingPerson.time_of_birth),
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
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
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
        <PersonGrid
          persons={persons}
          onEdit={handleOpenEdit}
          onDelete={setDeletingPerson}
        />
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
