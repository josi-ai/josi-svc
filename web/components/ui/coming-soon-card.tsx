import { Card, CardContent } from '@/components/ui/card';
import { type LucideIcon } from 'lucide-react';

interface ComingSoonCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

export function ComingSoonCard({ title, description, icon: Icon }: ComingSoonCardProps) {
  return (
    <div>
      <h3 className="font-display text-display-md text-text-primary mb-6">{title}</h3>
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--gold-bg)] mb-6">
            <Icon className="h-7 w-7 text-gold" />
          </div>
          <p className="text-sm text-text-muted max-w-md">{description}</p>
        </CardContent>
      </Card>
    </div>
  );
}
