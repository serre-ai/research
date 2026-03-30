import { clsx } from 'clsx';

type TuiDotStatus = 'ok' | 'warn' | 'error' | 'idle';

interface TuiStatusDotProps {
  status: TuiDotStatus;
  className?: string;
}

const DOT_CHARS: Record<TuiDotStatus, string> = {
  ok: '●',
  warn: '●',
  error: '✗',
  idle: '○',
};

/**
 * Terminal-style status indicator: ● ○ ✗
 */
export function TuiStatusDot({ status, className }: TuiStatusDotProps) {
  return (
    <span className={clsx('tui-dot', `tui-dot--${status}`, className)} aria-label={status}>
      {DOT_CHARS[status]}
    </span>
  );
}
