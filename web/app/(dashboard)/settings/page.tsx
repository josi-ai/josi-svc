import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { Settings } from 'lucide-react';

export default function SettingsPage() {
  return (
    <ComingSoonCard
      title="Settings"
      description="Account settings, subscription management, notification preferences, and default calculation options. Coming soon."
      icon={Settings}
    />
  );
}
