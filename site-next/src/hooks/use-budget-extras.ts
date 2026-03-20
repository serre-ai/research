import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';

interface BudgetProvider {
  id: string;
  display_name: string;
  provider_type: string;
  monthly_fixed: number;
  enabled: boolean;
}

interface RecordManualCostRequest {
  provider: string;
  cost_usd: number;
  description: string;
}

export function useBudgetProviders() {
  return useQuery({
    queryKey: ['budget', 'providers'],
    queryFn: () => apiFetch<BudgetProvider[]>('/budget/providers'),
    staleTime: 120_000,
  });
}

export function useRecordManualCost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: RecordManualCostRequest) =>
      apiFetch<void>('/budget/manual', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Manual cost recorded');
      queryClient.invalidateQueries({ queryKey: ['budget'] });
    },
    onError: (error) => {
      toast.error(`Failed to record cost: ${error.message}`);
    },
  });
}
