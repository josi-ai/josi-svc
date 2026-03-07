'use client';

import { Typography, Card } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function DashaPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <ClockCircleOutlined style={{ marginRight: 10, color: '#E78A5C' }} />
        Dasha Timeline
      </Title>

      <Card
        bordered={false}
        style={{
          background: '#231845',
          borderRadius: 12,
          border: '1px solid rgba(107, 92, 231, 0.1)',
        }}
        styles={{ body: { padding: 40, textAlign: 'center' } }}
      >
        <ClockCircleOutlined style={{ fontSize: 40, color: 'rgba(231, 138, 92, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          Explore your Vimshottari Dasha periods — major, sub, and sub-sub levels.
          Understand the planetary time cycles shaping your life. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
