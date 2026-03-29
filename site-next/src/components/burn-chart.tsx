'use client';

import { TuiSparkline } from '@/components/tui';

interface BurnChartProps {
  data: Array<{ date: string; total_usd: number }>;
  dailyLimit?: number;
}

export function BurnChart({ data, dailyLimit }: BurnChartProps) {
  if (!data.length) {
    return <span className="text-text-muted">no spend data</span>;
  }

  const values = data.map((d) => d.total_usd);
  const max = Math.max(...values, dailyLimit ?? 0);
  const min = Math.min(...values);

  return (
    <div className="space-y-2">
      {/* Sparkline */}
      <div className="flex items-end gap-1">
        <span className="text-text-muted shrink-0">${min.toFixed(0)}</span>
        <TuiSparkline data={values} />
        <span className="text-text-muted shrink-0">${max.toFixed(0)}</span>
      </div>

      {dailyLimit != null && (
        <span className="text-text-muted">limit: ${dailyLimit}/day</span>
      )}

      {/* Last 7 days as text table */}
      <div className="space-y-0">
        {data.slice(-7).map((d) => {
          const overLimit = dailyLimit != null && d.total_usd > dailyLimit;
          return (
            <div key={d.date} className="flex items-center gap-2">
              <span className="w-16 shrink-0 tabular-nums text-text-muted">
                {d.date.slice(5)}
              </span>
              <span className={`tabular-nums ${overLimit ? 'text-[--color-danger]' : 'text-text-bright'}`}>
                ${d.total_usd.toFixed(2)}
              </span>
              {overLimit && <span className="text-[--color-danger]">!</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
