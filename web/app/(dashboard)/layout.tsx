'use client';

import React, { useState } from 'react';
import { Layout } from 'antd';
import Sidebar from '@/components/layout/sidebar';
import DashboardHeader from '@/components/layout/dashboard-header';

const { Sider, Header, Content } = Layout;

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={240}
        theme="dark"
        style={{
          background: '#0f0a1e',
          borderRight: '1px solid #2d2060',
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <Sidebar collapsed={collapsed} />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 240, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            padding: 0,
            background: '#1a1230',
            borderBottom: '1px solid #2d2060',
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}
        >
          <DashboardHeader />
        </Header>
        <Content
          style={{
            padding: 24,
            overflow: 'auto',
            background: '#0f0a1e',
            minHeight: 'calc(100vh - 64px)',
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
