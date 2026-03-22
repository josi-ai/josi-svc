import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { MoonStar } from 'lucide-react';

export default function PanchangPage() {
  return (
    <ComingSoonCard
      title="Daily Panchang"
      description="View today's Panchang — tithi, nakshatra, yoga, karana, and vara. Auspicious and inauspicious periods at a glance. Coming soon."
      icon={MoonStar}
    />
  );
}
