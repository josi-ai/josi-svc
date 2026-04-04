'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { AvatarUser } from '@/components/ui/avatar';
import { useAuth } from '@/contexts/AuthContext';
import { PanelLeftClose, PanelLeftOpen, ChevronRight } from 'lucide-react';
import UserDropdown from '@/components/layout/user-dropdown';
import {
  sidebarMenuItems,
  sidebarGroups,
  type SidebarMenuItem,
} from '@/config/sidebar-config';

// TODO: Replace with real data from API
const counterValues: Record<string, string> = {
  charts: '12',
  ai: '7',
  consultations: '1',
};

interface AppSidebarProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

function NavItem({
  item,
  isActive,
  collapsed,
  onClick,
  mounted,
}: {
  item: SidebarMenuItem;
  isActive: boolean;
  collapsed: boolean;
  onClick: () => void;
  mounted: boolean;
}) {
  const Icon = item.icon;
  const counter = mounted ? counterValues[item.key] : undefined;

  return (
    <button
      onClick={onClick}
      title={collapsed ? item.label : undefined}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '8px 10px',
        marginBottom: 1,
        fontSize: 13,
        cursor: 'pointer',
        width: '100%',
        border: 'none',
        borderRadius: 7,
        borderLeft: isActive ? '3px solid var(--gold)' : '3px solid transparent',
        background: isActive ? 'var(--sb-active-bg)' : 'transparent',
        fontWeight: isActive ? ('var(--sb-active-weight)' as React.CSSProperties['fontWeight']) : 'normal',
        color: isActive ? 'var(--sb-text-active)' : 'var(--sb-text)',
        transition: 'all 0.2s',
        textAlign: 'left',
        fontFamily: 'inherit',
        justifyContent: collapsed ? 'center' : 'flex-start',
      }}
      onMouseEnter={(e) => {
        if (!isActive) e.currentTarget.style.background = 'var(--sb-hover-bg)';
      }}
      onMouseLeave={(e) => {
        if (!isActive) e.currentTarget.style.background = 'transparent';
      }}
    >
      <Icon size={16} style={{ color: `var(${item.iconColorVar})`, flexShrink: 0 }} />
      {!collapsed && (
        <>
          <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>
          {counter && item.counterColorBgVar && item.counterColorTextVar && (
            <span
              style={{
                marginLeft: 'auto',
                fontSize: 10,
                padding: '2px 7px',
                borderRadius: 8,
                fontWeight: 600,
                background: `var(${item.counterColorBgVar})`,
                color: `var(${item.counterColorTextVar})`,
              }}
            >
              {counter}
            </span>
          )}
        </>
      )}
    </button>
  );
}

export default function AppSidebar({ collapsed = false, onToggleCollapse }: AppSidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user } = useAuth();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const allItems = Object.values(sidebarMenuItems);
  const activeKey = allItems.find(
    (item) => pathname === item.path || pathname.startsWith(item.path + '/'),
  )?.key;

  const displayName = user?.full_name || user?.email || 'User';
  const initials = displayName.charAt(0).toUpperCase();

  return (
    <aside
      suppressHydrationWarning
      style={{
        background: 'var(--sb-bg)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        position: 'relative',
        overflow: 'visible',
      }}
    >
      {/* Gold top accent line */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 2,
          background: 'var(--sb-top-line)',
          zIndex: 2,
          pointerEvents: 'none',
        }}
      />

      {/* Header: Logo + MYSTIC + Collapse toggle */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          padding: collapsed ? '20px 10px 16px' : '20px 20px 16px',
          borderBottom: '1px solid var(--sb-border)',
          position: 'relative',
          zIndex: 1,
        }}
      >
        {!collapsed ? (
          <>
            <span className="font-display" style={{ fontSize: 22, color: 'var(--sb-text)' }}>
              Josi
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Badge
                variant="plan"
                style={{
                  background: 'rgba(200,145,58,0.12)',
                  color: '#C8913A',
                  border: '1px solid rgba(200,145,58,0.3)',
                }}
              >
                MYSTIC
              </Badge>
              <button
                onClick={onToggleCollapse}
                title="Collapse sidebar"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 24,
                  height: 24,
                  borderRadius: 6,
                  border: 'none',
                  background: 'transparent',
                  color: 'var(--sb-text-muted, var(--sb-text))',
                  cursor: 'pointer',
                  transition: 'color 0.2s',
                }}
              >
                <PanelLeftClose size={14} />
              </button>
            </div>
          </>
        ) : (
          <button
            onClick={onToggleCollapse}
            title="Expand sidebar"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 28,
              height: 28,
              borderRadius: 6,
              border: 'none',
              background: 'transparent',
              color: 'var(--sb-text)',
              cursor: 'pointer',
            }}
          >
            <PanelLeftOpen size={16} />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav
        suppressHydrationWarning
        style={{
          flexGrow: 1,
          flexShrink: 1,
          flexBasis: '0%',
          minHeight: 0,
          overflowY: 'auto' as const,
          padding: collapsed ? '12px 6px' : '12px 10px',
          position: 'relative' as const,
          zIndex: 1,
        }}
      >
        {sidebarGroups.map((group, groupIdx) => (
          <React.Fragment key={group.label}>
            {!collapsed && (
              <div
                style={{
                  fontSize: 9,
                  textTransform: 'uppercase',
                  letterSpacing: '1.5px',
                  fontWeight: 600,
                  padding: '10px 10px 5px',
                  color: 'var(--sb-group-color)',
                }}
              >
                {group.label}
              </div>
            )}
            {group.items.map((item) => (
              <NavItem
                key={item.key}
                item={item}
                isActive={activeKey === item.key}
                collapsed={collapsed}
                mounted={mounted}
                onClick={() => router.push(item.path)}
              />
            ))}
            {groupIdx < sidebarGroups.length - 1 && (
              <div
                style={{
                  height: 1,
                  margin: collapsed ? '4px 6px' : '4px 16px',
                  background: 'var(--sb-divider)',
                }}
              />
            )}
          </React.Fragment>
        ))}
      </nav>

      {/* Footer: User dropdown (replaces header avatar) */}
      <div
        style={{
          borderTop: '1px solid var(--sb-border)',
          position: 'relative',
          zIndex: 50,
        }}
      >
        <UserDropdown
          initials={initials}
          variant="sidebar"
          collapsed={collapsed}
        />
      </div>
    </aside>
  );
}
