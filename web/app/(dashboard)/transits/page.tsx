'use client';

import { Typography, Card } from 'antd';
import { SwapOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function TransitsPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <SwapOutlined style={{ marginRight: 10, color: '#6B5CE7' }} />
        Current Transits
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
        <SwapOutlined style={{ fontSize: 40, color: 'rgba(107, 92, 231, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          Track planetary transits over your natal chart. See how current sky positions
          activate your birth placements. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
