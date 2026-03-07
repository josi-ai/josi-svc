import React from 'react';
import {
  DashboardOutlined,
  RadarChartOutlined,
  UserOutlined,
  HeartOutlined,
  RetweetOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  BulbOutlined,
  MedicineBoxOutlined,
  TeamOutlined,
  RobotOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';

type MenuItem = Required<MenuProps>['items'][number];

export interface SidebarMenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  path: string;
}

export const sidebarMenuItems: SidebarMenuItem[] = [
  // Main
  { key: 'dashboard', icon: React.createElement(DashboardOutlined), label: 'Dashboard', path: '/dashboard' },

  // Astrology
  { key: 'charts', icon: React.createElement(RadarChartOutlined), label: 'Charts', path: '/charts' },
  { key: 'persons', icon: React.createElement(UserOutlined), label: 'Profiles', path: '/persons' },
  { key: 'compatibility', icon: React.createElement(HeartOutlined), label: 'Compatibility', path: '/compatibility' },
  { key: 'transits', icon: React.createElement(RetweetOutlined), label: 'Transits', path: '/transits' },
  { key: 'dasha', icon: React.createElement(ClockCircleOutlined), label: 'Dasha', path: '/dasha' },
  { key: 'panchang', icon: React.createElement(CalendarOutlined), label: 'Panchang', path: '/panchang' },
  { key: 'predictions', icon: React.createElement(BulbOutlined), label: 'Predictions', path: '/predictions' },
  { key: 'remedies', icon: React.createElement(MedicineBoxOutlined), label: 'Remedies', path: '/remedies' },

  // Services
  { key: 'consultations', icon: React.createElement(TeamOutlined), label: 'Consultations', path: '/consultations' },
  { key: 'ai', icon: React.createElement(RobotOutlined), label: 'AI Insights', path: '/ai' },

  // Settings
  { key: 'settings', icon: React.createElement(SettingOutlined), label: 'Settings', path: '/settings' },
];

export function getMenuItems(): MenuItem[] {
  return [
    { type: 'group', label: 'Main', children: toAntdItems(sidebarMenuItems.slice(0, 1)) },
    { type: 'group', label: 'Astrology', children: toAntdItems(sidebarMenuItems.slice(1, 9)) },
    { type: 'group', label: 'Services', children: toAntdItems(sidebarMenuItems.slice(9, 11)) },
    { type: 'group', label: 'Settings', children: toAntdItems(sidebarMenuItems.slice(11)) },
  ];
}

function toAntdItems(items: SidebarMenuItem[]): MenuItem[] {
  return items.map((item) => ({
    key: item.key,
    icon: item.icon,
    label: item.label,
  }));
}
