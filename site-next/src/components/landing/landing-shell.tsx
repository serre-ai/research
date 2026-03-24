'use client';

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { FocusProvider } from '@/providers/focus-provider';
import { TuiScreen, TuiFrame, TuiPanel, TuiList, TuiStatusDot, TuiBadge, TuiProgress } from '@/components/tui';

interface HealthData {
  status: string;
  uptime_s?: number;
  database?: { connected: boolean; latency_ms?: number };
  memory?: { percentage: number; free_mb: number; total_mb: number };
}

interface Project {
  name: string;
  title: string;
  venue?: string;
  phase?: string;
  status: string;
  confidence?: number;
}

interface Paper {
  title: string;
  subtitle?: string;
  venue: string;
  status: string;
  href?: string;
}

interface Post {
  date: string;
  title: string;
  href: string;
}

interface LandingShellProps {
  health: HealthData | null;
  projects: Project[];
  papers: Paper[];
  posts: Post[];
}

function formatUptime(s: number): string {
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  return `${d}d ${h}h`;
}

function StatusLine({ health, projectCount }: { health: HealthData | null; projectCount: number }) {
  if (!health) {
    return <div className="text-text-muted">status unavailable</div>;
  }
  const memPct = health.memory?.percentage ?? 0;
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1">
      <span className="flex items-center gap-1">
        <TuiStatusDot status={health.status === 'ok' ? 'ok' : 'error'} />
        <span className="text-text-secondary">API online</span>
      </span>
      <span className="flex items-center gap-1">
        <TuiStatusDot status={health.database?.connected ? 'ok' : 'error'} />
        <span className="text-text-secondary">
          DB {health.database?.connected ? `${health.database.latency_ms ?? '?'}ms` : 'down'}
        </span>
      </span>
      <span className="text-text-muted">{projectCount} active</span>
      {health.uptime_s != null && (
        <span className="text-text-muted">up {formatUptime(health.uptime_s)}</span>
      )}
      {health.memory && (
        <span className="flex items-center gap-1">
          <span className="text-text-muted">MEM</span>
          <TuiProgress
            value={memPct}
            width={8}
            showPercent={false}
            color={memPct > 90 ? 'error' : memPct > 70 ? 'warn' : 'ok'}
          />
          <span className="text-text-muted">{Math.round(memPct)}%</span>
        </span>
      )}
    </div>
  );
}

export function LandingShell({ health, projects, papers, posts }: LandingShellProps) {
  const router = useRouter();

  const handleProjectSelect = useCallback(
    (idx: number) => { if (projects[idx]) router.push(`/projects/${projects[idx].name}`); },
    [projects, router],
  );
  const handlePaperSelect = useCallback(
    (idx: number) => { if (papers[idx]?.href) router.push(papers[idx].href!); },
    [papers, router],
  );
  const handlePostSelect = useCallback(
    (idx: number) => { if (posts[idx]?.href) router.push(posts[idx].href); },
    [posts, router],
  );

  return (
    <FocusProvider>
      <TuiScreen>
        <TuiFrame title="DEEPWORK" titleRight="Autonomous AI Research">
          {/* Status line — not a panel, not focusable */}
          <div className="mb-3">
            <StatusLine health={health} projectCount={projects.length} />
          </div>

          {/* Two-column: Projects | Papers */}
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 mb-3">
            <TuiPanel
              id="projects"
              title="PROJECTS"
              order={1}
              itemCount={projects.length}
              onActivateItem={handleProjectSelect}
            >
              <TuiList
                panelId="projects"
                items={projects}
                emptyMessage="no active projects"
                renderItem={(p, _i, active) => (
                  <div className="flex items-center justify-between gap-2">
                    <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                      {p.name}
                    </span>
                    <span className="flex items-center gap-2">
                      {p.venue && <span className="text-text-muted">{p.venue}</span>}
                      <TuiBadge color="accent">{p.phase ?? p.status}</TuiBadge>
                    </span>
                  </div>
                )}
              />
            </TuiPanel>

            <TuiPanel
              id="papers"
              title="PAPERS"
              order={2}
              itemCount={papers.length}
              onActivateItem={handlePaperSelect}
            >
              <TuiList
                panelId="papers"
                items={papers}
                emptyMessage="no papers"
                renderItem={(p, _i, active) => (
                  <div>
                    <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                      {p.title}
                    </span>
                    <div className="text-text-muted">
                      {p.venue}{' '}
                      <TuiBadge color={p.status === 'Pre-Print' ? 'ok' : 'accent'}>
                        {p.status.toUpperCase()}
                      </TuiBadge>
                    </div>
                  </div>
                )}
              />
            </TuiPanel>
          </div>

          {/* Log — full width */}
          <TuiPanel
            id="log"
            title="LOG"
            order={3}
            itemCount={posts.length}
            onActivateItem={handlePostSelect}
          >
            <TuiList
              panelId="log"
              items={posts}
              emptyMessage="no posts"
              renderItem={(post, _i, active) => (
                <div className="flex items-baseline gap-4">
                  <span className="text-text-muted tabular-nums shrink-0">{post.date}</span>
                  <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                    {post.title}
                  </span>
                </div>
              )}
            />
          </TuiPanel>
        </TuiFrame>
      </TuiScreen>
    </FocusProvider>
  );
}
