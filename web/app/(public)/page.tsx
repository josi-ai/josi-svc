'use client';

import { Button, Card, Col, Row, Typography } from 'antd';
import {
  GlobalOutlined,
  RobotOutlined,
  TeamOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';
import Link from 'next/link';

const { Title, Paragraph, Text } = Typography;

const features = [
  {
    icon: <GlobalOutlined style={{ fontSize: 36, color: '#6B5CE7' }} />,
    title: '6 Traditions',
    description:
      'Vedic, Western, Chinese, Hellenistic, Mayan, and Celtic astrology — all calculated with precision using Swiss Ephemeris.',
  },
  {
    icon: <RobotOutlined style={{ fontSize: 36, color: '#E78A5C' }} />,
    title: 'AI Guidance',
    description:
      'LLM-powered interpretations transform chart data into personalized guidance with Neural Pathway self-reflection prompts.',
  },
  {
    icon: <TeamOutlined style={{ fontSize: 36, color: '#6B5CE7' }} />,
    title: 'Expert Consultations',
    description:
      'Connect with verified professional astrologers for video, chat, and voice consultations with AI-powered summaries.',
  },
];

export default function LandingPage() {
  return (
    <div style={{ background: '#0f0a1e' }}>
      {/* Hero Section */}
      <section
        style={{
          position: 'relative',
          minHeight: '80vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: '80px 24px',
          overflow: 'hidden',
        }}
      >
        {/* Radial gradient background */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(107, 92, 231, 0.15) 0%, rgba(231, 138, 92, 0.05) 50%, transparent 80%)',
            pointerEvents: 'none',
          }}
        />

        <div style={{ position: 'relative', maxWidth: 720 }}>
          <Text
            style={{
              display: 'block',
              fontSize: 14,
              letterSpacing: 3,
              textTransform: 'uppercase',
              color: '#E78A5C',
              marginBottom: 16,
            }}
          >
            Multi-Tradition Astrology Platform
          </Text>
          <Title
            level={1}
            style={{
              fontSize: 56,
              fontWeight: 700,
              lineHeight: 1.1,
              margin: 0,
              marginBottom: 24,
              background: 'linear-gradient(135deg, #ffffff 0%, #c4b5fd 50%, #E78A5C 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Discover Your Cosmic Blueprint
          </Title>
          <Paragraph
            style={{
              fontSize: 18,
              color: 'rgba(255, 255, 255, 0.6)',
              maxWidth: 540,
              margin: '0 auto 40px',
              lineHeight: 1.7,
            }}
          >
            Explore birth charts across six astrological traditions, receive AI-powered
            interpretations, and connect with expert astrologers — all in one platform.
          </Paragraph>
          <Link href="/chart-calculator">
            <Button
              type="primary"
              size="large"
              icon={<ArrowRightOutlined />}
              style={{
                height: 52,
                paddingInline: 36,
                fontSize: 16,
                fontWeight: 600,
                borderRadius: 12,
                background: 'linear-gradient(135deg, #6B5CE7 0%, #8B7CF7 100%)',
                border: 'none',
                boxShadow: '0 0 32px rgba(107, 92, 231, 0.4)',
              }}
            >
              Calculate Your Birth Chart
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '0 24px 120px' }}>
        <Row gutter={[32, 32]}>
          {features.map((feature) => (
            <Col xs={24} md={8} key={feature.title}>
              <Card
                bordered={false}
                style={{
                  background: '#1a1230',
                  borderRadius: 16,
                  height: '100%',
                  border: '1px solid rgba(107, 92, 231, 0.12)',
                }}
                styles={{ body: { padding: 32 } }}
              >
                <div style={{ marginBottom: 20 }}>{feature.icon}</div>
                <Title level={4} style={{ color: '#fff', marginBottom: 12 }}>
                  {feature.title}
                </Title>
                <Paragraph style={{ color: 'rgba(255,255,255,0.55)', margin: 0, lineHeight: 1.7 }}>
                  {feature.description}
                </Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      </section>
    </div>
  );
}
