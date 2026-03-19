import { clsx } from 'clsx';

interface LabelProps {
  children: React.ReactNode;
  className?: string;
}

export function Label({ className, children }: LabelProps) {
  return (
    <span
      className={clsx(
        'font-mono text-xs font-medium uppercase tracking-wider text-text-muted',
        className,
      )}
    >
      {children}
    </span>
  );
}
