'use client';

import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { useFocusKeydownHandler } from '@/providers/focus-provider';

interface TuiScreenProps {
  children: ReactNode;
}

/**
 * Root TUI viewport. Fills 100vw × 100vh, enforces one font size,
 * no page scroll, captures keyboard events for the focus system.
 */
export function TuiScreen({ children }: TuiScreenProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const handlerRef = useFocusKeydownHandler();

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      // Don't intercept typing in inputs
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      // Don't intercept browser shortcuts (Cmd+T, Cmd+W, etc.)
      if (e.metaKey || e.ctrlKey) return;

      handlerRef.current(e);
    }

    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [handlerRef]);

  return (
    <div ref={containerRef} className="tui-screen" tabIndex={-1}>
      {children}
    </div>
  );
}
