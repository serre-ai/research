'use client';

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from '@/providers/websocket-provider';

/**
 * Subscribes to WebSocket channels and invalidates relevant
 * TanStack Query caches when real-time events arrive.
 */
export function useWsInvalidation() {
  const { subscribe, unsubscribe, onMessage } = useWebSocket();
  const queryClient = useQueryClient();

  useEffect(() => {
    subscribe('eval-progress');
    subscribe('logs');
    subscribe('budget');
    subscribe('health');

    const cleanup = onMessage((msg) => {
      switch (msg.channel) {
        case 'eval-progress':
          queryClient.invalidateQueries({ queryKey: ['eval'] });
          break;
        case 'logs':
          queryClient.invalidateQueries({ queryKey: ['activity'] });
          queryClient.invalidateQueries({ queryKey: ['sessions'] });
          break;
        case 'budget':
          queryClient.invalidateQueries({ queryKey: ['budget'] });
          break;
        case 'health':
          queryClient.invalidateQueries({ queryKey: ['health'] });
          queryClient.invalidateQueries({ queryKey: ['daemon'] });
          break;
      }
    });

    return () => {
      unsubscribe('eval-progress');
      unsubscribe('logs');
      unsubscribe('budget');
      unsubscribe('health');
      cleanup();
    };
  }, [subscribe, unsubscribe, onMessage, queryClient]);
}
