export type DetectorType = 'gap' | 'trend' | 'contrarian' | 'frontier' | 'reviewer' | 'portfolio';

export interface ResearchSignal {
  id: string;
  detector: DetectorType;
  signal_type: string;
  title: string;
  description: string | null;
  confidence: number;
  source_papers: string[];
  source_claims: string[];
  topics: string[];
  relevance: number;
  timing_score: number;
  metadata: Record<string, unknown>;
  batch_date: string;
  created_at: string;
}

export interface ResearchOpportunity {
  id: string;
  title: string;
  thesis: string | null;
  composite_score: number;
  signal_ids: string[];
  detectors_hit: DetectorType[];
  topics: string[];
  target_venue: string | null;
  portfolio_fit: number;
  timing_urgency: number;
  venue_receptivity: number;
  rationale: string | null;
  batch_date: string;
  status: 'new' | 'reviewed' | 'accepted' | 'rejected';
  created_at: string;
}
