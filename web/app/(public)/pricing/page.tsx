'use client';

import { Typography, Card, Button, Col, Row, Space } from 'antd';
import { CheckOutlined, CrownOutlined } from '@ant-design/icons';
import Link from 'next/link';

const { Title, Paragraph, Text } = Typography;

const tiers = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    features: ['3 birth charts', 'Basic Vedic & Western', 'Community access'],
    cta: 'Get Started',
    highlight: false,
  },
  {
    name: 'Explorer',
    price: '$9.99',
    period: '/month',
    features: [
      '25 birth charts',
      'All 6 traditions',
      '10 AI readings/month',
      'Dasha & transit reports',
    ],
    cta: 'Start Exploring',
    highlight: false,
  },
  {
    name: 'Mystic',
    price: '$19.99',
    period: '/month',
    features: [
      'Unlimited charts',
      'Unlimited AI readings',
      '2 consultations/month',
      'Compatibility analysis',
      'Neural Pathway Questions',
    ],
    cta: 'Go Mystic',
    highlight: true,
  },
  {
    name: 'Master',
    price: '$39.99',
    period: '/month',
    features: [
      'Everything in Mystic',
      '5 consultations/month',
      'Priority astrologer matching',
      'API access',
      'Custom chart exports',
    ],
    cta: 'Unlock Mastery',
    highlight: false,
  },
];

export default function PricingPage() {
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '60px 24px 120px' }}>
      <div style={{ textAlign: 'center', marginBottom: 56 }}>
        <CrownOutlined style={{ fontSize: 36, color: '#E78A5C', marginBottom: 12 }} />
        <Title level={2} style={{ color: '#fff', marginBottom: 8 }}>
          Choose Your Plan
        </Title>
        <Paragraph style={{ color: 'rgba(255,255,255,0.5)', fontSize: 16 }}>
          From casual exploration to mastery — find the tier that fits your journey
        </Paragraph>
      </div>

      <Row gutter={[24, 24]} justify="center">
        {tiers.map((tier) => (
          <Col xs={24} sm={12} lg={6} key={tier.name}>
            <Card
              bordered={false}
              style={{
                background: tier.highlight ? '#231845' : '#1a1230',
                borderRadius: 16,
                height: '100%',
                border: tier.highlight
                  ? '1px solid rgba(107, 92, 231, 0.4)'
                  : '1px solid rgba(107, 92, 231, 0.1)',
                ...(tier.highlight
                  ? { boxShadow: '0 0 40px rgba(107, 92, 231, 0.15)' }
                  : {}),
              }}
              styles={{ body: { padding: 28 } }}
            >
              {tier.highlight && (
                <Text
                  style={{
                    display: 'block',
                    fontSize: 11,
                    letterSpacing: 2,
                    textTransform: 'uppercase',
                    color: '#E78A5C',
                    marginBottom: 8,
                    fontWeight: 600,
                  }}
                >
                  Most Popular
                </Text>
              )}
              <Title level={4} style={{ color: '#fff', marginBottom: 4 }}>
                {tier.name}
              </Title>
              <div style={{ marginBottom: 20 }}>
                <Text style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
                  {tier.price}
                </Text>
                <Text style={{ color: 'rgba(255,255,255,0.4)', marginLeft: 4 }}>
                  {tier.period}
                </Text>
              </div>
              <Space direction="vertical" size={10} style={{ width: '100%', marginBottom: 24 }}>
                {tier.features.map((f) => (
                  <div key={f} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <CheckOutlined style={{ color: '#6B5CE7', marginTop: 4, flexShrink: 0 }} />
                    <Text style={{ color: 'rgba(255,255,255,0.65)', fontSize: 13 }}>{f}</Text>
                  </div>
                ))}
              </Space>
              <Link href="/auth/login">
                <Button
                  type={tier.highlight ? 'primary' : 'default'}
                  block
                  style={{
                    borderRadius: 8,
                    height: 40,
                    ...(tier.highlight
                      ? { background: '#6B5CE7', borderColor: '#6B5CE7' }
                      : {
                          background: 'transparent',
                          borderColor: 'rgba(107, 92, 231, 0.3)',
                          color: '#fff',
                        }),
                  }}
                >
                  {tier.cta}
                </Button>
              </Link>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
