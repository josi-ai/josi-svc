'use client';

import { Typography, Card } from 'antd';
import { RobotOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function AIInsightsPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <RobotOutlined style={{ marginRight: 10, color: '#6B5CE7' }} />
        AI Insights
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
        <RobotOutlined style={{ fontSize: 40, color: 'rgba(107, 92, 231, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          LLM-powered chart interpretations across five styles. Neural Pathway Questions
          use your placements to generate personalized self-reflection prompts. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
