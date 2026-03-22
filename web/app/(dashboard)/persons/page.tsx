'use client';

import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export default function PersonsPage() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-display text-display-md text-text-primary mb-1">Birth Profiles</h3>
          <p className="text-sm text-text-muted">Manage saved birth profiles</p>
        </div>
        <Button><Plus className="h-4 w-4" /> Add Profile</Button>
      </div>
      <div className="flex flex-col items-center justify-center rounded-2xl border border-border bg-card py-16 text-center">
        <p className="text-sm text-text-muted mb-4">No profiles yet. Add a birth profile to get started.</p>
        <Button variant="outline">Add your first profile</Button>
      </div>
    </div>
  );
}
