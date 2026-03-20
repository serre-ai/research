'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';

const tabs = [
  { label: 'Browser', href: '' },
  { label: 'Alerts', href: '/alerts' },
  { label: 'Stats', href: '/stats' },
];

export default function KnowledgeLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const basePath = '/knowledge';

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-mono text-2xl font-semibold text-text-bright">Knowledge Graph</h1>
        <p className="mt-1 font-mono text-xs text-text-muted">Claims, evidence chains, and contradictions</p>
      </div>

      <nav className="flex overflow-x-auto border-b border-border mb-6">
        {tabs.map((tab) => {
          const tabPath = `${basePath}${tab.href}`;
          const isActive =
            tab.href === ''
              ? pathname === basePath || pathname === `${basePath}/`
              : pathname.startsWith(tabPath);

          return (
            <Link
              key={tab.label}
              href={tabPath}
              className={clsx(
                'whitespace-nowrap shrink-0 px-4 py-2 font-mono text-sm border-b-2 -mb-px transition-colors',
                isActive
                  ? 'border-primary text-text-bright'
                  : 'border-transparent text-text-muted hover:text-text-secondary',
              )}
            >
              {tab.label}
            </Link>
          );
        })}
      </nav>

      {children}
    </div>
  );
}
