import { clsx } from 'clsx';
import type { StatusKey } from '@/lib/constants';

interface StatusDotProps {
  status: StatusKey;
  pulse?: boolean;
  className?: string;
}

const dotColors: Record<StatusKey, string> = {
  ok: 'bg-[--color-status-ok]',
  warn: 'bg-[--color-status-warn]',
  error: 'bg-[--color-status-error]',
  idle: 'bg-[--color-status-idle]',
};

export function StatusDot({ status, pulse = false, className }: StatusDotProps) {
  return (
    <span className={clsx('relative inline-flex h-2 w-2', className)}>
      {pulse && (
        <span
          className={clsx(
            'absolute inline-flex h-full w-full animate-ping rounded-full opacity-75',
            dotColors[status],
          )}
        />
      )}
      <span className={clsx('relative inline-flex h-2 w-2 rounded-full', dotColors[status])} />
    </span>
  );
}
