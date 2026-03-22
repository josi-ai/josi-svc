import { ComingSoonCard } from '@/components/ui/coming-soon-card';
import { FileText } from 'lucide-react';

export default function APIDocsPage() {
  return (
    <ComingSoonCard
      title="API Documentation"
      description="Interactive API documentation with endpoint references, request/response examples, and code snippets for all six astrological traditions. Coming soon."
      icon={FileText}
    />
  );
}
