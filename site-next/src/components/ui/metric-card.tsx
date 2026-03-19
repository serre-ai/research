import { clsx } from 'clsx';
import type { LucideIcon } from 'lucide-react';
import { Card } from './card';
import { Label } from './label';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: LucideIcon;
  trend?: { value: number; label: string };
  className?: string;
}

export function MetricCard({ label, value, icon: Icon, trend, className }: MetricCardProps) {
  return (
    <Card className={clsx('flex flex-col gap-2', className)}>
      <div className="flex items-center justify-between">
        <Label>{label}</Label>
        {Icon && <Icon className="h-4 w-4 text-text-muted" />}
      </div>
      <div className="font-mono text-2xl font-bold tabular-nums text-text-bright">
        {value}
      </div>
      {trend && (
        <div className={clsx(
          'text-xs font-mono',
          trend.value >= 0 ? 'text-[--color-status-ok]' : 'text-[--color-status-error]',
        )}>
          {trend.value >= 0 ? '+' : ''}{trend.value}% {trend.label}
        </div>
      )}
    </Card>
  );
}
