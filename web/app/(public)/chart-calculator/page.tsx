'use client';

import { Typography, Card, Button, Space } from 'antd';
import { CalculatorOutlined, StarOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function ChartCalculatorPage() {
  return (
    <div
      style={{
        maxWidth: 720,
        margin: '0 auto',
        padding: '60px 24px',
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <CalculatorOutlined
          style={{ fontSize: 40, color: '#6B5CE7', marginBottom: 16 }}
        />
        <Title level={2} style={{ color: '#fff', marginBottom: 8 }}>
          Birth Chart Calculator
        </Title>
        <Paragraph style={{ color: 'rgba(255,255,255,0.55)', fontSize: 16 }}>
          Enter your birth details to generate a precise chart across multiple traditions
        </Paragraph>
      </div>

      <Card
        bordered={false}
        style={{
          background: '#1a1230',
          borderRadius: 16,
          border: '1px solid rgba(107, 92, 231, 0.12)',
        }}
        styles={{ body: { padding: 40, textAlign: 'center' } }}
      >
        <StarOutlined
          style={{ fontSize: 48, color: 'rgba(107, 92, 231, 0.3)', marginBottom: 24 }}
        />
        <Paragraph style={{ color: 'rgba(255,255,255,0.45)', fontSize: 15 }}>
          Birth chart form coming soon — date, time, and place inputs with
          multi-tradition calculation options.
        </Paragraph>
        <Space style={{ marginTop: 16 }}>
          <Button
            type="primary"
            disabled
            style={{
              background: '#6B5CE7',
              borderColor: '#6B5CE7',
              borderRadius: 8,
            }}
          >
            Calculate Chart
          </Button>
        </Space>
      </Card>
    </div>
  );
}
