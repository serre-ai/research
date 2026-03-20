'use client';

import { useParams, usePathname } from 'next/navigation';
import { useProject } from '@/hooks';
import { Skeleton } from '@/components/ui/skeleton';
import { StatusDot } from '@/components/ui/status-dot';
import Link from 'next/link';
import type { StatusKey } from '@/lib/constants';

const tabs = [
  { label: 'Overview', href: '' },
  { label: 'Eval', href: '/eval' },
  { label: 'Budget', href: '/budget' },
  { label: 'Sessions', href: '/sessions' },
  { label: 'Decisions', href: '/decisions' },
  { label: 'Verification', href: '/verification' },
  { label: 'Planner', href: '/planner' },
];

function mapProjectStatus(status?: string): StatusKey {
  switch (status) {
    case 'active':
    case 'running':
      return 'ok';
    case 'error':
    case 'failed':
      return 'error';
    case 'paused':
    case 'pending':
      return 'warn';
    default:
      return 'idle';
  }
}

export default function ProjectLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const name = params.name as string;
  const { data: project, isLoading } = useProject(name);

  const basePath = `/projects/${name}`;
  const statusKey = mapProjectStatus(project?.status);

  return (
    <div>
      {/* Project header */}
      <div className="mb-6">
        {isLoading ? (
          <div className="flex items-center gap-3">
            <Skeleton className="h-2 w-2 rounded-full" />
            <Skeleton className="h-7 w-64" />
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <StatusDot
              status={statusKey}
              pulse={project?.status === 'running' || project?.status === 'active'}
            />
            <h1 className="font-mono text-2xl font-semibold text-text-bright">
              {project?.name ?? name}
            </h1>
            {project?.phase && (
              <span className="font-mono text-xs text-text-muted">{project.phase}</span>
            )}
          </div>
        )}
      </div>

      {/* Tab navigation */}
      <nav className="flex border-b border-border mb-6">
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
              className={`px-4 py-2 font-mono text-sm border-b-2 -mb-px transition-colors ${
                isActive
                  ? 'border-primary text-text-bright'
                  : 'border-transparent text-text-muted hover:text-text-secondary'
              }`}
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
