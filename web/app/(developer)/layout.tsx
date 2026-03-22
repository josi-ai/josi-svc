'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Code, Key, FileText } from 'lucide-react';

const menuItems = [
  { key: '/developer', icon: Code, label: 'Overview' },
  { key: '/developer/keys', icon: Key, label: 'API Keys' },
  { key: '/developer/docs', icon: FileText, label: 'Documentation' },
];

export default function DeveloperLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="w-60 border-r border-subtle bg-surface pt-6">
        <div className="mb-8 px-6">
          <Link href="/" className="font-display text-xl text-text-primary no-underline">
            Josi
          </Link>
          <span className="mt-1 block text-[11px] uppercase tracking-widest text-text-faint">
            Developer Portal
          </span>
        </div>
        <nav className="px-2.5">
          {menuItems.map((item) => {
            const isActive = pathname === item.key;
            return (
              <Link
                key={item.key}
                href={item.key}
                className={cn(
                  'flex items-center gap-2.5 rounded-lg px-3 py-2 mb-px text-[13px] no-underline transition-colors',
                  isActive
                    ? 'bg-card text-text-primary'
                    : 'text-text-muted hover:bg-card hover:text-text-secondary',
                )}
              >
                <item.icon className="h-4 w-4 opacity-70" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
