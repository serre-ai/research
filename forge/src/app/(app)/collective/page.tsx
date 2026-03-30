'use client';

import { useRouter } from 'next/navigation';
import { TuiBox, TuiPanel, TuiList } from '@/components/tui';
import { StatsBar } from '@/components/collective/stats-bar';
import { ActivityFeed } from '@/components/collective/activity-feed';
import { useCollectiveHealth, useCollectiveEvents } from '@/hooks/use-collective';
import { AGENTS } from '@/lib/agents';

export default function CollectivePage() {
  const router = useRouter();
  const { data: health, isLoading: healthLoading } = useCollectiveHealth();
  const { data: events, isLoading: eventsLoading } = useCollectiveEvents(20);

  const agentList = Object.values(AGENTS);

  return (
    <>
      <div className="mb-3">
        <StatsBar health={health} isLoading={healthLoading} />
      </div>

      <div className="grid gap-3 lg:grid-cols-3">
        {/* Agent grid */}
        <div className="lg:col-span-2">
          <TuiPanel
            id="agents"
            title="AGENTS"
            order={1}
            itemCount={agentList.length}
          >
            <TuiList
              panelId="agents"
              items={agentList}
              keyFn={(a) => a.id}
              onActivate={(a) => {
                router.push(`/collective/agents/${a.id}`);
              }}
              renderItem={(agent, _i, active) => (
                <div className="flex items-center gap-2">
                  <span style={{ color: agent.color }}>{'●'}</span>
                  <span className={active ? 'text-text-bright' : 'text-text-secondary'}>{agent.displayName}</span>
                  <span className="text-text-muted">{agent.role}</span>
                </div>
              )}
            />
          </TuiPanel>
        </div>

        {/* Activity feed */}
        <div>
          <TuiBox title="ACTIVITY">
            <ActivityFeed events={events} isLoading={eventsLoading} />
          </TuiBox>
        </div>
      </div>
    </>
  );
}
