// Forum
export type PostType = 'proposal' | 'debate' | 'signal' | 'prediction' | 'reply' | 'synthesis';
export type ThreadStatus = 'open' | 'resolved' | 'archived';
export type VotePosition = 'support' | 'oppose' | 'abstain';

export interface ForumThread {
  id: string;
  thread_id: string;
  author: string;
  post_type: PostType;
  title: string;
  status: ThreadStatus;
  created_at: string;
  reply_count: number;
  vote_count: number;
  last_activity: string;
  depth: number;
}

export interface ForumPost {
  id: string;
  thread_id: string;
  parent_id: string | null;
  author: string;
  post_type: PostType;
  title: string | null;
  body: string;
  status: ThreadStatus;
  created_at: string;
}

export interface ForumVote {
  id: string;
  thread_id: string;
  voter: string;
  position: VotePosition;
  rationale: string;
  confidence: number;
  created_at: string;
}

export interface ThreadDetail {
  thread: ForumThread;
  posts: ForumPost[];
  votes: ForumVote[];
}

export interface ForumStats {
  by_agent: { agent: string; post_count: number; threads_participated: number }[];
  summary: {
    total_threads: number;
    open_threads: number;
    total_posts: number;
    posts_last_24h: number;
  };
}

// Predictions
export interface Prediction {
  id: string;
  author: string;
  claim: string;
  probability: number;
  category: string;
  outcome: boolean | null;
  resolved_at: string | null;
  resolved_by: string | null;
  created_at: string;
}

export interface CalibrationBucket {
  bucket_start: number;
  bucket_end: number;
  predicted_avg: number;
  actual_avg: number;
  count: number;
}

export interface CalibrationData {
  agent: string;
  brier_score: number;
  total_resolved: number;
  by_bucket: CalibrationBucket[];
  by_category: { category: string; brier: number; count: number }[];
}

export interface CalibrationLeaderboardEntry {
  agent: string;
  brier_score: number;
  total_resolved: number;
  rank: number;
}

// Agent State
export interface AgentRelationship {
  agent: string;
  trust: number;
  agreement_rate: number;
  interactions: number;
}

export interface LearningEntry {
  lesson: string;
  source: string;
  category: string;
  added_at: string;
}

export interface AgentState {
  agent: string;
  relationships: AgentRelationship[];
  learned: LearningEntry[];
  calibration: { brier_score: number; total_predictions: number };
  interaction_stats: { total_posts: number; total_votes: number; threads_started: number };
}

// Graph
export interface AgentGraphNode {
  id: string;
  displayName: string;
  role: string;
  color: string;
}

export interface AgentGraphEdge {
  source: string;
  target: string;
  trust: number;
  agreement_rate: number;
  interactions: number;
}

export interface AgentGraph {
  nodes: AgentGraphNode[];
  edges: AgentGraphEdge[];
}

// Collective Health
export interface CollectiveHealth {
  active_threads: number;
  pending_proposals: number;
  unread_messages: number;
  upcoming_rituals: number;
  unresolved_predictions: number;
  open_governance: number;
  posts_last_24h: number;
  collective_spend_today: number;
}

// Domain Events
export interface DomainEvent {
  id: string;
  event_type: string;
  agent?: string;
  payload: Record<string, unknown>;
  created_at: string;
}
