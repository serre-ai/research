import { clsx } from 'clsx';

interface TuiMetricProps {
  label: string;
  value: string | number;
  unit?: string;
  className?: string;
}

/**
 * Compact terminal-style metric display.
 *
 * DAILY SPEND
 * $14.34
 */
export function TuiMetric({ label, value, unit, className }: TuiMetricProps) {
  return (
    <div className={clsx('tui-metric', className)}>
      <div className="tui-metric-label">{label}</div>
      <div className="tui-metric-value">
        {value}
        {unit && <span className="tui-metric-unit"> {unit}</span>}
      </div>
    </div>
  );
}
