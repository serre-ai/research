import { clsx } from 'clsx';

type BadgeVariant = 'default' | 'outline' | 'success' | 'warning' | 'error';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-bg-elevated text-text-secondary border-border',
  outline: 'border-border-strong text-text-secondary',
  success: 'bg-[--color-status-ok-muted] text-[--color-status-ok] border-[--color-status-ok-border]',
  warning: 'bg-[--color-status-warn-muted] text-[--color-status-warn] border-[--color-status-warn-border]',
  error: 'bg-[--color-status-error-muted] text-[--color-status-error] border-[--color-status-error-border]',
};

export function Badge({ variant = 'default', className, children }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center border px-2 py-0.5 font-mono text-xs font-medium',
        variantStyles[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
