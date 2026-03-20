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
} from 'lucide-react';

interface UserDropdownProps {
  initials: string;
}

export default function UserDropdown({ initials }: UserDropdownProps) {
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

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className={cn(
          'flex items-center justify-center rounded-full border-2 transition-all',
          open
            ? 'border-gold shadow-[0_0_0_3px_var(--gold-bg)]'
            : 'border-transparent hover:border-gold',
        )}
      >
        <AvatarUser size="md" initials={initials} />
      </button>

      {open && (
        <div className="absolute right-0 top-[calc(100%+8px)] z-50 w-80 animate-in fade-in slide-in-from-top-1 overflow-hidden rounded-2xl border border-border bg-card shadow-dropdown">
          {/* User info */}
          <div className="flex items-center gap-3.5 border-b border-divider p-5">
            <AvatarUser size="lg" initials={initials} />
            <div>
              <div className="text-sm font-semibold text-text-primary">{displayName}</div>
              <div className="text-xs text-text-muted">{email}</div>
              <span className="mt-1 inline-block rounded-lg bg-[var(--gold-bg)] px-1.5 py-0.5 text-[9px] font-bold text-gold-bright">
                MYSTIC PLAN
              </span>
            </div>
          </div>

          {/* Layout preference */}
          <div className="px-5 pt-3.5 pb-1.5">
            <div className="text-label font-semibold uppercase text-text-faint">Navigation Layout</div>
          </div>
          <div className="flex gap-2.5 px-5 pb-4">
            <LayoutOption icon={<PanelLeft className="h-4 w-4" />} label="Side Nav" selected />
            <LayoutOption icon={<PanelTop className="h-4 w-4" />} label="Top Nav" />
          </div>

          {/* Theme preference */}
          <div className="px-5 pt-0 pb-1.5">
            <div className="text-label font-semibold uppercase text-text-faint">Theme</div>
          </div>
          <div className="flex gap-2.5 px-5 pb-4">
            <ThemeOption icon={<Sun className="h-4 w-4" />} label="Light" selected={theme === 'light'} onClick={() => setTheme('light')} />
            <ThemeOption icon={<Moon className="h-4 w-4" />} label="Dark" selected={theme === 'dark'} onClick={() => setTheme('dark')} />
            <ThemeOption icon={<Monitor className="h-4 w-4" />} label="Auto" selected={theme === 'system'} onClick={() => setTheme('system')} />
          </div>

          {/* Menu items */}
          <div className="border-t border-divider p-1.5">
            <MenuItem icon={<User />} label="Edit Profile" onClick={() => { router.push('/settings/profile'); setOpen(false); }} />
            <MenuItem icon={<Star />} label="Subscription" badge="Mystic" onClick={() => { router.push('/settings'); setOpen(false); }} />
            <MenuItem icon={<Key />} label="API Keys" onClick={() => { router.push('/settings'); setOpen(false); }} />
            <MenuItem icon={<Settings />} label="Settings" onClick={() => { router.push('/settings'); setOpen(false); }} />
            <Separator className="my-1 mx-3" />
            <MenuItem icon={<LogOut />} label="Sign Out" danger onClick={() => { logout(); setOpen(false); }} />
          </div>
        </div>
      )}
    </div>
  );
}

function LayoutOption({ icon, label, selected }: { icon: React.ReactNode; label: string; selected?: boolean }) {
  return (
    <button
      className={cn(
        'flex flex-1 flex-col items-center gap-2 rounded-xl border-2 p-3 transition-all',
        selected
          ? 'border-gold bg-[var(--gold-bg-subtle)]'
          : 'border-border hover:border-border-strong hover:bg-card-hover',
      )}
    >
      <span className={cn('opacity-60', selected && 'text-gold opacity-100')}>{icon}</span>
      <span className={cn('text-[11px] font-semibold', selected ? 'text-gold-bright' : 'text-text-secondary')}>
        {label}
      </span>
    </button>
  );
}

function ThemeOption({ icon, label, selected, onClick }: { icon: React.ReactNode; label: string; selected?: boolean; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex flex-1 flex-col items-center gap-2 rounded-xl border-2 p-3 transition-all',
        selected
          ? 'border-gold bg-[var(--gold-bg-subtle)]'
          : 'border-border hover:border-border-strong hover:bg-card-hover',
      )}
    >
      <span className={cn('opacity-60', selected && 'text-gold opacity-100')}>{icon}</span>
      <span className={cn('text-[11px] font-semibold', selected ? 'text-gold-bright' : 'text-text-secondary')}>
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
      className={cn(
        'flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-[13px] transition-colors',
        danger
          ? 'text-red hover:bg-red/[0.08]'
          : 'text-text-secondary hover:bg-card-hover hover:text-text-primary',
      )}
    >
      <span className="h-4 w-4 opacity-70 [&>svg]:h-4 [&>svg]:w-4">{icon}</span>
      <span className="flex-1 text-left">{label}</span>
      {badge && (
        <span className="rounded-lg bg-[var(--gold-bg)] px-2 py-0.5 text-[10px] font-semibold text-gold-bright">
          {badge}
        </span>
      )}
    </button>
  );
}
