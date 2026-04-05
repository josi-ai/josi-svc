'use client';

import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input, Textarea } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Plus, Copy, Trash2, RefreshCw, Key } from 'lucide-react';

interface ApiKeyResponse {
  api_key_id: string;
  key_prefix: string;
  name: string;
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

interface ApiKeyCreatedResponse {
  api_key_id: string;
  key: string;
  key_prefix: string;
  name: string;
}

type Toast = { message: string; type: 'success' | 'error' } | null;

export default function ApiKeysPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [confirmAction, setConfirmAction] = useState<{
    label: string;
    onConfirm: () => void;
  } | null>(null);
  const [toast, setToast] = useState<Toast>(null);
  const queryClient = useQueryClient();

  const showToast = useCallback((message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const { data: keys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiClient.get<ApiKeyResponse[]>('/api/v1/api-keys'),
  });

  const createMutation = useMutation({
    mutationFn: (name: string) =>
      apiClient.post<ApiKeyCreatedResponse>('/api/v1/api-keys', { name }),
    onSuccess: (data) => {
      setCreatedKey(data.data?.key ?? '');
      setNewKeyName('');
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      showToast('API key created');
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (keyId: string) => apiClient.delete(`/api/v1/api-keys/${keyId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      showToast('API key revoked');
    },
  });

  const rotateMutation = useMutation({
    mutationFn: (keyId: string) =>
      apiClient.post<ApiKeyCreatedResponse>(`/api/v1/api-keys/${keyId}/rotate`),
    onSuccess: (data) => {
      setCreatedKey(data.data?.key ?? '');
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      showToast('API key rotated');
    },
  });

  const closeCreateModal = () => {
    setIsCreateOpen(false);
    setCreatedKey(null);
    setNewKeyName('');
  };

  const keysList = keys?.data || [];

  return (
    <div>
      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-4 z-[60] animate-in fade-in slide-in-from-top-2">
          <div
            className={`rounded-xl border px-4 py-2.5 text-sm shadow-lg ${
              toast.type === 'success'
                ? 'border-green/20 bg-green/10 text-green'
                : 'border-red/20 bg-red/10 text-red'
            }`}
          >
            {toast.message}
          </div>
        </div>
      )}

      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <h3 className="font-display text-display-md text-text-primary">API Keys</h3>
        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus className="h-4 w-4" /> Create API Key
        </Button>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-16 text-sm text-text-muted">
              Loading…
            </div>
          ) : keysList.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Key className="mb-4 h-10 w-10 text-text-faint" />
              <p className="text-sm text-text-muted">
                No API keys yet. Create one to get started.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-divider text-left">
                    <th className="px-5 py-3 font-medium text-text-muted">Name</th>
                    <th className="px-5 py-3 font-medium text-text-muted">Key</th>
                    <th className="px-5 py-3 font-medium text-text-muted">Created</th>
                    <th className="px-5 py-3 font-medium text-text-muted">Last Used</th>
                    <th className="px-5 py-3 font-medium text-text-muted">Status</th>
                    <th className="px-5 py-3 font-medium text-text-muted text-right">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {keysList.map((row) => (
                    <tr
                      key={row.api_key_id}
                      className="border-b border-divider last:border-0 hover:bg-surface-hover transition-colors"
                    >
                      <td className="px-5 py-3 text-text-primary">{row.name}</td>
                      <td className="px-5 py-3">
                        <code className="rounded bg-surface-raised px-2 py-0.5 text-xs text-text-secondary">
                          {row.key_prefix}…************************
                        </code>
                      </td>
                      <td className="px-5 py-3 text-text-secondary">
                        {new Date(row.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-5 py-3 text-text-secondary">
                        {row.last_used_at
                          ? new Date(row.last_used_at).toLocaleDateString()
                          : 'Never'}
                      </td>
                      <td className="px-5 py-3">
                        <Badge variant={row.is_active ? 'green' : 'destructive'}>
                          {row.is_active ? 'Active' : 'Revoked'}
                        </Badge>
                      </td>
                      <td className="px-5 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              setConfirmAction({
                                label: `Rotate "${row.name}"?`,
                                onConfirm: () => rotateMutation.mutate(row.api_key_id),
                              })
                            }
                          >
                            <RefreshCw className="h-3.5 w-3.5" /> Rotate
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red hover:text-red"
                            onClick={() =>
                              setConfirmAction({
                                label: `Revoke "${row.name}"? This cannot be undone.`,
                                onConfirm: () => revokeMutation.mutate(row.api_key_id),
                              })
                            }
                          >
                            <Trash2 className="h-3.5 w-3.5" /> Revoke
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Key Dialog */}
      <Dialog open={isCreateOpen} onClose={closeCreateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{createdKey ? 'Key Created' : 'Create API Key'}</DialogTitle>
          </DialogHeader>

          {createdKey ? (
            <div className="space-y-4">
              <p className="text-sm text-amber-400">
                Copy this key now. You will not be able to see it again.
              </p>
              <Textarea
                value={createdKey}
                readOnly
                className="font-mono text-xs"
              />
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  navigator.clipboard.writeText(createdKey);
                  showToast('Copied to clipboard');
                }}
              >
                <Copy className="h-4 w-4" /> Copy to Clipboard
              </Button>
            </div>
          ) : (
            <Input
              placeholder="Key name (e.g., Production, Staging)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && newKeyName.trim()) {
                  createMutation.mutate(newKeyName);
                }
              }}
              autoFocus
            />
          )}

          <DialogFooter>
            {createdKey ? (
              <Button onClick={closeCreateModal}>Done</Button>
            ) : (
              <>
                <Button variant="ghost" onClick={() => setIsCreateOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => createMutation.mutate(newKeyName)}
                  disabled={!newKeyName.trim() || createMutation.isPending}
                >
                  {createMutation.isPending ? 'Creating…' : 'Create'}
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Confirm Dialog */}
      <Dialog
        open={!!confirmAction}
        onClose={() => setConfirmAction(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-text-secondary">{confirmAction?.label}</p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setConfirmAction(null)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                confirmAction?.onConfirm();
                setConfirmAction(null);
              }}
            >
              Confirm
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
