'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
  ChevronDown,
  ChevronUp,
  Menu,
  X,
} from 'lucide-react';
import { useProjects, usePendingTriggers, useCollectiveHealth } from '@/hooks';
import { StatusDot } from '@/components/ui/status-dot';
import type { StatusKey } from '@/lib/constants';
import { AGENTS } from '@/lib/agents';
import { NAV_ITEMS } from '@/lib/nav-items';

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

export function AppSidebar() {
  const pathname = usePathname();
  const { data: projects } = useProjects();
  const { data: triggers } = usePendingTriggers();
  const { data: collectiveHealth } = useCollectiveHealth();
  const [projectsExpanded, setProjectsExpanded] = useState(true);
  const [agentsExpanded, setAgentsExpanded] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed left-4 top-3 z-50 p-1 text-text-muted hover:text-text md:hidden"
        aria-label="Toggle sidebar"
      >
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed left-0 top-0 z-40 flex h-screen w-[220px] flex-col border-r border-border bg-bg',
          'transition-transform duration-200 md:relative md:translate-x-0',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Logo */}
        <div className="flex h-[49px] items-center border-b border-border px-5">
          <Link
            href="/"
            className="font-mono text-sm font-bold text-text-bright hover:no-underline"
          >
            deepwork
          </Link>
        </div>

        {/* Main nav */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-0.5">
            {NAV_ITEMS.map(({ label, href, icon: Icon }) => {
              const isActive =
                pathname === href || (href !== '/dashboard' && pathname.startsWith(href));

              return (
                <li key={href}>
                  <Link
                    href={href}
                    onClick={() => setMobileOpen(false)}
                    className={clsx(
                      'flex items-center gap-3 rounded-none px-3 py-2 font-mono text-xs transition-colors hover:no-underline',
                      isActive
                        ? 'bg-bg-elevated text-text-bright'
                        : 'text-text-secondary hover:bg-bg-hover hover:text-text',
                    )}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    <span className="flex-1">{label}</span>
                    {label === 'Dashboard' && triggers && triggers.length > 0 && (
                      <span className="inline-flex items-center justify-center h-4 min-w-4 px-1 font-mono text-[9px] font-bold bg-[--color-status-warn-muted] text-[--color-status-warn] border border-[--color-status-warn-border]">
                        {triggers.length}
                      </span>
                    )}
                    {label === 'Collective' && collectiveHealth && collectiveHealth.unread_messages > 0 && (
                      <span className="inline-flex items-center justify-center h-4 min-w-4 px-1 font-mono text-[9px] font-bold bg-[--color-status-error-muted] text-[--color-status-error] border border-[--color-status-error-border]">
                        {collectiveHealth.unread_messages}
                      </span>
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>

          {/* Project list */}
          <div className="mt-6">
            <button
              onClick={() => setProjectsExpanded(!projectsExpanded)}
              className="flex w-full items-center justify-between px-3 py-1.5 font-mono text-[10px] font-medium uppercase tracking-wider text-text-muted hover:text-text-secondary"
            >
              Projects
              {projectsExpanded ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </button>

            {projectsExpanded && projects && (
              <ul className="mt-1 space-y-0.5">
                {projects.map((project) => {
                  const projectHref = `/projects/${project.name}`;
                  const isActive = pathname === projectHref;

                  return (
                    <li key={project.id}>
                      <Link
                        href={projectHref}
                        onClick={() => setMobileOpen(false)}
                        className={clsx(
                          'flex items-center gap-2.5 px-3 py-1.5 font-mono text-xs transition-colors hover:no-underline',
                          isActive
                            ? 'bg-bg-elevated text-text-bright'
                            : 'text-text-secondary hover:bg-bg-hover hover:text-text',
                        )}
                      >
                        <StatusDot status={mapStatusToKey(project.status)} />
                        <span className="truncate">{project.name}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* Agents list */}
          <div className="mt-4">
            <button
              onClick={() => setAgentsExpanded(!agentsExpanded)}
              className="flex w-full items-center justify-between px-3 py-1.5 font-mono text-[10px] font-medium uppercase tracking-wider text-text-muted hover:text-text-secondary"
            >
              Agents
              {agentsExpanded ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </button>

            {agentsExpanded && (
              <ul className="mt-1 space-y-0.5">
                {Object.values(AGENTS).map((agent) => {
                  const agentHref = `/collective/agents/${agent.id}`;
                  const isActive = pathname === agentHref;

                  return (
                    <li key={agent.id}>
                      <Link
                        href={agentHref}
                        onClick={() => setMobileOpen(false)}
                        className={clsx(
                          'flex items-center gap-2.5 px-3 py-1.5 font-mono text-xs transition-colors hover:no-underline',
                          isActive
                            ? 'bg-bg-elevated text-text-bright'
                            : 'text-text-secondary hover:bg-bg-hover hover:text-text',
                        )}
                      >
                        <span
                          className="inline-block h-2 w-2 shrink-0"
                          style={{ backgroundColor: agent.color, borderRadius: '50%' }}
                        />
                        <span className="truncate">{agent.displayName}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </nav>

        {/* Footer */}
        <div className="border-t border-border px-5 py-3">
          <span className="font-mono text-[10px] text-text-muted">v0.1.0</span>
        </div>
      </aside>
    </>
  );
}
