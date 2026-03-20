'use client';

import React from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { AvatarUser } from '@/components/ui/avatar';
import { useAuth } from '@/contexts/AuthContext';
import {
  sidebarMenuItems,
  sidebarGroups,
  type SidebarMenuItem,
} from '@/config/sidebar-config';

/** Hardcoded counter placeholders until real data flows in */
const counterValues: Record<string, string> = {
  charts: '12',
  ai: '7',
  consultations: '1',
};

interface AppSidebarProps {
  collapsed?: boolean;
}

function NavItem({
  item,
  isActive,
  collapsed,
  onClick,
}: {
  item: SidebarMenuItem;
  isActive: boolean;
  collapsed: boolean;
  onClick: () => void;
}) {
  const Icon = item.icon;
  const counter = counterValues[item.key];

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
        fontWeight: isActive ? 'var(--sb-active-weight)' as React.CSSProperties['fontWeight'] : 'normal',
        color: isActive ? 'var(--sb-text-active)' : 'var(--sb-text)',
        transition: 'all 0.2s',
        textAlign: 'left',
        fontFamily: 'inherit',
        justifyContent: collapsed ? 'center' : 'flex-start',
      }}
      onMouseEnter={(e) => {
        if (!isActive) {
          e.currentTarget.style.background = 'var(--sb-hover-bg)';
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          e.currentTarget.style.background = 'transparent';
        }
      }}
    >
      <Icon
        size={16}
        style={{
          color: `var(${item.iconColorVar})`,
          flexShrink: 0,
        }}
      />
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

export default function AppSidebar({ collapsed = false }: AppSidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user } = useAuth();

  const allItems = Object.values(sidebarMenuItems);
  const activeKey = allItems.find(
    (item) => pathname === item.path || pathname.startsWith(item.path + '/'),
  )?.key;

  const displayName = user?.full_name || user?.email || 'User';
  const initials = displayName.charAt(0).toUpperCase();

  return (
    <aside
      style={{
        background: 'var(--sb-bg)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        width: collapsed ? 60 : 240,
        transition: 'width 0.2s ease',
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

      {/* Header */}
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
        <span
          className="font-display"
          style={{
            fontSize: 22,
            color: 'var(--sb-text)',
          }}
        >
          {collapsed ? 'J' : 'Josi'}
        </span>
        {!collapsed && (
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
        )}
      </div>

      {/* Navigation */}
      <nav
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: collapsed ? '12px 6px' : '12px 10px',
          position: 'relative',
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

      {/* Footer */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: collapsed ? '14px 10px' : '14px 16px',
          borderTop: '1px solid var(--sb-border)',
          position: 'relative',
          zIndex: 1,
          justifyContent: collapsed ? 'center' : 'flex-start',
        }}
      >
        <AvatarUser size="sm" initials={initials} />
        {!collapsed && (
          <div>
            <div style={{ fontSize: 12, color: 'var(--sb-text)' }}>{displayName}</div>
            <div style={{ fontSize: 10, color: 'var(--sb-text-muted)' }}>Mystic Plan</div>
          </div>
        )}
      </div>
    </aside>
  );
}
