'use client';

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import { useFocus } from '@/providers/focus-provider';
import { TuiNavPanel } from './tui-nav-panel';

interface TuiAppShellProps {
  children: React.ReactNode;
}

/**
 * App layout wrapper: NAV panel (left) + page content (right).
 * Resets focus to the first content panel on page navigation.
 */
export function TuiAppShell({ children }: TuiAppShellProps) {
  const pathname = usePathname();
  const { focusFirstAfter } = useFocus();
  const prevPathname = useRef(pathname);

  // On page change, focus first content panel (order >= 1)
  useEffect(() => {
    if (prevPathname.current !== pathname) {
      prevPathname.current = pathname;
      const timer = setTimeout(() => focusFirstAfter(1), 50);
      return () => clearTimeout(timer);
    }
  }, [pathname, focusFirstAfter]);

  return (
    <div className="flex gap-3 h-full">
      <div className="shrink-0 w-[18ch]">
        <TuiNavPanel />
      </div>
      <div className="flex-1 min-w-0 space-y-3 overflow-y-auto">
        {children}
      </div>
    </div>
  );
}
