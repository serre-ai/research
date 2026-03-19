'use client';

import type { ReactNode } from 'react';
import { WebSocketProvider } from './websocket-provider';
import { Toaster } from 'sonner';

/**
 * Client providers for the authenticated (app) layout.
 * Wraps children with WebSocket connectivity and toast notifications.
 *
 * Add this inside the (app)/layout.tsx:
 *   import { AppProviders } from '@/providers/app-providers';
 *   <AppProviders>{children}</AppProviders>
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <WebSocketProvider>
      {children}
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.875rem',
          },
        }}
      />
    </WebSocketProvider>
  );
}
