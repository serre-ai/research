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
 * Focusable panel with single-line box-drawing border.
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
      {/* Top border: ┌─ TITLE ──────┐ */}
      <div className="tui-panel__top" aria-hidden="true">
        <span className="tui-panel__corner">┌</span>
        {title ? (
          <>
            <span className="tui-panel__hline" />
            <span className="tui-panel__title">{title}</span>
            <span className="tui-panel__hline tui-panel__hline--fill" />
          </>
        ) : (
          <span className="tui-panel__hline tui-panel__hline--fill" />
        )}
        <span className="tui-panel__corner">┐</span>
      </div>

      {/* Content with side borders */}
      <div className="tui-panel__body">
        <div className="tui-panel__content">{children}</div>
      </div>

      {/* Bottom border: └──────────────┘ */}
      <div className="tui-panel__bottom" aria-hidden="true">
        <span className="tui-panel__corner">└</span>
        <span className="tui-panel__hline tui-panel__hline--fill" />
        <span className="tui-panel__corner">┘</span>
      </div>
    </div>
  );
}
