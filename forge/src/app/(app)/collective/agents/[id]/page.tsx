'use client';

import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { AgentAvatar } from '@/components/collective/agent-avatar';
import { RelationshipCard } from '@/components/collective/relationship-card';
import { PredictionCard } from '@/components/collective/prediction-card';
import { CalibrationChart } from '@/components/collective/calibration-chart';
import { ThreadCard } from '@/components/collective/thread-card';
import { MessageCard } from '@/components/collective/message-card';
import { MentionCard } from '@/components/collective/mention-card';
import {
  useAgentState,
  useAgentPredictions,
  useCalibration,
  useForumThreads,
} from '@/hooks/use-collective';
import { useInbox, useMentions, useMessageStats } from '@/hooks/use-messages';
import { getAgent } from '@/lib/agents';
import { CreatePredictionDialog } from '@/components/collective/create-prediction-dialog';
import { ResolvePredictionDialog } from '@/components/collective/resolve-prediction-dialog';
import { Users, Target, MessageSquare, BookOpen, Mail } from 'lucide-react';

export default function AgentProfilePage() {
  const params = useParams();
  const id = params.id as string;
  const agent = getAgent(id);

  const { data: state, isLoading: stateLoading } = useAgentState(id);
  const { data: predictions, isLoading: predsLoading } = useAgentPredictions(id);
  const { data: calibration } = useCalibration(id);
  const { data: threads } = useForumThreads({ author: id });
  const { data: inbox } = useInbox(id);
  const { data: mentions } = useMentions(id);
  const { data: msgStats } = useMessageStats(id);

  if (!agent) {
    return <EmptyState icon={Users} message={`Agent "${id}" not found`} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="flex items-center gap-4">
        <AgentAvatar agentId={id} size="lg" showStatus status="idle" />
        <div>
          <h2 className="font-mono text-xl font-semibold text-text-bright">{agent.displayName}</h2>
          <p className="font-mono text-sm text-text-secondary">{agent.role}</p>
          <p className="font-mono text-[10px] text-text-muted">{agent.model}</p>
        </div>
        {state && (
          <div className="ml-auto flex gap-6">
            <div className="text-center">
              <p className="font-mono text-lg font-bold text-text-bright tabular-nums">
                {state.interaction_stats?.total_posts ?? 0}
              </p>
              <p className="font-mono text-[10px] text-text-muted">Posts</p>
            </div>
            <div className="text-center">
              <p className="font-mono text-lg font-bold text-text-bright tabular-nums">
                {state.interaction_stats?.total_votes ?? 0}
              </p>
              <p className="font-mono text-[10px] text-text-muted">Votes</p>
            </div>
            <div className="text-center">
              <p className="font-mono text-lg font-bold text-text-bright tabular-nums">
                {state.calibration?.brier_score?.toFixed(3) ?? '—'}
              </p>
              <p className="font-mono text-[10px] text-text-muted">Brier</p>
            </div>
          </div>
        )}
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="relationships">
        <TabsList>
          <TabsTrigger value="relationships">Relationships</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="forum">Forum</TabsTrigger>
          <TabsTrigger value="learnings">Learnings</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
        </TabsList>

        {/* Relationships */}
        <TabsContent value="relationships">
          {stateLoading ? (
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <Card key={i} className="space-y-2">
                  <Skeleton className="h-8 w-8" />
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-2 w-full" />
                </Card>
              ))}
            </div>
          ) : state?.relationships && state.relationships.length > 0 ? (
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              {state.relationships.map((rel) => (
                <RelationshipCard key={rel.agent} relationship={rel} />
              ))}
            </div>
          ) : (
            <EmptyState icon={Users} message="No relationship data" />
          )}
        </TabsContent>

        {/* Predictions */}
        <TabsContent value="predictions">
          {predsLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <Card key={i} className="space-y-2">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-2 w-full" />
                </Card>
              ))}
            </div>
          ) : (
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2 space-y-4">
                <CreatePredictionDialog />
                {predictions && predictions.length > 0 ? (
                  <>
                    {predictions.filter((p) => p.outcome === null).length > 0 && (
                      <div>
                        <p className="font-mono text-xs text-text-muted mb-2 uppercase">Unresolved</p>
                        <div className="space-y-3">
                          {predictions.filter((p) => p.outcome === null).map((p) => (
                            <div key={p.id} className="flex items-start gap-2">
                              <div className="flex-1">
                                <PredictionCard prediction={p} />
                              </div>
                              <ResolvePredictionDialog predictionId={p.id} claim={p.claim} />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {predictions.filter((p) => p.outcome !== null).length > 0 && (
                      <div>
                        <p className="font-mono text-xs text-text-muted mb-2 uppercase">Resolved</p>
                        <div className="space-y-3">
                          {predictions.filter((p) => p.outcome !== null).map((p) => (
                            <PredictionCard key={p.id} prediction={p} />
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <EmptyState icon={Target} message="No predictions" />
                )}
              </div>
              {calibration && calibration.by_bucket.length > 0 && (
                <div>
                  <CalibrationChart
                    buckets={calibration.by_bucket}
                    brierScore={calibration.brier_score}
                  />
                </div>
              )}
            </div>
          )}
        </TabsContent>

        {/* Forum */}
        <TabsContent value="forum">
          {threads && threads.length > 0 ? (
            <Card padding={false}>
              {threads.map((thread) => (
                <ThreadCard key={thread.id} thread={thread} />
              ))}
            </Card>
          ) : (
            <EmptyState icon={MessageSquare} message="No forum activity" />
          )}
        </TabsContent>

        {/* Learnings */}
        <TabsContent value="learnings">
          {state?.learned && state.learned.length > 0 ? (
            <div className="space-y-3">
              {state.learned.map((entry, i) => (
                <Card key={i} className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px] text-text-muted uppercase">
                      {entry.category}
                    </span>
                    {entry.added_at && (
                      <span className="font-mono text-[10px] text-text-muted">
                        {new Date(entry.added_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <p className="font-mono text-sm text-text-bright">{entry.lesson}</p>
                  {entry.source && (
                    <p className="font-mono text-[10px] text-text-muted">Source: {entry.source}</p>
                  )}
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState icon={BookOpen} message="No learnings recorded" />
          )}
        </TabsContent>

        {/* Messages */}
        <TabsContent value="messages">
          {msgStats && (
            <div className="grid grid-cols-4 gap-4 mb-6">
              {[
                { label: 'Sent', value: msgStats.sent },
                { label: 'Received', value: msgStats.received },
                { label: 'Unread', value: msgStats.unread },
                { label: 'Urgent', value: msgStats.urgent_unread },
              ].map((stat) => (
                <Card key={stat.label} className="text-center">
                  <p className="font-mono text-lg font-bold text-text-bright tabular-nums">{stat.value}</p>
                  <p className="font-mono text-[10px] text-text-muted">{stat.label}</p>
                </Card>
              ))}
            </div>
          )}
          {inbox && inbox.length > 0 ? (
            <div className="mb-6">
              <p className="font-mono text-xs text-text-muted mb-2 uppercase">Inbox</p>
              <Card padding={false}>
                {inbox.map((msg) => (
                  <MessageCard key={msg.id} message={msg} />
                ))}
              </Card>
            </div>
          ) : (
            <EmptyState icon={Mail} message="No messages" className="mb-6" />
          )}
          {mentions && mentions.length > 0 ? (
            <div>
              <p className="font-mono text-xs text-text-muted mb-2 uppercase">Mentions</p>
              <div className="space-y-2">
                {mentions.map((mention) => (
                  <MentionCard key={mention.id} mention={mention} />
                ))}
              </div>
            </div>
          ) : (
            <EmptyState icon={Mail} message="No mentions" />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
