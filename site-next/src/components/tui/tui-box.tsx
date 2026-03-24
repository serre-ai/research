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
 * └──────────────────────────────┘
 */
export function TuiBox({ title, variant = 'default', className, children }: TuiBoxProps) {
  const variantClass = variant !== 'default' ? `tui-box--${variant}` : '';

  return (
    <div className={clsx('tui-box', variantClass, className)}>
      {/* Top frame */}
      <div className="tui-box-frame tui-box-frame-top" aria-hidden="true">
        <span className="tui-corner">┌</span>
        {title ? (
          <>
            <span className="tui-line">─</span>
            <span className="tui-box-title">{title}</span>
            <span className="tui-line" style={{ overflow: 'hidden' }}>
              {'─'.repeat(200)}
            </span>
          </>
        ) : (
          <span className="tui-line">{'─'.repeat(200)}</span>
        )}
        <span className="tui-corner">┐</span>
      </div>

      {/* Content with side borders */}
      <div className="flex">
        <span className="tui-box-frame tui-box-side" aria-hidden="true">│</span>
        <div className="tui-box-content flex-1 min-w-0">{children}</div>
        <span className="tui-box-frame tui-box-side" aria-hidden="true">│</span>
      </div>

      {/* Bottom frame */}
      <div className="tui-box-frame tui-box-frame-bottom" aria-hidden="true">
        <span className="tui-corner">└</span>
        <span className="tui-line">{'─'.repeat(200)}</span>
        <span className="tui-corner">┘</span>
      </div>
    </div>
  );
}
