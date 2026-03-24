import { clsx } from 'clsx';

interface TuiSkeletonProps {
  width?: number;      // character count
  className?: string;
}

/**
 * Terminal-style loading placeholder: ░░░░░░░░░░
 */
export function TuiSkeleton({ width = 16, className }: TuiSkeletonProps) {
  return (
    <span className={clsx('tui-skeleton', className)} aria-label="loading">
      {'░'.repeat(width)}
    </span>
  );
}
