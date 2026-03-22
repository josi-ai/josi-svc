'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Plug, Key, CheckCircle } from 'lucide-react';

const stats = [
  { title: 'API Calls (30d)', value: '0', icon: Plug, color: 'text-gold' },
  { title: 'Active Keys', value: '0', icon: Key, color: 'text-gold-bright' },
  { title: 'Status', value: 'Active', icon: CheckCircle, color: 'text-green' },
];

export default function DeveloperPortalPage() {
  return (
    <div>
      <div className="mb-8">
        <h3 className="font-display text-display-md text-text-primary mb-1">API Developer Portal</h3>
        <p className="text-sm text-text-muted">Manage your API keys, monitor usage, and explore documentation</p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        {stats.map((s) => (
          <Card key={s.title}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[13px] text-text-muted mb-1">{s.title}</p>
                  <p className="font-display text-display-md text-text-primary">{s.value}</p>
                </div>
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--gold-bg)]">
                  <s.icon className={`h-5 w-5 ${s.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
