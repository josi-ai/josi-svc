'use client';

import { Layout, Button, Space, Typography } from 'antd';
import Link from 'next/link';

const { Header, Content } = Layout;
const { Text } = Typography;

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <Layout style={{ minHeight: '100vh', background: '#0f0a1e' }}>
      <Header
        style={{
          background: 'transparent',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 48px',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(107, 92, 231, 0.1)',
        }}
      >
        <Link href="/" style={{ textDecoration: 'none' }}>
          <Text
            strong
            style={{
              fontSize: 24,
              background: 'linear-gradient(135deg, #6B5CE7, #E78A5C)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.5px',
            }}
          >
            Josi
          </Text>
        </Link>
        <Space size="large">
          <Link href="/chart-calculator">
            <Button type="text" style={{ color: 'rgba(255,255,255,0.75)' }}>
              Calculator
            </Button>
          </Link>
          <Link href="/pricing">
            <Button type="text" style={{ color: 'rgba(255,255,255,0.75)' }}>
              Pricing
            </Button>
          </Link>
          <Link href="/auth/login">
            <Button
              type="primary"
              style={{
                background: '#6B5CE7',
                borderColor: '#6B5CE7',
                borderRadius: 8,
              }}
            >
              Sign In
            </Button>
          </Link>
        </Space>
      </Header>
      <Content>{children}</Content>
    </Layout>
  );
}
