import type { Contradiction } from '@/lib/knowledge-types';

interface ContradictionAlertProps {
  contradictions: Contradiction[];
}

export function ContradictionAlert({ contradictions }: ContradictionAlertProps) {
  if (contradictions.length === 0) return null;

  return (
    <div className="space-y-2">
      <span className="text-text-muted">{contradictions.length} contradiction(s)</span>
      {contradictions.map((c) => (
        <div key={c.relation.id} className="border-b border-border py-1.5 last:border-0 last:pb-0 first:pt-0">
          <span className="text-text-secondary">{c.claim_a.statement}</span>
          <span className="text-[--color-danger] block">contradicts</span>
          <span className="text-text-secondary">{c.claim_b.statement}</span>
        </div>
      ))}
    </div>
  );
}
