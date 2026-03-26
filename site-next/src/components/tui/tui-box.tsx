import { clsx } from 'clsx';

type TuiBoxVariant = 'default' | 'accent' | 'success' | 'warning' | 'error';

interface TuiBoxProps {
  title?: string;
  variant?: TuiBoxVariant;
  className?: string;
  children: React.ReactNode;
}

/**
 * Terminal-style bordered container.
 * Uses CSS borders with background-gap title technique.
 */
export function TuiBox({ title, variant = 'default', className, children }: TuiBoxProps) {
  const variantClass = variant !== 'default' ? `tui-box--${variant}` : '';

  return (
    <div className={clsx('tui-box', variantClass, className)}>
      {title && <div className="tui-box-label" aria-hidden="true">{title}</div>}
      <div className="tui-box-content">{children}</div>
    </div>
  );
}
