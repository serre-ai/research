import { clsx } from 'clsx';
import type { StatusKey } from '@/lib/constants';

interface StatusBadgeProps {
  status: StatusKey;
  children: React.ReactNode;
  className?: string;
}

const statusStyles: Record<StatusKey, string> = {
  ok: 'bg-[--color-status-ok-muted] text-[--color-status-ok] border-[--color-status-ok-border]',
  warn: 'bg-[--color-status-warn-muted] text-[--color-status-warn] border-[--color-status-warn-border]',
  error: 'bg-[--color-status-error-muted] text-[--color-status-error] border-[--color-status-error-border]',
  idle: 'bg-[--color-status-idle-muted] text-[--color-status-idle] border-[--color-status-idle-border]',
};

export function StatusBadge({ status, className, children }: StatusBadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center border px-2 py-0.5 font-mono text-xs font-medium',
        statusStyles[status],
        className,
      )}
    >
      {children}
    </span>
  );
}
