'use client';

import React from 'react';
import { Breadcrumb, Dropdown, Avatar, Badge, Space, type MenuProps } from 'antd';
import { BellOutlined, UserOutlined, SettingOutlined, LogoutOutlined } from '@ant-design/icons';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function DashboardHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const breadcrumbItems = pathname
    .split('/')
    .filter(Boolean)
    .map((segment, index, arr) => ({
      title: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
      href: index < arr.length - 1 ? '/' + arr.slice(0, index + 1).join('/') : undefined,
    }));

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => router.push('/settings/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => router.push('/settings'),
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
      onClick: logout,
    },
  ];

  const displayName = user?.name || user?.email || 'User';

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        height: '100%',
      }}
    >
      <Breadcrumb
        items={[{ title: 'Home', href: '/dashboard' }, ...breadcrumbItems]}
        style={{ color: 'rgba(255,255,255,0.65)' }}
      />
      <Space size={16}>
        <Badge count={0} size="small">
          <BellOutlined style={{ fontSize: 18, color: 'rgba(255,255,255,0.65)', cursor: 'pointer' }} />
        </Badge>
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" trigger={['click']}>
          <Space style={{ cursor: 'pointer' }}>
            <Avatar
              size={32}
              icon={<UserOutlined />}
              style={{ backgroundColor: '#6B5CE7' }}
            />
            <span style={{ color: 'rgba(255,255,255,0.87)', fontSize: 14 }}>
              {displayName}
            </span>
          </Space>
        </Dropdown>
      </Space>
    </div>
  );
}
