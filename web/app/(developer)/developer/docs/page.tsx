'use client';

import { Typography, Card } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function APIDocsPage() {
  return (
    <div>
      <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
        <FileTextOutlined style={{ marginRight: 10, color: '#6B5CE7' }} />
        API Documentation
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
        <FileTextOutlined style={{ fontSize: 40, color: 'rgba(107, 92, 231, 0.3)', marginBottom: 16 }} />
        <Paragraph style={{ color: 'rgba(255,255,255,0.4)' }}>
          Interactive API documentation with endpoint references, request/response examples,
          and code snippets for all six astrological traditions. Coming soon.
        </Paragraph>
      </Card>
    </div>
  );
}
