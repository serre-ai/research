'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface BurnChartProps {
  data: Array<{ date: string; total_usd: number }>;
  dailyLimit?: number;
}

function formatDateLabel(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatDollar(value: number): string {
  return `$${value.toFixed(0)}`;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div
      style={{
        backgroundColor: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border)',
        padding: '8px 12px',
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
      }}
    >
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '4px' }}>
        {label ? formatDateLabel(label) : ''}
      </p>
      <p style={{ color: 'var(--color-text-bright)', fontWeight: 600 }}>
        ${payload[0].value.toFixed(2)}
      </p>
    </div>
  );
}

export function BurnChart({ data, dailyLimit }: BurnChartProps) {
  if (!data.length) {
    return (
      <div className="flex h-[300px] items-center justify-center text-sm text-text-muted">
        No spend data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="burnFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.15} />
            <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="var(--color-border)"
          strokeOpacity={0.3}
          vertical={false}
        />
        <XAxis
          dataKey="date"
          tickFormatter={formatDateLabel}
          tick={{
            fill: 'var(--color-text-muted)',
            fontFamily: 'var(--font-mono)',
            fontSize: 11,
          }}
          axisLine={{ stroke: 'var(--color-border)' }}
          tickLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          tickFormatter={formatDollar}
          tick={{
            fill: 'var(--color-text-muted)',
            fontFamily: 'var(--font-mono)',
            fontSize: 11,
          }}
          axisLine={false}
          tickLine={false}
          width={50}
        />
        <Tooltip content={<CustomTooltip />} />
        {dailyLimit != null && (
          <ReferenceLine
            y={dailyLimit}
            stroke="var(--color-status-warn)"
            strokeDasharray="6 4"
            strokeWidth={1.5}
            label={{
              value: `Limit $${dailyLimit}`,
              fill: 'var(--color-status-warn)',
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              position: 'insideTopRight',
            }}
          />
        )}
        <Area
          type="monotone"
          dataKey="total_usd"
          stroke="var(--color-primary)"
          strokeWidth={2}
          fill="url(#burnFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
