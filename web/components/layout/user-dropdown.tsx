'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';
import { AvatarUser } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { useAuth } from '@/contexts/AuthContext';
import {
  User,
  Star,
  Key,
  Settings,
  LogOut,
  PanelLeft,
  PanelTop,
  Sun,
  Moon,
  Monitor,
  ChevronUp,
} from 'lucide-react';

interface UserDropdownProps {
  initials: string;
  variant?: 'header' | 'sidebar';
  collapsed?: boolean;
}

export default function UserDropdown({ initials, variant = 'header', collapsed = false }: UserDropdownProps) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();

  const displayName = user?.full_name || user?.email || 'User';
  const email = user?.email || '';

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open]);

  const isSidebar = variant === 'sidebar';

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger */}
      {isSidebar ? (
        <button
          onClick={() => setOpen(!open)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: collapsed ? '14px 10px' : '14px 16px',
            width: '100%',
            border: 'none',
            background: open ? 'var(--sb-hover-bg)' : 'transparent',
            cursor: 'pointer',
            transition: 'background 0.2s',
            justifyContent: collapsed ? 'center' : 'flex-start',
            fontFamily: 'inherit',
          }}
          onMouseEnter={(e) => { if (!open) e.currentTarget.style.background = 'var(--sb-hover-bg)'; }}
          onMouseLeave={(e) => { if (!open) e.currentTarget.style.background = 'transparent'; }}
        >
          <AvatarUser size="sm" initials={initials} />
          {!collapsed && (
            <>
              <div style={{ flex: 1, textAlign: 'left' }}>
                <div style={{ fontSize: 12, color: 'var(--sb-text)', fontWeight: 500 }}>{displayName}</div>
                <div style={{ fontSize: 10, color: 'var(--sb-text-muted, var(--sb-group-color))' }}>Mystic Plan</div>
              </div>
              <ChevronUp
                size={14}
                style={{
                  color: 'var(--sb-text-muted, var(--sb-group-color))',
                  transition: 'transform 0.2s',
                  transform: open ? 'rotate(0deg)' : 'rotate(180deg)',
                }}
              />
            </>
          )}
        </button>
      ) : (
        <button
          onClick={() => setOpen(!open)}
          className={cn(
            'flex items-center justify-center rounded-full border-2 transition-all',
            open
              ? 'border-gold shadow-[0_0_0_3px_var(--gold-bg)]'
              : 'border-gold/40 hover:border-gold',
          )}
        >
          <AvatarUser size="md" initials={initials} />
        </button>
      )}

      {/* Dropdown panel */}
      {open && (
        <div
          className={cn(
            'absolute z-50 w-80 overflow-hidden rounded-2xl border shadow-dropdown',
            isSidebar ? 'bottom-full left-0 mb-2' : 'right-0 top-[calc(100%+8px)]',
          )}
          style={{
            borderColor: 'var(--border)',
            background: 'var(--card)',
          }}
        >
          {/* User info */}
          <div className="flex items-center gap-3.5 p-5" style={{ borderBottom: '1px solid var(--border-divider)' }}>
            <AvatarUser size="lg" initials={initials} />
            <div>
              <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{displayName}</div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{email}</div>
              <span
                className="mt-1 inline-block rounded-lg px-1.5 py-0.5 text-[9px] font-bold"
                style={{ background: 'var(--gold-bg)', color: 'var(--gold-bright)' }}
              >
                MYSTIC PLAN
              </span>
            </div>
          </div>

          {/* Theme preference */}
          <div className="px-5 pt-3.5 pb-1.5">
            <div className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: 'var(--text-faint)' }}>Theme</div>
          </div>
          <div className="flex gap-2.5 px-5 pb-4">
            <ThemeOption icon={<Sun className="h-4 w-4" />} label="Light" selected={theme === 'light'} onClick={() => setTheme('light')} />
            <ThemeOption icon={<Moon className="h-4 w-4" />} label="Dark" selected={theme === 'dark'} onClick={() => setTheme('dark')} />
            <ThemeOption icon={<Monitor className="h-4 w-4" />} label="Auto" selected={theme === 'system'} onClick={() => setTheme('system')} />
          </div>

          {/* Menu items */}
          <div className="p-1.5" style={{ borderTop: '1px solid var(--border-divider)' }}>
            <MenuItem icon={<User />} label="Edit Profile" onClick={() => { router.push('/settings/profile'); setOpen(false); }} />
            <MenuItem icon={<Star />} label="Subscription" badge="Mystic" onClick={() => { router.push('/settings'); setOpen(false); }} />
            <MenuItem icon={<Key />} label="API Keys" onClick={() => { router.push('/developer/keys'); setOpen(false); }} />
            <MenuItem icon={<Settings />} label="Settings" onClick={() => { router.push('/settings'); setOpen(false); }} />
            <Separator className="my-1 mx-3" />
            <MenuItem icon={<LogOut />} label="Sign Out" danger onClick={() => { logout(); setOpen(false); }} />
          </div>
        </div>
      )}
    </div>
  );
}

function ThemeOption({ icon, label, selected, onClick }: { icon: React.ReactNode; label: string; selected?: boolean; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex flex-1 flex-col items-center gap-2 rounded-xl border-2 p-3 transition-all"
      style={{
        borderColor: selected ? 'var(--gold)' : 'var(--border)',
        background: selected ? 'var(--gold-bg-subtle)' : 'transparent',
      }}
    >
      <span style={{ opacity: selected ? 1 : 0.6, color: selected ? 'var(--gold)' : 'inherit' }}>{icon}</span>
      <span className="text-[11px] font-semibold" style={{ color: selected ? 'var(--gold-bright)' : 'var(--text-secondary)' }}>
        {label}
      </span>
    </button>
  );
}

function MenuItem({
  icon,
  label,
  badge,
  danger,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  badge?: string;
  danger?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-[13px] transition-colors"
      style={{
        color: danger ? 'var(--red)' : 'var(--text-secondary)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = danger ? 'rgba(196,80,60,0.08)' : 'var(--card-hover)';
        if (!danger) e.currentTarget.style.color = 'var(--text-primary)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'transparent';
        if (!danger) e.currentTarget.style.color = 'var(--text-secondary)';
      }}
    >
      <span className="h-4 w-4 opacity-70 [&>svg]:h-4 [&>svg]:w-4">{icon}</span>
      <span className="flex-1 text-left">{label}</span>
      {badge && (
        <span className="rounded-lg px-2 py-0.5 text-[10px] font-semibold" style={{ background: 'var(--gold-bg)', color: 'var(--gold-bright)' }}>
          {badge}
        </span>
      )}
    </button>
  );
}
