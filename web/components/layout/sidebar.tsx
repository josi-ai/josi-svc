'use client';

import React from 'react';
import { Menu } from 'antd';
import { usePathname, useRouter } from 'next/navigation';
import { getMenuItems, sidebarMenuItems } from '@/config/sidebar-config';

interface SidebarProps {
  collapsed: boolean;
}

export default function Sidebar({ collapsed }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();

  const activeKey = sidebarMenuItems.find(
    (item) => pathname === item.path || pathname.startsWith(item.path + '/'),
  )?.key;

  const handleMenuClick = ({ key }: { key: string }) => {
    const item = sidebarMenuItems.find((i) => i.key === key);
    if (item) {
      router.push(item.path);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #2d2060',
        }}
      >
        <span
          className="cosmic-glow-text"
          style={{
            fontSize: collapsed ? 20 : 28,
            fontWeight: 700,
            color: '#6B5CE7',
            letterSpacing: '0.05em',
            transition: 'font-size 0.2s',
          }}
        >
          {collapsed ? 'J' : 'Josi'}
        </span>
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={activeKey ? [activeKey] : []}
        items={getMenuItems()}
        onClick={handleMenuClick}
        style={{ background: 'transparent', borderRight: 'none', flex: 1 }}
      />
    </div>
  );
}
