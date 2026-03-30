import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import type { ReactNode } from 'react';
import { useWsInvalidation } from '@/hooks/use-ws-invalidation';

type MessageHandler = (msg: { channel: string; event: string; data: unknown }) => void;

const mockSubscribe = vi.fn();
const mockUnsubscribe = vi.fn();
let capturedHandler: MessageHandler | null = null;
const mockCleanup = vi.fn();
const mockOnMessage = vi.fn((handler: MessageHandler) => {
  capturedHandler = handler;
  return mockCleanup;
});

vi.mock('@/providers/websocket-provider', () => ({
  useWebSocket: () => ({
    subscribe: mockSubscribe,
    unsubscribe: mockUnsubscribe,
    onMessage: mockOnMessage,
  }),
}));

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

describe('useWsInvalidation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    capturedHandler = null;
  });

  it('subscribes to 4 channels on mount', () => {
    renderHook(() => useWsInvalidation(), {
      wrapper: createWrapper(),
    });

    expect(mockSubscribe).toHaveBeenCalledTimes(4);
    expect(mockSubscribe).toHaveBeenCalledWith('eval-progress');
    expect(mockSubscribe).toHaveBeenCalledWith('logs');
    expect(mockSubscribe).toHaveBeenCalledWith('budget');
    expect(mockSubscribe).toHaveBeenCalledWith('health');
  });

  it('unsubscribes from 4 channels on unmount', () => {
    const { unmount } = renderHook(() => useWsInvalidation(), {
      wrapper: createWrapper(),
    });

    unmount();

    expect(mockUnsubscribe).toHaveBeenCalledTimes(4);
    expect(mockUnsubscribe).toHaveBeenCalledWith('eval-progress');
    expect(mockUnsubscribe).toHaveBeenCalledWith('logs');
    expect(mockUnsubscribe).toHaveBeenCalledWith('budget');
    expect(mockUnsubscribe).toHaveBeenCalledWith('health');
    expect(mockCleanup).toHaveBeenCalledTimes(1);
  });

  it('invalidates ["eval"] on eval-progress message', () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const spy = vi.spyOn(queryClient, 'invalidateQueries');

    renderHook(() => useWsInvalidation(), {
      wrapper: ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });

    expect(capturedHandler).not.toBeNull();

    act(() => {
      capturedHandler!({ channel: 'eval-progress', event: 'update', data: {} });
    });

    expect(spy).toHaveBeenCalledWith({ queryKey: ['eval'] });
  });

  it('invalidates ["activity"], ["sessions"], ["events"] on logs message', () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const spy = vi.spyOn(queryClient, 'invalidateQueries');

    renderHook(() => useWsInvalidation(), {
      wrapper: ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });

    act(() => {
      capturedHandler!({ channel: 'logs', event: 'new', data: {} });
    });

    expect(spy).toHaveBeenCalledWith({ queryKey: ['activity'] });
    expect(spy).toHaveBeenCalledWith({ queryKey: ['sessions'] });
    expect(spy).toHaveBeenCalledWith({ queryKey: ['events'] });
  });

  it('invalidates ["budget"] on budget message', () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const spy = vi.spyOn(queryClient, 'invalidateQueries');

    renderHook(() => useWsInvalidation(), {
      wrapper: ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });

    act(() => {
      capturedHandler!({ channel: 'budget', event: 'update', data: {} });
    });

    expect(spy).toHaveBeenCalledWith({ queryKey: ['budget'] });
  });

  it('invalidates ["health"], ["daemon"] on health message', () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const spy = vi.spyOn(queryClient, 'invalidateQueries');

    renderHook(() => useWsInvalidation(), {
      wrapper: ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });

    act(() => {
      capturedHandler!({ channel: 'health', event: 'ping', data: {} });
    });

    expect(spy).toHaveBeenCalledWith({ queryKey: ['health'] });
    expect(spy).toHaveBeenCalledWith({ queryKey: ['daemon'] });
  });
});
