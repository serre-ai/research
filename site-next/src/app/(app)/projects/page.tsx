'use client';

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useProjects } from '@/hooks';
import { TuiPanel, TuiList, TuiStatusDot, TuiBadge, TuiProgress } from '@/components/tui';
import { mapStatusToKey } from '@/lib/dashboard-helpers';

export default function ProjectsPage() {
  const router = useRouter();
  const { data: projects, isLoading, error } = useProjects();

  const projectList = projects ?? [];

  const navigateToProject = useCallback(
    (p: (typeof projectList)[number]) => router.push(`/projects/${p.name}`),
    [router],
  );

  return (
    <TuiPanel
      id="projects"
      title="PROJECTS"
      order={1}
      itemCount={projectList.length}
      onActivateItem={(idx) => navigateToProject(projectList[idx])}
    >
      {error ? (
        <span className="text-[--color-status-error]">
          failed to load: {error.message ?? 'error'}
        </span>
      ) : (
        <TuiList
          panelId="projects"
          items={projectList}
          keyFn={(p) => p.id}
          onActivate={navigateToProject}
          emptyMessage={isLoading ? 'loading...' : 'no projects'}
          renderItem={(p, _i, active) => (
            <div className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-2">
                <TuiStatusDot status={mapStatusToKey(p.status)} />
                <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                  {p.name}
                </span>
              </span>
              <span className="flex items-center gap-2">
                {p.focus && (
                  <span className="text-text-muted text-xs hidden sm:inline">{p.focus}</span>
                )}
                <TuiBadge color="accent">{p.phase ?? p.status}</TuiBadge>
                {p.confidence != null && (
                  <TuiProgress
                    value={Math.round(p.confidence * 100)}
                    width={6}
                    showPercent={false}
                    color={p.confidence > 0.7 ? 'ok' : p.confidence > 0.3 ? 'warn' : 'error'}
                  />
                )}
              </span>
            </div>
          )}
        />
      )}
    </TuiPanel>
  );
}
