import { clsx } from 'clsx';
import type { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: boolean;
}

export function Card({ className, padding = true, children, ...props }: CardProps) {
  return (
    <div
      className={clsx(
        'border border-border bg-bg-elevated',
        padding && 'p-6',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
