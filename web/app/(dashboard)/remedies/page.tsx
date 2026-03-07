'use client';

import { Typography, Card } from 'antd';
import { MedicineBoxOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function RemediesPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <MedicineBoxOutlined style={{ marginRight: 10, color: '#6B5CE7' }} />
        Remedies
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
        <MedicineBoxOutlined style={{ fontSize: 40, color: 'rgba(107, 92, 231, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          Personalized Vedic remedies — mantras, gemstones, charities, and rituals
          based on your chart&apos;s planetary strengths and afflictions. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
