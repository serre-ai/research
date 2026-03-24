'use client';

import { useEffect, useRef, useCallback } from 'react';
import type { ReactNode } from 'react';
import { clsx } from 'clsx';
import { useFocus } from '@/providers/focus-provider';

interface TuiListProps<T> {
  panelId: string;
  items: T[];
  renderItem: (item: T, index: number, active: boolean) => ReactNode;
  keyFn?: (item: T, index: number) => string;
  onActivate?: (item: T, index: number) => void;
  emptyMessage?: string;
  className?: string;
}

/**
 * Keyboard-navigable list inside a TuiPanel.
 *
 * Active item gets `> ` cursor prefix. Inactive items get `  ` for alignment.
 * Arrow keys change selection (handled by FocusProvider). Mouse click selects.
 * Active item auto-scrolls into view.
 */
export function TuiList<T>({
  panelId,
  items,
  renderItem,
  keyFn,
  onActivate,
  emptyMessage = 'empty',
  className,
}: TuiListProps<T>) {
  const { isItemActive, focusItem } = useFocus();
  const itemRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  // Find active index for scroll-into-view
  const activeIndex = items.findIndex((_, i) => isItemActive(panelId, i));

  useEffect(() => {
    if (activeIndex >= 0) {
      const el = itemRefs.current.get(activeIndex);
      el?.scrollIntoView({ block: 'nearest' });
    }
  }, [activeIndex]);

  // Single click: select and activate (navigate)
  const handleItemClick = useCallback(
    (index: number) => {
      focusItem(panelId, index);
      onActivate?.(items[index], index);
    },
    [panelId, focusItem, onActivate, items],
  );

  if (items.length === 0) {
    return <div className="tui-list__empty">{emptyMessage}</div>;
  }

  return (
    <div className={clsx('tui-list', className)} role="listbox" aria-label={panelId}>
      {items.map((item, index) => {
        const active = isItemActive(panelId, index);
        return (
          <div
            key={keyFn ? keyFn(item, index) : index}
            ref={(el) => {
              if (el) itemRefs.current.set(index, el);
              else itemRefs.current.delete(index);
            }}
            className={clsx('tui-list__item', active && 'tui-list__item--active')}
            onClick={() => handleItemClick(index)}
            role="option"
            aria-selected={active}
          >
            <span className="tui-list__cursor" aria-hidden="true">
              {active ? '> ' : '\u00A0\u00A0'}
            </span>
            <span className="tui-list__content">
              {renderItem(item, index, active)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
