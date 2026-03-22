'use client';

import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export default function ChartsPage() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-display text-display-md text-text-primary mb-1">My Charts</h3>
          <p className="text-sm text-text-muted">View and manage your birth charts</p>
        </div>
        <Button><Plus className="h-4 w-4" /> Create New Chart</Button>
      </div>
      <div className="flex flex-col items-center justify-center rounded-2xl border border-border bg-card py-16 text-center">
        <p className="text-sm text-text-muted mb-4">No charts yet. Create your first birth chart to get started.</p>
        <Button variant="outline">Create your first chart</Button>
      </div>
    </div>
  );
}
