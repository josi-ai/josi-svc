'use client';

import { Typography, Card } from 'antd';
import { VideoCameraOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function ConsultationsPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <VideoCameraOutlined style={{ marginRight: 10, color: '#E78A5C' }} />
        Consultations
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
        <VideoCameraOutlined style={{ fontSize: 40, color: 'rgba(231, 138, 92, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          Book video, chat, and voice consultations with verified professional astrologers.
          AI-powered session summaries included. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
