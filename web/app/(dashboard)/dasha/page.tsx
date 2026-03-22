import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { Clock } from 'lucide-react';

export default function DashaPage() {
  return (
    <ComingSoonCard
      title="Dasha Timeline"
      description="Explore your Vimshottari Dasha periods — major, sub, and sub-sub levels. Understand the planetary time cycles shaping your life. Coming soon."
      icon={Clock}
    />
  );
}
