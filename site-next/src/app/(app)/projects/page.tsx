'use client';

import Link from 'next/link';
import { FolderOpen, ArrowRight } from 'lucide-react';
import { useProjects } from '@/hooks';
import { PageHeader } from '@/components/ui/page-header';
import { Card } from '@/components/ui/card';
import { StatusDot } from '@/components/ui/status-dot';
import { StatusBadge } from '@/components/ui/status-badge';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import type { StatusKey } from '@/lib/constants';

function mapStatusToKey(status: string): StatusKey {
  switch (status) {
    case 'active':
    case 'running':
      return 'ok';
    case 'paused':
    case 'pending':
      return 'warn';
    case 'error':
    case 'failed':
      return 'error';
    default:
      return 'idle';
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function ProjectsPage() {
  const { data: projects, isLoading, error } = useProjects();

  return (
    <div>
      <PageHeader
        title="Projects"
        subtitle="All research projects"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Projects' },
        ]}
      />

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Skeleton className="h-2 w-2 rounded-full" />
                <div className="space-y-1.5">
                  <Skeleton className="h-4 w-40" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
              <Skeleton className="h-5 w-16" />
            </Card>
          ))}
        </div>
      ) : error ? (
        <Card>
          <p className="text-sm text-[--color-status-error]">
            Failed to load projects: {error.message}
          </p>
        </Card>
      ) : projects && projects.length > 0 ? (
        <div className="space-y-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/projects/${project.name}`}
              className="group block hover:no-underline"
            >
              <Card className="flex items-center justify-between transition-colors group-hover:border-border-strong">
                <div className="flex items-center gap-4">
                  <StatusDot
                    status={mapStatusToKey(project.status)}
                    pulse={project.status === 'active'}
                  />
                  <div>
                    <span className="font-mono text-sm font-semibold text-text-bright">
                      {project.name}
                    </span>
                    <div className="mt-1 flex items-center gap-2">
                      {project.phase && (
                        <Badge variant="outline">{project.phase}</Badge>
                      )}
                      <span className="font-mono text-xs text-text-muted">
                        Updated {formatDate(project.updated_at)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={mapStatusToKey(project.status)}>
                    {project.status}
                  </StatusBadge>
                  <ArrowRight className="h-4 w-4 text-text-muted opacity-0 transition-opacity group-hover:opacity-100" />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FolderOpen}
          message="No projects yet"
          description="Projects will appear here once created"
        />
      )}
    </div>
  );
}
