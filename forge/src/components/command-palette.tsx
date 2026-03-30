'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Command } from 'cmdk';
import { NAV_ITEMS } from '@/lib/nav-items';
import { AGENTS } from '@/lib/agents';
import { useProjects } from '@/hooks';

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const { data: projects } = useProjects();

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    }
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  const navigate = useCallback(
    (href: string) => {
      setOpen(false);
      router.push(href);
    },
    [router],
  );

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60" onClick={() => setOpen(false)}>
      <div
        className="fixed left-1/2 top-[20%] z-50 w-full max-w-lg -translate-x-1/2"
        onClick={(e) => e.stopPropagation()}
      >
        <Command
          className="border border-border bg-bg-elevated font-mono text-text shadow-lg"
          label="Command palette"
        >
          <Command.Input
            placeholder="Type a command..."
            className="w-full border-b border-border bg-transparent px-4 py-3 font-mono text-sm text-text-bright outline-none placeholder:text-text-muted"
          />
          <Command.List className="max-h-[320px] overflow-y-auto p-2">
            <Command.Empty className="px-4 py-6 text-center font-mono text-xs text-text-muted">
              No results found.
            </Command.Empty>

            <Command.Group
              heading="Navigation"
              className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:font-mono [&_[cmdk-group-heading]]:text-[10px] [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:uppercase [&_[cmdk-group-heading]]:tracking-wider [&_[cmdk-group-heading]]:text-text-muted"
            >
              {NAV_ITEMS.map((item) => (
                <Command.Item
                  key={item.href}
                  value={item.label}
                  onSelect={() => navigate(item.href)}
                  className="flex cursor-pointer items-center gap-3 px-3 py-2 font-mono text-xs text-text-secondary data-[selected=true]:bg-bg-hover data-[selected=true]:text-text-bright"
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  {item.label}
                </Command.Item>
              ))}
            </Command.Group>

            {projects && projects.length > 0 && (
              <Command.Group
                heading="Projects"
                className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:font-mono [&_[cmdk-group-heading]]:text-[10px] [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:uppercase [&_[cmdk-group-heading]]:tracking-wider [&_[cmdk-group-heading]]:text-text-muted"
              >
                {projects.map((project) => (
                  <Command.Item
                    key={project.id}
                    value={`project ${project.name}`}
                    onSelect={() => navigate(`/projects/${project.name}`)}
                    className="flex cursor-pointer items-center gap-3 px-3 py-2 font-mono text-xs text-text-secondary data-[selected=true]:bg-bg-hover data-[selected=true]:text-text-bright"
                  >
                    <span className="inline-block h-2 w-2 shrink-0 bg-text-muted" />
                    {project.name}
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            <Command.Group
              heading="Agents"
              className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:font-mono [&_[cmdk-group-heading]]:text-[10px] [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:uppercase [&_[cmdk-group-heading]]:tracking-wider [&_[cmdk-group-heading]]:text-text-muted"
            >
              {Object.values(AGENTS).map((agent) => (
                <Command.Item
                  key={agent.id}
                  value={`agent ${agent.displayName} ${agent.role}`}
                  onSelect={() => navigate(`/collective/agents/${agent.id}`)}
                  className="flex cursor-pointer items-center gap-3 px-3 py-2 font-mono text-xs text-text-secondary data-[selected=true]:bg-bg-hover data-[selected=true]:text-text-bright"
                >
                  <span
                    className="inline-block h-2 w-2 shrink-0 rounded-full"
                    style={{ backgroundColor: agent.color }}
                  />
                  <span>{agent.displayName}</span>
                  <span className="text-text-muted">{agent.role}</span>
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>

          <div className="border-t border-border px-4 py-2">
            <span className="font-mono text-[10px] text-text-muted">
              esc to close &middot; &uarr;&darr; to navigate &middot; enter to select
            </span>
          </div>
        </Command>
      </div>
    </div>
  );
}
