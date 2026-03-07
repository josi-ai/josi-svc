'use client';

import { Layout, Menu, Typography } from 'antd';
import { CodeOutlined, KeyOutlined, FileTextOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const { Sider, Content } = Layout;
const { Text } = Typography;

const menuItems = [
  { key: '/developer', icon: <CodeOutlined />, label: <Link href="/developer">Overview</Link> },
  { key: '/developer/keys', icon: <KeyOutlined />, label: <Link href="/developer/keys">API Keys</Link> },
  { key: '/developer/docs', icon: <FileTextOutlined />, label: <Link href="/developer/docs">Documentation</Link> },
];

export default function DeveloperLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <Layout style={{ minHeight: '100vh', background: '#0f0a1e' }}>
      <Sider
        width={240}
        style={{
          background: '#1a1230',
          borderRight: '1px solid rgba(107, 92, 231, 0.1)',
          paddingTop: 24,
        }}
      >
        <div style={{ padding: '0 24px', marginBottom: 32 }}>
          <Link href="/" style={{ textDecoration: 'none' }}>
            <Text
              strong
              style={{
                fontSize: 20,
                background: 'linear-gradient(135deg, #6B5CE7, #E78A5C)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Josi
            </Text>
          </Link>
          <Text
            style={{
              display: 'block',
              fontSize: 11,
              letterSpacing: 1.5,
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.3)',
              marginTop: 4,
            }}
          >
            Developer Portal
          </Text>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[pathname]}
          style={{ background: 'transparent', borderInlineEnd: 'none' }}
          items={menuItems}
        />
      </Sider>
      <Content style={{ padding: 32 }}>{children}</Content>
    </Layout>
  );
}
