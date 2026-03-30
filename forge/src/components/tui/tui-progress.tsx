import { clsx } from 'clsx';

type TuiProgressColor = 'ok' | 'warn' | 'error' | 'accent';

interface TuiProgressProps {
  value: number;       // 0-100
  width?: number;      // character width of the bar (default 20)
  color?: TuiProgressColor;
  className?: string;
  showPercent?: boolean;
}

const FILL_CLASSES: Record<TuiProgressColor, string> = {
  ok: 'tui-progress-fill',
  warn: 'tui-progress-fill tui-progress-fill--warn',
  error: 'tui-progress-fill tui-progress-fill--error',
  accent: 'tui-progress-fill tui-progress-fill--accent',
};

/**
 * Terminal-style progress bar: [████████░░░░] 62%
 *
 * Color defaults to 'ok' (green). Use 'warn' for amber, 'error' for red.
 */
export function TuiProgress({
  value,
  width = 20,
  color = 'ok',
  showPercent = true,
  className,
}: TuiProgressProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const filled = Math.round((clamped / 100) * width);
  const empty = width - filled;

  return (
    <span className={clsx('tui-progress', className)}>
      [<span className={FILL_CLASSES[color]}>{'█'.repeat(filled)}</span>
      <span className="tui-progress-empty">{'░'.repeat(empty)}</span>]
      {showPercent && <span className="ml-1">{Math.round(clamped)}%</span>}
    </span>
  );
}
