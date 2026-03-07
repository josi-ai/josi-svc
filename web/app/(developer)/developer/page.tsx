'use client';

import { Typography, Card, Row, Col, Statistic } from 'antd';
import { ApiOutlined, KeyOutlined, CheckCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const stats = [
  { title: 'API Calls (30d)', value: 0, icon: <ApiOutlined style={{ color: '#6B5CE7' }} /> },
  { title: 'Active Keys', value: 0, icon: <KeyOutlined style={{ color: '#E78A5C' }} /> },
  { title: 'Status', value: 'Active', icon: <CheckCircleOutlined style={{ color: '#52c41a' }} /> },
];

export default function DeveloperPortalPage() {
  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <Title level={3} style={{ color: '#fff', marginBottom: 4 }}>
          <ApiOutlined style={{ marginRight: 10, color: '#6B5CE7' }} />
          API Developer Portal
        </Title>
        <Text style={{ color: 'rgba(255,255,255,0.4)' }}>
          Manage your API keys, monitor usage, and explore documentation
        </Text>
      </div>

      <Row gutter={[20, 20]}>
        {stats.map((s) => (
          <Col xs={24} sm={8} key={s.title}>
            <Card
              bordered={false}
              style={{
                background: '#231845',
                borderRadius: 12,
                border: '1px solid rgba(107, 92, 231, 0.1)',
              }}
              styles={{ body: { padding: 20 } }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Statistic
                  title={<Text style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13 }}>{s.title}</Text>}
                  value={s.value}
                  valueStyle={{ color: '#fff', fontSize: 28 }}
                />
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 10,
                    background: 'rgba(107, 92, 231, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 20,
                  }}
                >
                  {s.icon}
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
