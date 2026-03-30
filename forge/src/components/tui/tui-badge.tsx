import { clsx } from 'clsx';

type TuiBadgeColor = 'ok' | 'warn' | 'error' | 'muted' | 'accent';

interface TuiBadgeProps {
  color?: TuiBadgeColor;
  className?: string;
  children: React.ReactNode;
}

/**
 * Terminal-style badge: [STATUS]
 */
export function TuiBadge({ color = 'muted', className, children }: TuiBadgeProps) {
  return (
    <span className={clsx('tui-badge', `tui-badge--${color}`, className)}>
      [{children}]
    </span>
  );
}
