export interface Digest {
  date: string;
  digest: string;
  key_events?: string[];
  filed_by: string;
  created_at: string;
}

export interface CreateDigestRequest {
  date: string;
  digest: string;
  key_events?: string[];
  filed_by: string;
}
