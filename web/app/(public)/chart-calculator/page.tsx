'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Calculator, Star } from 'lucide-react';

export default function ChartCalculatorPage() {
  return (
    <div className="mx-auto max-w-[720px] px-6 py-16">
      <div className="mb-10 text-center">
        <Calculator className="mx-auto mb-4 h-10 w-10 text-gold" />
        <h2 className="font-display text-display-lg text-text-primary mb-2">
          Birth Chart Calculator
        </h2>
        <p className="text-base text-text-muted">
          Enter your birth details to generate a precise chart across multiple traditions
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center py-16 text-center">
          <Star className="mb-6 h-12 w-12 text-text-faint" />
          <p className="mb-4 text-[15px] text-text-muted">
            Birth chart form coming soon — date, time, and place inputs with
            multi-tradition calculation options.
          </p>
          <Button disabled>Calculate Chart</Button>
        </CardContent>
      </Card>
    </div>
  );
}
