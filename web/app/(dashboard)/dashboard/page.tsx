'use client';

import { Typography, Card, Row, Col, Statistic, Button, Space } from 'antd';
import {
  PieChartOutlined,
  RobotOutlined,
  VideoCameraOutlined,
  StarOutlined,
  PlusOutlined,
  SearchOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

const stats = [
  { title: 'Charts Created', value: 0, icon: <PieChartOutlined style={{ color: '#6B5CE7' }} /> },
  { title: 'AI Readings', value: 0, icon: <RobotOutlined style={{ color: '#E78A5C' }} /> },
  { title: 'Consultations', value: 0, icon: <VideoCameraOutlined style={{ color: '#6B5CE7' }} /> },
  { title: 'Plan', value: 'Free', icon: <StarOutlined style={{ color: '#E78A5C' }} /> },
];

export default function DashboardPage() {
  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <Title level={3} style={{ color: '#fff', marginBottom: 4 }}>
          Welcome back
        </Title>
        <Text style={{ color: 'rgba(255,255,255,0.45)' }}>
          Here&apos;s an overview of your cosmic journey
        </Text>
      </div>

      <Row gutter={[20, 20]} style={{ marginBottom: 36 }}>
        {stats.map((s) => (
          <Col xs={24} sm={12} lg={6} key={s.title}>
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

      <Title level={5} style={{ color: 'rgba(255,255,255,0.7)', marginBottom: 16 }}>
        Quick Actions
      </Title>
      <Space size={12} wrap>
        <Button
          icon={<PlusOutlined />}
          style={{
            background: '#6B5CE7',
            borderColor: '#6B5CE7',
            color: '#fff',
            borderRadius: 8,
            height: 40,
          }}
        >
          New Chart
        </Button>
        <Button
          icon={<SearchOutlined />}
          style={{
            background: 'transparent',
            borderColor: 'rgba(107, 92, 231, 0.3)',
            color: '#fff',
            borderRadius: 8,
            height: 40,
          }}
        >
          Find Astrologer
        </Button>
        <Button
          icon={<BulbOutlined />}
          style={{
            background: 'transparent',
            borderColor: 'rgba(231, 138, 92, 0.3)',
            color: '#fff',
            borderRadius: 8,
            height: 40,
          }}
        >
          AI Reading
        </Button>
      </Space>
    </div>
  );
}
