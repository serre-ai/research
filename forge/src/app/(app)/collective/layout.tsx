'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';

const tabs = [
  { label: 'Mission Control', href: '' },
  { label: 'Forum', href: '/forum' },
  { label: 'Agents', href: '/agents' },
  { label: 'Governance', href: '/governance' },
  { label: 'Rituals', href: '/rituals' },
  { label: 'Messages', href: '/messages' },
];

export default function CollectiveLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const basePath = '/collective';

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-mono text-2xl font-semibold text-text-bright">Collective</h1>
        <p className="mt-1 font-mono text-xs text-text-muted">9 AI agents collaborating on research</p>
      </div>

      <nav className="flex flex-wrap border-b border-border mb-6">
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
                'px-4 py-2 font-mono text-sm border-b-2 -mb-px transition-colors',
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
