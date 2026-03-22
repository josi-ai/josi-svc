import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { Lightbulb } from 'lucide-react';

export default function PredictionsPage() {
  return (
    <ComingSoonCard
      title="Predictions"
      description="AI-generated predictions based on your dasha periods, transits, and natal chart. Personalized forecasts for career, relationships, and wellbeing. Coming soon."
      icon={Lightbulb}
    />
  );
}
