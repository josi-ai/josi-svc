'use client';

import React from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { AvatarUser } from '@/components/ui/avatar';
import { useAuth } from '@/contexts/AuthContext';
import UserDropdown from '@/components/layout/user-dropdown';

const navLinks = [
  { label: 'Home', path: '/dashboard' },
  { label: 'Charts', path: '/charts' },
  { label: 'AI Insights', path: '/ai' },
  { label: 'Compatibility', path: '/compatibility' },
  { label: 'Transits', path: '/transits' },
  { label: 'Panchang', path: '/panchang' },
  { label: 'Astrologers', path: '/consultations' },
];

export default function AppTopNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user } = useAuth();

  const displayName = user?.full_name || user?.email || 'User';
  const initials = displayName.charAt(0).toUpperCase();

  return (
    <div className="flex items-center justify-between border-b border-subtle bg-surface px-10 py-3.5">
      <span className="font-display text-2xl text-text-primary">Josi</span>

      <nav className="flex gap-8">
        {navLinks.map((link) => {
          const isActive =
            pathname === link.path || pathname.startsWith(link.path + '/');
          return (
            <button
              key={link.path}
              onClick={() => router.push(link.path)}
              className={cn(
                'text-[13px] font-medium transition-colors',
                isActive ? 'text-text-primary' : 'text-text-muted hover:text-text-secondary',
              )}
            >
              {link.label}
            </button>
          );
        })}
      </nav>

      <div className="flex items-center gap-3">
        <Badge variant="plan">MYSTIC</Badge>
        <UserDropdown initials={initials} />
      </div>
    </div>
  );
}
