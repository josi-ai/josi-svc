import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { Pill } from 'lucide-react';

export default function RemediesPage() {
  return (
    <ComingSoonCard
      title="Remedies"
      description="Personalized Vedic remedies — mantras, gemstones, charities, and rituals based on your chart's planetary strengths and afflictions. Coming soon."
      icon={Pill}
    />
  );
}
