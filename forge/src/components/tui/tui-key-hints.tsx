'use client';

import { useFocus } from '@/providers/focus-provider';

/**
 * Context-sensitive keyboard shortcut bar.
 * Shows global hints + active panel's specific hints.
 */
export function TuiKeyHints() {
  const { globalKeyHints, activeKeyHints } = useFocus();
  const hints = [...activeKeyHints, ...globalKeyHints];

  return (
    <div className="tui-frame__hints" aria-label="Keyboard shortcuts">
      {hints.map((hint) => (
        <span key={hint.key} className="tui-frame__hint">
          <kbd className="tui-frame__hint-key">{hint.key}</kbd>
          <span>{hint.label}</span>
        </span>
      ))}
    </div>
  );
}
