export interface VerificationReport {
  id: string;
  totalClaims: number;
  verified: number;
  inconsistencies: number;
  missingEvidence: number;
  created_at?: string;
}

export interface VerificationSummary {
  id: string;
  totalClaims: number;
  verified: number;
  inconsistencies: number;
  missingEvidence: number;
}
