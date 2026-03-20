'use client';

import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { AgentAvatar } from '@/components/collective/agent-avatar';
import { StatsBar } from '@/components/collective/stats-bar';
import { ActivityFeed } from '@/components/collective/activity-feed';
import { useCollectiveHealth, useCollectiveEvents } from '@/hooks/use-collective';
import { AGENTS } from '@/lib/agents';

export default function CollectivePage() {
  const { data: health, isLoading: healthLoading } = useCollectiveHealth();
  const { data: events, isLoading: eventsLoading } = useCollectiveEvents(20);

  return (
    <div className="space-y-6">
      <StatsBar health={health} isLoading={healthLoading} />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Agent Status Grid */}
        <div className="lg:col-span-2">
          <div className="grid grid-cols-3 gap-3">
            {Object.values(AGENTS).map((agent) => (
              <Link key={agent.id} href={`/collective/agents/${agent.id}`}>
                <Card className="flex items-center gap-3 p-4 transition-colors hover:bg-bg-hover cursor-pointer">
                  <AgentAvatar agentId={agent.id} size="md" showStatus status="idle" />
                  <div className="min-w-0">
                    <p className="font-mono text-sm font-medium text-text-bright truncate">
                      {agent.displayName}
                    </p>
                    <p className="font-mono text-[10px] text-text-muted">{agent.role}</p>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* Activity Feed */}
        <div>
          <ActivityFeed events={events} isLoading={eventsLoading} />
        </div>
      </div>
    </div>
  );
}
