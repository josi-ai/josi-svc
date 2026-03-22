import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { Star } from 'lucide-react';

export default function ConsultationsPage() {
  return (
    <ComingSoonCard
      title="Consultations"
      description="Book video, chat, and voice consultations with verified professional astrologers. AI-powered session summaries included. Coming soon."
      icon={Star}
    />
  );
}
