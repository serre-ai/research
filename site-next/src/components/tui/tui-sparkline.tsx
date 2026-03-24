import { clsx } from 'clsx';

interface TuiSparklineProps {
  data: number[];
  className?: string;
}

const BLOCKS = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];

/**
 * Terminal-style sparkline from number array: ▁▂▃▅▇█▇▅▃▂
 */
export function TuiSparkline({ data, className }: TuiSparklineProps) {
  if (data.length === 0) return null;

  let min = data[0];
  let max = data[0];
  for (const v of data) {
    if (v < min) min = v;
    if (v > max) max = v;
  }
  const range = max - min || 1;

  const chars = data.map((v) => {
    const idx = Math.round(((v - min) / range) * (BLOCKS.length - 1));
    return BLOCKS[idx];
  });

  return (
    <span className={clsx('tui-sparkline', className)} aria-label={`sparkline: ${data.join(', ')}`}>
      {chars.join('')}
    </span>
  );
}
