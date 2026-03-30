import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import type { ReactNode } from 'react';
import { useEvalData } from '@/hooks/use-eval';

vi.mock('@/lib/api', () => ({
  apiFetch: vi.fn(),
}));

import { apiFetch } from '@/lib/api';

const mockApiFetch = apiFetch as ReturnType<typeof vi.fn>;

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe('useEvalData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('transforms raw run fields correctly', async () => {
    mockApiFetch.mockResolvedValueOnce({
      runs: [
        {
          run_id: 'run-abc',
          model: 'claude-3',
          task: 'B1',
          condition: 'cot',
          instance_count: 50,
          accuracy: 0.85,
          started_at: '2026-03-01T00:00:00Z',
        },
      ],
      progress: [],
      byDifficulty: [],
    });

    const { result } = renderHook(() => useEvalData('test-project'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    const run = result.current.data!.runs[0];
    expect(run.id).toBe('run-abc');
    expect(run.instances).toBe(50);
    expect(run.created_at).toBe('2026-03-01T00:00:00Z');
    expect(run.model).toBe('claude-3');
    expect(run.task).toBe('B1');
    expect(run.condition).toBe('cot');
    expect(run.accuracy).toBe(0.85);
  });

  it('handles nullish defaults', async () => {
    mockApiFetch.mockResolvedValueOnce({
      runs: [
        {
          run_id: 'run-null',
          model: 'gpt-4',
          task: 'B2',
          condition: 'direct',
          instance_count: null,
          accuracy: null,
          started_at: '2026-03-02T00:00:00Z',
        },
      ],
      progress: [],
      byDifficulty: [],
    });

    const { result } = renderHook(() => useEvalData('test-project'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    const run = result.current.data!.runs[0];
    expect(run.instances).toBe(0);
    expect(run.accuracy).toBe(0);
  });

  it('computes summary correctly', async () => {
    mockApiFetch.mockResolvedValueOnce({
      runs: [
        {
          run_id: 'run-1',
          model: 'claude-3',
          task: 'B1',
          condition: 'cot',
          instance_count: 100,
          accuracy: 0.9,
          started_at: '2026-03-01T00:00:00Z',
        },
        {
          run_id: 'run-2',
          model: 'gpt-4',
          task: 'B2',
          condition: 'direct',
          instance_count: 50,
          accuracy: 0,
          started_at: '2026-03-02T00:00:00Z',
        },
        {
          run_id: 'run-3',
          model: 'claude-3',
          task: 'B3',
          condition: 'cot',
          instance_count: 0,
          accuracy: 0,
          started_at: '2026-03-03T00:00:00Z',
        },
      ],
      progress: [
        { model: 'claude-3', task: 'B1', condition: 'cot', completed_count: 80, correct_count: 72, accuracy: 0.9, avg_latency_ms: 100, last_updated: '2026-03-01' },
        { model: 'gpt-4', task: 'B2', condition: 'direct', completed_count: 50, correct_count: 0, accuracy: 0, avg_latency_ms: 200, last_updated: '2026-03-02' },
      ],
      byDifficulty: [],
    });

    const { result } = renderHook(() => useEvalData('test-project'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    const summary = result.current.data!.summary;
    expect(summary.total).toBe(3);
    expect(summary.completed).toBe(130); // 80 + 50
    // run-2 has accuracy===0 && instances>0 => failed; run-3 has instances===0 => not failed
    expect(summary.failed).toBe(1);
  });

  it('handles empty response', async () => {
    mockApiFetch.mockResolvedValueOnce({
      runs: [],
      progress: [],
      byDifficulty: [],
    });

    const { result } = renderHook(() => useEvalData('test-project'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data!.runs).toEqual([]);
    expect(result.current.data!.progress).toEqual([]);
    expect(result.current.data!.summary).toEqual({ total: 0, completed: 0, failed: 0 });
  });
});
