'use client';

import { use } from 'react';
import { DollarSign, TrendingUp, Gauge, Calendar } from 'lucide-react';
import { useBudget } from '@/hooks';
import { useDailySpend } from '@/hooks/use-daily-spend';
import { useBudgetProviders } from '@/hooks/use-budget-extras';
import { Card } from '@/components/ui/card';
import { MetricCard } from '@/components/ui/metric-card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ProgressBar } from '@/components/ui/progress-bar';
import { BurnChart } from '@/components/burn-chart';
import { ProviderBreakdown } from '@/components/provider-breakdown';
import { ManualCostDialog } from '@/components/manual-cost-dialog';

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
  const { data: providers, isLoading: providersLoading } = useBudgetProviders();

  const monthlyBudget = 1000;
  const spent = budget?.total ?? 0;
  const remaining = budget?.remaining ?? monthlyBudget;
  const spentPct = monthlyBudget > 0 ? (spent / monthlyBudget) * 100 : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="font-mono text-lg font-semibold text-text-bright">Budget</h2>
        <ManualCostDialog />
      </div>

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

      {/* Providers */}
      <section>
        <Label className="mb-3 block">Providers</Label>
        {providersLoading ? (
          <Card>
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-8 w-full" />
              ))}
            </div>
          </Card>
        ) : providers && providers.length > 0 ? (
          <Card padding={false}>
            <div className="overflow-x-auto">
              <table className="w-full font-mono text-xs">
                <thead>
                  <tr className="border-b border-border text-left text-text-muted">
                    <th className="px-4 py-2 font-medium">Provider</th>
                    <th className="px-4 py-2 font-medium">Type</th>
                    <th className="px-4 py-2 font-medium text-right">Monthly Fixed</th>
                    <th className="px-4 py-2 font-medium text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {providers.map((p) => (
                    <tr key={p.id} className="hover:bg-bg-elevated transition-colors">
                      <td className="px-4 py-2 text-text-secondary">{p.display_name}</td>
                      <td className="px-4 py-2 text-text-muted">{p.provider_type}</td>
                      <td className="px-4 py-2 text-right tabular-nums text-text-bright">
                        ${p.monthly_fixed.toFixed(2)}
                      </td>
                      <td className="px-4 py-2 text-right">
                        <Badge variant={p.enabled ? 'success' : 'default'}>
                          {p.enabled ? 'active' : 'disabled'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        ) : (
          <Card>
            <p className="font-mono text-xs text-text-muted">No providers configured.</p>
          </Card>
        )}
      </section>
    </div>
  );
}
