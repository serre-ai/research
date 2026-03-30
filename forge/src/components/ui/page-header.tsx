import { clsx } from 'clsx';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: { label: string; href?: string }[];
  children?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, subtitle, breadcrumbs, children, className }: PageHeaderProps) {
  return (
    <div className={clsx('mb-8', className)}>
      {breadcrumbs && (
        <nav className="mb-4 flex items-center gap-2 font-mono text-xs text-text-muted">
          {breadcrumbs.map((crumb, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <span>/</span>}
              {crumb.href ? (
                <a href={crumb.href} className="hover:text-text-secondary">{crumb.label}</a>
              ) : (
                <span>{crumb.label}</span>
              )}
            </span>
          ))}
        </nav>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-mono text-2xl font-semibold text-text-bright">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-text-secondary">{subtitle}</p>}
        </div>
        {children && <div className="flex items-center gap-3">{children}</div>}
      </div>
    </div>
  );
}
