import type { ReactNode } from 'react';
import { TuiKeyHints } from './tui-key-hints';

interface TuiFrameProps {
  title?: string;
  titleRight?: ReactNode;
  children: ReactNode;
}

/**
 * Full-viewport double-line bordered frame.
 * Server component — TuiKeyHints is the only client island.
 *
 * ╔═ TITLE ══════════════════ STATUS ═╗
 * ║  {children}                       ║
 * ╠═══════════════════════════════════╣
 * ║ Tab:Next  ↑↓:Nav  Enter:Select   ║
 * ╚═══════════════════════════════════╝
 */
export function TuiFrame({ title = 'DEEPWORK', titleRight, children }: TuiFrameProps) {
  return (
    <div className="tui-frame">
      {/* Top: ╔═ TITLE ════════════ STATUS ═╗ */}
      <div className="tui-frame__top" aria-hidden="true">
        <span className="tui-frame__corner">╔</span>
        <span className="tui-frame__hline" />
        <span className="tui-frame__title">{title}</span>
        <span className="tui-frame__hline tui-frame__hline--fill" />
        {titleRight && (
          <>
            <span className="tui-frame__title-right">{titleRight}</span>
            <span className="tui-frame__hline" />
          </>
        )}
        <span className="tui-frame__corner">╗</span>
      </div>

      {/* Content */}
      <div className="tui-frame__body">
        <div className="tui-frame__content">
          {children}
        </div>
      </div>

      {/* Separator: ╠═══════════╣ */}
      <div className="tui-frame__separator" aria-hidden="true">
        <span className="tui-frame__corner">╠</span>
        <span className="tui-frame__hline tui-frame__hline--fill" />
        <span className="tui-frame__corner">╣</span>
      </div>

      {/* Key hints (client island) */}
      <div className="tui-frame__hints-row">
        <TuiKeyHints />
      </div>

      {/* Bottom: ╚═══════════╝ */}
      <div className="tui-frame__bottom" aria-hidden="true">
        <span className="tui-frame__corner">╚</span>
        <span className="tui-frame__hline tui-frame__hline--fill" />
        <span className="tui-frame__corner">╝</span>
      </div>
    </div>
  );
}
