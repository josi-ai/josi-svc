import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { RefreshCw } from 'lucide-react';

export default function TransitsPage() {
  return (
    <ComingSoonCard
      title="Current Transits"
      description="Track planetary transits over your natal chart. See how current sky positions activate your birth placements. Coming soon."
      icon={RefreshCw}
    />
  );
}
