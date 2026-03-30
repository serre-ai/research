import type { ReactNode } from 'react';
import { TuiKeyHints } from './tui-key-hints';

interface TuiFrameProps {
  title?: string;
  titleRight?: ReactNode;
  children: ReactNode;
}

/**
 * Full-viewport bordered frame with title bar and status bar.
 * Server component — TuiKeyHints is the only client island.
 */
export function TuiFrame({ title = 'FORGE', titleRight, children }: TuiFrameProps) {
  return (
    <div className="tui-frame">
      {/* Title bar */}
      <div className="tui-frame__titlebar">
        <span className="tui-frame__title">{title}</span>
        {titleRight && <span className="tui-frame__title-right">{titleRight}</span>}
      </div>

      {/* Content */}
      <div className="tui-frame__body">
        <div className="tui-frame__content">
          {children}
        </div>
      </div>

      {/* Status bar with key hints */}
      <div className="tui-frame__statusbar">
        <TuiKeyHints />
      </div>
    </div>
  );
}
