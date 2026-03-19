'use client';

import { use } from 'react';
import { DollarSign, TrendingUp, Gauge, Calendar } from 'lucide-react';
import { useBudget } from '@/hooks';
import { useDailySpend } from '@/hooks/use-daily-spend';
import { Card } from '@/components/ui/card';
import { MetricCard } from '@/components/ui/metric-card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { ProgressBar } from '@/components/ui/progress-bar';
import { BurnChart } from '@/components/burn-chart';
import { ProviderBreakdown } from '@/components/provider-breakdown';

function MetricSkeleton() {
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-4 w-4" />
      </div>
      <Skeleton className="h-8 w-20" />
    </Card>
  );
}

function ChartSkeleton() {
  return (
    <Card>
      <Skeleton className="mb-4 h-3 w-32" />
      <Skeleton className="h-[300px] w-full" />
    </Card>
  );
}

function formatCurrency(value: number): string {
  return `$${value.toFixed(0)}`;
}

function formatCurrencyDecimal(value: number): string {
  return `$${value.toFixed(2)}`;
}

export default function BudgetPage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  // Unwrap dynamic route params (Next.js 16 async params in client components)
  use(params);

  const { data: budget, isLoading: budgetLoading } = useBudget();
  const { data: dailySpend, isLoading: dailyLoading } = useDailySpend();

  const monthlyBudget = 1000;
  const spent = budget?.total ?? 0;
  const remaining = budget?.remaining ?? monthlyBudget;
  const spentPct = monthlyBudget > 0 ? (spent / monthlyBudget) * 100 : 0;

  return (
    <div className="space-y-8">
      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {budgetLoading ? (
          <>
            <MetricSkeleton />
            <MetricSkeleton />
            <MetricSkeleton />
            <MetricSkeleton />
          </>
        ) : (
          <>
            <MetricCard
              label="Monthly Spend"
              value={formatCurrency(spent)}
              icon={DollarSign}
            />
            <MetricCard
              label="Daily Limit"
              value={formatCurrency(budget?.daily_limit ?? 40)}
              icon={Gauge}
            />
            <MetricCard
              label="Burn Rate"
              value={`${formatCurrencyDecimal(budget?.burn_rate ?? 0)}/day`}
              icon={TrendingUp}
            />
            <MetricCard
              label="Projected Monthly"
              value={formatCurrency(budget?.projected_monthly ?? 0)}
              icon={Calendar}
            />
          </>
        )}
      </div>

      {/* Burn chart */}
      {dailyLoading ? (
        <ChartSkeleton />
      ) : (
        <Card>
          <Label className="mb-4 block">Daily Spend (Last 30 Days)</Label>
          <BurnChart
            data={dailySpend?.days ?? []}
            dailyLimit={budget?.daily_limit ?? 40}
          />
        </Card>
      )}

      {/* Provider breakdown + remaining budget */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Provider breakdown */}
        {budgetLoading ? (
          <Card>
            <Skeleton className="mb-4 h-3 w-40" />
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="space-y-1.5">
                  <div className="flex justify-between">
                    <Skeleton className="h-3 w-20" />
                    <Skeleton className="h-3 w-16" />
                  </div>
                  <Skeleton className="h-1.5 w-full" />
                </div>
              ))}
            </div>
          </Card>
        ) : (
          <Card>
            <Label className="mb-4 block">Provider Breakdown</Label>
            <ProviderBreakdown
              providers={budget?.variable_costs.by_provider ?? {}}
            />
            {budget?.fixed_costs && budget.fixed_costs.items.length > 0 && (
              <div className="mt-6 border-t border-border pt-4">
                <Label className="mb-3 block">Fixed Costs</Label>
                <div className="space-y-2">
                  {budget.fixed_costs.items.map((item) => (
                    <div
                      key={item.name}
                      className="flex items-center justify-between"
                    >
                      <span className="font-mono text-xs text-text-secondary">
                        {item.name}
                      </span>
                      <span className="font-mono text-xs tabular-nums text-text-bright">
                        ${item.amount.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}

        {/* Remaining budget */}
        {budgetLoading ? (
          <Card>
            <Skeleton className="mb-4 h-3 w-36" />
            <Skeleton className="mb-2 h-8 w-24" />
            <Skeleton className="h-2 w-full" />
          </Card>
        ) : (
          <Card className="flex flex-col">
            <Label className="mb-4">Remaining Budget</Label>
            <div className="mb-1 font-mono text-2xl font-bold tabular-nums text-text-bright">
              {formatCurrency(remaining)}
            </div>
            <p className="mb-4 font-mono text-xs text-text-muted">
              of {formatCurrency(monthlyBudget)} monthly budget
            </p>
            <ProgressBar
              value={spent}
              max={monthlyBudget}
              color={
                spentPct > 90
                  ? 'var(--color-status-error)'
                  : spentPct > 70
                    ? 'var(--color-status-warn)'
                    : undefined
              }
            />
            <div className="mt-2 flex justify-between font-mono text-[10px] text-text-muted">
              <span>{spentPct.toFixed(0)}% used</span>
              <span>{budget?.month ?? ''}</span>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
