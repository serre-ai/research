import { clsx } from 'clsx';
import type { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  message: string;
  description?: string;
  className?: string;
  children?: React.ReactNode;
}

export function EmptyState({ icon: Icon, message, description, className, children }: EmptyStateProps) {
  return (
    <div className={clsx('flex flex-col items-center justify-center py-16 text-center', className)}>
      {Icon && <Icon className="mb-4 h-10 w-10 text-text-muted" />}
      <p className="font-mono text-sm font-medium text-text-secondary">{message}</p>
      {description && <p className="mt-1 text-sm text-text-muted">{description}</p>}
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}
