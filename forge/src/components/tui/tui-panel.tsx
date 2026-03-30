'use client';

import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { clsx } from 'clsx';
import { useFocus } from '@/providers/focus-provider';
import type { KeyHint } from '@/providers/focus-provider';

interface TuiPanelProps {
  id: string;
  title?: string;
  order?: number;
  itemCount?: number;
  keyHints?: KeyHint[];
  onActivateItem?: (index: number) => void;
  onEscape?: () => void;
  className?: string;
  children: ReactNode;
}

/**
 * Focusable panel with CSS border and background-gap title.
 * Registers with the focus system. Active panel gets bright border.
 */
export function TuiPanel({
  id,
  title,
  order = 0,
  itemCount = 0,
  keyHints,
  onActivateItem,
  onEscape,
  className,
  children,
}: TuiPanelProps) {
  const { registerPanel, updatePanel, isPanelActive, focusPanel } = useFocus();
  const active = isPanelActive(id);

  useEffect(() => {
    const unregister = registerPanel({ id, order, itemCount, keyHints, onActivateItem, onEscape });
    return unregister;
    // Only re-register on id/order change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, order]);

  useEffect(() => {
    updatePanel(id, { itemCount, keyHints, onActivateItem, onEscape });
  }, [id, itemCount, keyHints, onActivateItem, onEscape, updatePanel]);

  return (
    <div
      className={clsx('tui-panel', active && 'tui-panel--active', className)}
      onClick={() => focusPanel(id)}
      role="region"
      aria-label={title ?? id}
    >
      {title && <div className="tui-panel__label" aria-hidden="true">{title}</div>}
      <div className="tui-panel__body">
        <div className="tui-panel__content">{children}</div>
      </div>
    </div>
  );
}
