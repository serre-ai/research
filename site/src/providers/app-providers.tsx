'use client';

import type { ReactNode } from 'react';
import { QueryProvider } from './query-provider';
import { WebSocketProvider } from './websocket-provider';
import { Toaster } from 'sonner';

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <QueryProvider>
      <WebSocketProvider>
        {children}
        <Toaster
          theme="dark"
          position="bottom-right"
          toastOptions={{
            style: {
              background: 'var(--card)',
              border: '1px solid var(--border)',
              color: 'var(--foreground)',
              fontSize: '13px',
            },
          }}
        />
      </WebSocketProvider>
    </QueryProvider>
  );
}
