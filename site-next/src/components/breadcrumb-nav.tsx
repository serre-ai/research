'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight } from 'lucide-react';

const LABELS: Record<string, string> = {
  dashboard: 'Dashboard',
  projects: 'Projects',
  collective: 'Collective',
  knowledge: 'Knowledge',
  paper: 'Paper',
  logs: 'Logs',
  settings: 'Settings',
  forum: 'Forum',
  agents: 'Agents',
  governance: 'Governance',
  rituals: 'Rituals',
  messages: 'Messages',
  eval: 'Eval',
  budget: 'Budget',
  sessions: 'Sessions',
  decisions: 'Decisions',
  alerts: 'Alerts',
  stats: 'Stats',
  backlog: 'Backlog',
  verification: 'Verification',
};

export function BreadcrumbNav() {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  const crumbs = segments.map((seg, i) => {
    const href = '/' + segments.slice(0, i + 1).join('/');
    const label = LABELS[seg] ?? seg;
    const isLast = i === segments.length - 1;
    return { href, label, isLast };
  });

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 font-mono text-xs text-text-muted">
      {crumbs.map((crumb, i) => (
        <span key={crumb.href} className="flex items-center gap-1">
          {i > 0 && <ChevronRight className="h-3 w-3" />}
          {crumb.isLast ? (
            <span className="text-text-secondary" aria-current="page">{crumb.label}</span>
          ) : (
            <Link href={crumb.href} className="hover:text-text-secondary transition-colors">
              {crumb.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
