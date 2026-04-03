import {
  LayoutDashboard,
  CircleDot,
  Users,
  Heart,
  RefreshCw,
  Clock,
  MoonStar,
  Star,
  Sparkles,
  Settings,
  MessageSquare,
  Calendar,
  type LucideIcon,
} from 'lucide-react';

export interface SidebarMenuItem {
  key: string;
  label: string;
  path: string;
  icon: LucideIcon;
  iconColorVar: string;
  counterColorBgVar?: string;
  counterColorTextVar?: string;
}

export interface SidebarGroup {
  label: string;
  items: SidebarMenuItem[];
}

const items: Record<string, SidebarMenuItem> = {
  dashboard: {
    key: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard,
    iconColorVar: '--ic-dashboard',
  },
  charts: {
    key: 'charts',
    label: 'Charts',
    path: '/charts',
    icon: CircleDot,
    iconColorVar: '--ic-charts',
    counterColorBgVar: '--ct-charts-bg',
    counterColorTextVar: '--ct-charts-text',
  },
  persons: {
    key: 'persons',
    label: 'Profiles',
    path: '/persons',
    icon: Users,
    iconColorVar: '--ic-charts',
  },
  ai: {
    key: 'ai',
    label: 'AI Insights',
    path: '/ai',
    icon: Sparkles,
    iconColorVar: '--ic-ai',
    counterColorBgVar: '--ct-ai-bg',
    counterColorTextVar: '--ct-ai-text',
  },
  compatibility: {
    key: 'compatibility',
    label: 'Compatibility',
    path: '/compatibility',
    icon: Heart,
    iconColorVar: '--ic-compatibility',
  },
  transits: {
    key: 'transits',
    label: 'Transits',
    path: '/transits',
    icon: RefreshCw,
    iconColorVar: '--ic-transits',
  },
  panchang: {
    key: 'panchang',
    label: 'Panchang',
    path: '/panchang',
    icon: MoonStar,
    iconColorVar: '--ic-panchang',
  },
  dasha: {
    key: 'dasha',
    label: 'Dasha',
    path: '/dasha',
    icon: Clock,
    iconColorVar: '--ic-dasha',
  },
  muhurta: {
    key: 'muhurta',
    label: 'Muhurta',
    path: '/muhurta',
    icon: Star,
    iconColorVar: '--ic-muhurta',
  },
  astrologers: {
    key: 'astrologers',
    label: 'Astrologers',
    path: '/astrologers',
    icon: Star,
    iconColorVar: '--ic-astrologers',
  },
  consultations: {
    key: 'consultations',
    label: 'Consultations',
    path: '/consultations',
    icon: MessageSquare,
    iconColorVar: '--ic-consultations',
    counterColorBgVar: '--ct-consultations-bg',
    counterColorTextVar: '--ct-consultations-text',
  },
  events: {
    key: 'events',
    label: 'Cultural Events',
    path: '/events',
    icon: Calendar,
    iconColorVar: '--ic-panchang',
  },
  settings: {
    key: 'settings',
    label: 'Settings',
    path: '/settings',
    icon: Settings,
    iconColorVar: '--ic-dashboard',
  },
};

export const sidebarMenuItems = items;

export const sidebarGroups: SidebarGroup[] = [
  {
    label: 'Overview',
    items: [items.dashboard, items.charts, items.persons, items.ai],
  },
  {
    label: 'Explore',
    items: [items.compatibility, items.transits, items.panchang, items.dasha, items.muhurta, items.events],
  },
  {
    label: 'Connect',
    items: [items.astrologers, items.consultations],
  },
];
