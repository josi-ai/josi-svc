import * as React from 'react';
import { cn } from '@/lib/utils';

const Avatar = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { size?: 'sm' | 'md' | 'lg' | 'xl' }
>(({ className, size = 'md', ...props }, ref) => {
  const sizes = {
    sm: 'h-[30px] w-[30px] text-[11px]',
    md: 'h-8 w-8 text-[11px]',
    lg: 'h-[42px] w-[42px] text-base',
    xl: 'h-12 w-12 text-lg',
  };

  return (
    <div
      ref={ref}
      className={cn(
        'relative flex shrink-0 items-center justify-center rounded-full font-bold',
        sizes[size],
        className,
      )}
      {...props}
    />
  );
});
Avatar.displayName = 'Avatar';

const AvatarUser = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    size?: 'sm' | 'md' | 'lg' | 'xl';
    initials: string;
  }
>(({ className, size = 'md', initials, ...props }, ref) => {
  return (
    <Avatar
      ref={ref}
      size={size}
      className={cn(className)}
      style={{
        background: 'linear-gradient(135deg, var(--gold), var(--gold-bright, var(--gold)))',
        color: 'var(--avatar-text)',
        ...props.style,
      }}
      {...props}
    >
      {initials}
    </Avatar>
  );
});
AvatarUser.displayName = 'AvatarUser';

const AvatarPlaceholder = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    size?: 'sm' | 'md' | 'lg' | 'xl';
    initials: string;
  }
>(({ className, size = 'lg', initials, ...props }, ref) => {
  return (
    <Avatar
      ref={ref}
      size={size}
      className={cn(
        'bg-gradient-to-br from-border to-border-strong font-display text-text-primary',
        className,
      )}
      {...props}
    >
      {initials}
    </Avatar>
  );
});
AvatarPlaceholder.displayName = 'AvatarPlaceholder';

export { Avatar, AvatarUser, AvatarPlaceholder };
