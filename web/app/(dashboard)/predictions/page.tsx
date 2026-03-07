'use client';

import { Typography, Card } from 'antd';
import { EyeOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function PredictionsPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <EyeOutlined style={{ marginRight: 10, color: '#E78A5C' }} />
        Predictions
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
        <EyeOutlined style={{ fontSize: 40, color: 'rgba(231, 138, 92, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          AI-generated predictions based on your dasha periods, transits, and natal chart.
          Personalized forecasts for career, relationships, and wellbeing. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
