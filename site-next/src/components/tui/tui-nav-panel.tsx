'use client';

import { useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { TuiPanel } from './tui-panel';
import { TuiList } from './tui-list';
import { useFocus } from '@/providers/focus-provider';
import { NAV_ITEMS } from '@/lib/nav-items';

/**
 * Persistent navigation panel (order=0, always first in Tab cycle).
 * Renders nav items as a TuiList. Enter navigates and focuses first content panel.
 */
export function TuiNavPanel() {
  const router = useRouter();
  const pathname = usePathname();
  const { focusFirstAfter } = useFocus();

  const handleActivate = useCallback(
    (item: (typeof NAV_ITEMS)[number]) => {
      router.push(item.href);
      // Focus first content panel after navigation
      requestAnimationFrame(() => focusFirstAfter(1));
    },
    [router, focusFirstAfter],
  );

  return (
    <TuiPanel
      id="nav"
      title="NAV"
      order={0}
      itemCount={NAV_ITEMS.length}
      onActivateItem={(idx) => handleActivate(NAV_ITEMS[idx])}
    >
      <TuiList
        panelId="nav"
        items={[...NAV_ITEMS]}
        keyFn={(item) => item.href}
        onActivate={handleActivate}
        renderItem={(item, _i, active) => {
          const isCurrent = pathname === item.href ||
            (item.href !== '/dashboard' && pathname.startsWith(item.href));
          return (
            <span
              className={
                active ? 'text-text-bright' :
                isCurrent ? 'text-[--color-accent-primary]' :
                'text-text-secondary'
              }
            >
              {item.label.toUpperCase()}
            </span>
          );
        }}
      />
    </TuiPanel>
  );
}
