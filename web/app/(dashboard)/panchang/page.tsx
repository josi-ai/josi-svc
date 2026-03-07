'use client';

import { Typography, Card } from 'antd';
import { CalendarOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function PanchangPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <CalendarOutlined style={{ marginRight: 10, color: '#6B5CE7' }} />
        Daily Panchang
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
        <CalendarOutlined style={{ fontSize: 40, color: 'rgba(107, 92, 231, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          View today&apos;s Panchang — tithi, nakshatra, yoga, karana, and vara.
          Auspicious and inauspicious periods at a glance. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
