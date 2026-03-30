'use client';

import { use } from 'react';
import { TuiBox, TuiProgress, TuiSkeleton, TuiBadge } from '@/components/tui';
import { useBudget } from '@/hooks';
import { useDailySpend } from '@/hooks/use-daily-spend';
import { useBudgetProviders } from '@/hooks/use-budget-extras';
import { BurnChart } from '@/components/burn-chart';
import { ProviderBreakdown } from '@/components/provider-breakdown';
import { ManualCostDialog } from '@/components/manual-cost-dialog';

export default function BudgetPage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  use(params);

  const { data: budget, isLoading: budgetLoading } = useBudget();
  const { data: dailySpend, isLoading: dailyLoading } = useDailySpend();
  const { data: providers, isLoading: providersLoading } = useBudgetProviders();

  const monthlyBudget = 1000;
  const spent = budget?.total ?? 0;
  const remaining = budget?.remaining ?? monthlyBudget;
  const spentPct = monthlyBudget > 0 ? Math.round((spent / monthlyBudget) * 100) : 0;

  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <ManualCostDialog />
      </div>

      {/* Summary metrics */}
      <TuiBox title="OVERVIEW" className="mb-3">
        {budgetLoading ? (
          <div className="flex flex-wrap gap-x-6 gap-y-1">
            {Array.from({ length: 4 }).map((_, i) => (
              <TuiSkeleton key={i} width={18} />
            ))}
          </div>
        ) : (
          <div className="flex flex-wrap gap-x-6 gap-y-1">
            <span>
              <span className="text-text-muted">spent </span>
              <span className="text-text-bright">${spent.toFixed(0)}</span>
              <span className="text-text-muted"> / ${monthlyBudget}</span>
            </span>
            <span>
              <span className="text-text-muted">limit </span>
              <span className="text-text-bright">${budget?.daily_limit ?? 40}</span>
              <span className="text-text-muted">/day</span>
            </span>
            <span>
              <span className="text-text-muted">burn </span>
              <span className="text-text-bright">${(budget?.burn_rate ?? 0).toFixed(2)}</span>
              <span className="text-text-muted">/day</span>
            </span>
            <span>
              <span className="text-text-muted">projected </span>
              <span className="text-text-bright">${(budget?.projected_monthly ?? 0).toFixed(0)}</span>
            </span>
            <span className="flex items-center gap-1">
              <TuiProgress
                value={spentPct}
                width={10}
                showPercent={false}
                color={spentPct > 90 ? 'error' : spentPct > 70 ? 'warn' : 'ok'}
              />
              <span className="text-text-muted">{spentPct}%</span>
              <span className="text-text-muted">({budget?.month ?? ''})</span>
            </span>
          </div>
        )}
      </TuiBox>

      {/* Burn chart */}
      <TuiBox title="DAILY SPEND (30D)" className="mb-3">
        {dailyLoading ? (
          <TuiSkeleton width={50} />
        ) : (
          <BurnChart
            data={dailySpend?.days ?? []}
            dailyLimit={budget?.daily_limit ?? 40}
          />
        )}
      </TuiBox>

      {/* Provider breakdown + remaining */}
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 mb-3">
        <TuiBox title="PROVIDER BREAKDOWN">
          {budgetLoading ? (
            <div className="space-y-1">
              {Array.from({ length: 3 }).map((_, i) => (
                <TuiSkeleton key={i} width={30} />
              ))}
            </div>
          ) : (
            <>
              <ProviderBreakdown
                providers={budget?.variable_costs.by_provider ?? {}}
              />
              {budget?.fixed_costs && budget.fixed_costs.items.length > 0 && (
                <div className="mt-3 border-t border-border pt-3">
                  <span className="text-text-muted mb-2 block">FIXED COSTS</span>
                  {budget.fixed_costs.items.map((item) => (
                    <div key={item.name} className="flex items-center justify-between">
                      <span className="text-text-secondary">{item.name}</span>
                      <span className="tabular-nums text-text-bright">${item.amount.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </TuiBox>

        <TuiBox title="REMAINING">
          {budgetLoading ? (
            <TuiSkeleton width={20} />
          ) : (
            <>
              <div className="mb-2">
                <span className="text-text-bright font-bold">${remaining.toFixed(0)}</span>
                <span className="text-text-muted"> of ${monthlyBudget}</span>
              </div>
              <TuiProgress
                value={spentPct}
                width={30}
                color={spentPct > 90 ? 'error' : spentPct > 70 ? 'warn' : 'ok'}
              />
            </>
          )}
        </TuiBox>
      </div>

      {/* Providers table */}
      <TuiBox title="PROVIDERS">
        {providersLoading ? (
          <div className="space-y-1">
            {Array.from({ length: 3 }).map((_, i) => (
              <TuiSkeleton key={i} width={50} />
            ))}
          </div>
        ) : providers && providers.length > 0 ? (
          <table className="tui-table">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Type</th>
                <th className="text-right">Fixed/mo</th>
                <th className="text-right">Status</th>
              </tr>
            </thead>
            <tbody>
              {providers.map((p) => (
                <tr key={p.id}>
                  <td className="text-text-secondary">{p.display_name}</td>
                  <td className="text-text-muted">{p.provider_type}</td>
                  <td className="text-right tabular-nums text-text-bright">${p.monthly_fixed.toFixed(2)}</td>
                  <td className="text-right">
                    <TuiBadge color={p.enabled ? 'ok' : 'muted'}>
                      {p.enabled ? 'ACTIVE' : 'OFF'}
                    </TuiBadge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <span className="text-text-muted">no providers configured</span>
        )}
      </TuiBox>
    </>
  );
}
