import { clsx } from 'clsx';

type TuiBoxVariant = 'default' | 'accent' | 'success' | 'warning' | 'error';

interface TuiBoxProps {
  title?: string;
  variant?: TuiBoxVariant;
  className?: string;
  children: React.ReactNode;
}

/**
 * Terminal-style bordered container with Unicode box-drawing characters.
 *
 * ┌─ TITLE ──────────────────────┐
 * │ content                      │
 * │ more content                 │
 * └──────────────────────────────┘
 *
 * Horizontal lines use a CSS border trick: a flex-growing span with a
 * bottom border renders as a continuous line. Side borders use
 * border-left/border-right on the content div so they stretch with content.
 */
export function TuiBox({ title, variant = 'default', className, children }: TuiBoxProps) {
  const variantClass = variant !== 'default' ? `tui-box--${variant}` : '';

  return (
    <div className={clsx('tui-box', variantClass, className)}>
      {/* Top frame: ┌─ TITLE ─────┐ */}
      <div className="tui-box-frame tui-box-frame-top" aria-hidden="true">
        <span className="tui-corner">┌</span>
        {title ? (
          <>
            <span className="tui-hline" />
            <span className="tui-box-title">{title}</span>
            <span className="tui-hline tui-hline-fill" />
          </>
        ) : (
          <span className="tui-hline tui-hline-fill" />
        )}
        <span className="tui-corner">┐</span>
      </div>

      {/* Content with CSS border sides (stretches with content height) */}
      <div className="tui-box-body">
        <div className="tui-box-content">{children}</div>
      </div>

      {/* Bottom frame: └─────────────┘ */}
      <div className="tui-box-frame tui-box-frame-bottom" aria-hidden="true">
        <span className="tui-corner">└</span>
        <span className="tui-hline tui-hline-fill" />
        <span className="tui-corner">┘</span>
      </div>
    </div>
  );
}
