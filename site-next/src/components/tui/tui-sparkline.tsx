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

  const min = Math.min(...data);
  const max = Math.max(...data);
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
