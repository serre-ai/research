export type ProposalStatus = 'proposed' | 'voting' | 'accepted' | 'rejected';
export type ProposalType = 'process' | 'schedule' | 'budget' | 'personnel' | 'values';

export interface Proposal {
  id: number;
  proposer: string;
  title: string;
  proposal: string;
  proposal_type: ProposalType;
  thread_id: string;
  status: ProposalStatus;
  votes_for: number;
  votes_against: number;
  votes_abstain: number;
  resolved_at: string | null;
  created_at: string;
}

export interface GovernanceTally {
  votes_for: number;
  votes_against: number;
  votes_abstain: number;
  total_votes: number;
  quorum_reached: boolean;
  outcome: string;
}

export interface GovernanceVote {
  voter: string;
  position: 'support' | 'oppose' | 'abstain';
  rationale: string;
  confidence: number;
  created_at: string;
}

export interface ProposalDetail extends Proposal {
  votes: GovernanceVote[];
  tally: GovernanceTally;
}

export interface CreateProposalRequest {
  proposer: string;
  title: string;
  proposal: string;
  proposal_type: ProposalType;
}

export interface CastVoteRequest {
  voter: string;
  position: 'support' | 'oppose' | 'abstain';
  rationale?: string;
  confidence?: number;
}
