'use client';

import type { ReactNode } from 'react';
import { WebSocketProvider } from './websocket-provider';
import { FocusProvider } from './focus-provider';
import { Toaster } from 'sonner';

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <FocusProvider>
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
              fontSize: '14px',
            },
          }}
        />
      </WebSocketProvider>
    </FocusProvider>
  );
}
