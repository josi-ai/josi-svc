'use client';

import { useState } from 'react';
import { Button, Card, Input, Table, Modal, Typography, Space, Tag, message, Popconfirm } from 'antd';
import { PlusOutlined, CopyOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

const { Title, Text, Paragraph } = Typography;

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

export default function ApiKeysPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: keys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiClient.get<ApiKeyResponse[]>('/api/v1/api-keys'),
  });

  const createMutation = useMutation({
    mutationFn: (name: string) => apiClient.post<ApiKeyCreatedResponse>('/api/v1/api-keys', { name }),
    onSuccess: (data) => {
      setCreatedKey(data.data.key);
      setNewKeyName('');
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      message.success('API key created');
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (keyId: string) => apiClient.delete(`/api/v1/api-keys/${keyId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      message.success('API key revoked');
    },
  });

  const rotateMutation = useMutation({
    mutationFn: (keyId: string) => apiClient.post<ApiKeyCreatedResponse>(`/api/v1/api-keys/${keyId}/rotate`),
    onSuccess: (data) => {
      setCreatedKey(data.data.key);
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      message.success('API key rotated');
    },
  });

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    {
      title: 'Key',
      dataIndex: 'key_prefix',
      key: 'key_prefix',
      render: (prefix: string) => <Text code>{prefix}...************************</Text>,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Last Used',
      dataIndex: 'last_used_at',
      key: 'last_used_at',
      render: (date: string | null) => date ? new Date(date).toLocaleDateString() : 'Never',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'red'}>{active ? 'Active' : 'Revoked'}</Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ApiKeyResponse) => (
        <Space>
          <Popconfirm title="Rotate this key?" onConfirm={() => rotateMutation.mutate(record.api_key_id)}>
            <Button icon={<SyncOutlined />} size="small">Rotate</Button>
          </Popconfirm>
          <Popconfirm title="Revoke this key?" onConfirm={() => revokeMutation.mutate(record.api_key_id)}>
            <Button icon={<DeleteOutlined />} size="small" danger>Revoke</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>API Keys</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsCreateOpen(true)}>
            Create API Key
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={keys?.data || []}
          loading={isLoading}
          rowKey="api_key_id"
          pagination={false}
        />

        {/* Create Key Modal */}
        <Modal
          title="Create API Key"
          open={isCreateOpen}
          onCancel={() => { setIsCreateOpen(false); setCreatedKey(null); }}
          footer={createdKey ? [
            <Button key="close" onClick={() => { setIsCreateOpen(false); setCreatedKey(null); }}>
              Done
            </Button>,
          ] : [
            <Button key="cancel" onClick={() => setIsCreateOpen(false)}>Cancel</Button>,
            <Button
              key="create"
              type="primary"
              loading={createMutation.isPending}
              onClick={() => createMutation.mutate(newKeyName)}
              disabled={!newKeyName.trim()}
            >
              Create
            </Button>,
          ]}
        >
          {createdKey ? (
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Paragraph type="warning">
                Copy this key now. You will not be able to see it again.
              </Paragraph>
              <Input.TextArea
                value={createdKey}
                readOnly
                autoSize
                style={{ fontFamily: 'monospace' }}
              />
              <Button
                icon={<CopyOutlined />}
                onClick={() => {
                  navigator.clipboard.writeText(createdKey);
                  message.success('Copied to clipboard');
                }}
              >
                Copy to Clipboard
              </Button>
            </Space>
          ) : (
            <Input
              placeholder="Key name (e.g., Production, Staging)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              onPressEnter={() => newKeyName.trim() && createMutation.mutate(newKeyName)}
            />
          )}
        </Modal>
      </Space>
    </div>
  );
}
