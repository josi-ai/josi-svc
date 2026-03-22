import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { Sparkles } from 'lucide-react';

export default function AIInsightsPage() {
  return (
    <ComingSoonCard
      title="AI Insights"
      description="LLM-powered chart interpretations across five styles. Neural Pathway Questions use your placements to generate personalized self-reflection prompts. Coming soon."
      icon={Sparkles}
    />
  );
}
