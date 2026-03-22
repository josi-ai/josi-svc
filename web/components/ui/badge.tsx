import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-[var(--gold-bg)] text-gold-bright',
        blue: 'bg-[var(--blue-bg)] text-blue',
        green: 'bg-[var(--green-bg)] text-green',
        destructive: 'bg-destructive/10 text-destructive',
        outline: 'border border-border text-text-secondary',
        plan: 'bg-[var(--gold-bg)] text-gold-bright text-[9px] font-bold tracking-wide uppercase',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
