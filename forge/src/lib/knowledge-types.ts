// Knowledge Graph

export type ClaimType =
  | 'hypothesis'
  | 'finding'
  | 'definition'
  | 'proof'
  | 'citation'
  | 'method'
  | 'result'
  | 'observation'
  | 'decision'
  | 'question';

export type RelationType =
  | 'supports'
  | 'contradicts'
  | 'derives_from'
  | 'cited_in'
  | 'supersedes'
  | 'refines'
  | 'depends_on'
  | 'related_to';

export interface Claim {
  id: string;
  project: string;
  type: ClaimType;
  statement: string;
  confidence: number;
  source: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Relation {
  id: string;
  source_id: string;
  target_id: string;
  relation_type: RelationType;
  created_at: string;
}

export interface KnowledgeSubgraph {
  claims: Claim[];
  relations: Relation[];
}

export interface Contradiction {
  claim_a: Claim;
  claim_b: Claim;
  relation: Relation;
}

export interface UnsupportedClaim {
  claim: Claim;
  reason: string;
}

export interface KnowledgeStats {
  total_claims: number;
  by_type: Record<ClaimType, number>;
  total_relations: number;
  by_relation: Record<RelationType, number>;
  projects: string[];
}

export interface EvidenceChain {
  claim: Claim;
  chain: { claim: Claim; relation: Relation }[];
}
