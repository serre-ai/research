import { clsx } from 'clsx';

interface TuiProgressProps {
  value: number;       // 0-100
  width?: number;      // character width of the bar (default 20)
  className?: string;
  showPercent?: boolean;
}

/**
 * Terminal-style progress bar: [████████░░░░] 62%
 */
export function TuiProgress({ value, width = 20, showPercent = true, className }: TuiProgressProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const filled = Math.round((clamped / 100) * width);
  const empty = width - filled;

  return (
    <span className={clsx('tui-progress', className)}>
      [<span className="tui-progress-fill">{'█'.repeat(filled)}</span>
      <span className="tui-progress-empty">{'░'.repeat(empty)}</span>]
      {showPercent && <span className="ml-1">{Math.round(clamped)}%</span>}
    </span>
  );
}
