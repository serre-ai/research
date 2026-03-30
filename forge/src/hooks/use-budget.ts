import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { Budget, BudgetApiResponse } from '@/lib/types';

function transformBudget(raw: BudgetApiResponse): Budget {
  const variableProviders: Record<string, number> = {};
  const fixedItems: { name: string; amount: number }[] = [];

  for (const p of raw.byProvider) {
    if (p.provider_type.includes('variable')) {
      variableProviders[p.display_name] = p.cost_usd;
    } else {
      fixedItems.push({ name: p.display_name, amount: p.cost_usd });
    }
  }

  const monthlyLimit = raw.limits.monthly_usd;
  const total = raw.monthly.total_usd;

  return {
    month: new Date().toLocaleString('en-US', { month: 'long', year: 'numeric' }),
    variable_costs: {
      total: raw.monthly.variable_usd,
      by_provider: variableProviders,
    },
    fixed_costs: {
      total: raw.monthly.fixed_usd,
      items: fixedItems,
    },
    total,
    daily_limit: raw.limits.daily_usd,
    burn_rate: raw.burnRate.daily_7d_avg,
    projected_monthly: raw.burnRate.projected_month_end,
    remaining: monthlyLimit - total,
  };
}

export function useBudget() {
  return useQuery({
    queryKey: ['budget'],
    queryFn: async () => {
      const raw = await apiFetch<BudgetApiResponse>('/budget');
      return transformBudget(raw);
    },
    staleTime: 60_000,
  });
}
