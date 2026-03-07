'use client';

import { Typography, Button, Empty } from 'antd';
import { UserOutlined, PlusOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export default function PersonsPage() {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
        <div>
          <Title level={3} style={{ color: '#fff', marginBottom: 4 }}>
            <UserOutlined style={{ marginRight: 10, color: '#6B5CE7' }} />
            Birth Profiles
          </Title>
          <Text style={{ color: 'rgba(255,255,255,0.4)' }}>
            Manage saved birth profiles
          </Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          style={{ background: '#6B5CE7', borderColor: '#6B5CE7', borderRadius: 8 }}
        >
          Add Profile
        </Button>
      </div>

      <div
        style={{
          background: '#231845',
          borderRadius: 12,
          border: '1px solid rgba(107, 92, 231, 0.1)',
          padding: '60px 24px',
          textAlign: 'center',
        }}
      >
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <Text style={{ color: 'rgba(255,255,255,0.4)' }}>
              No profiles yet. Add a birth profile to get started.
            </Text>
          }
        />
      </div>
    </div>
  );
}
