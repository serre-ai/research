import { AlertTriangle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import type { Contradiction } from '@/lib/knowledge-types';

interface ContradictionAlertProps {
  contradictions: Contradiction[];
}

export function ContradictionAlert({ contradictions }: ContradictionAlertProps) {
  if (contradictions.length === 0) return null;

  return (
    <Card className="border-l-4 border-l-[--color-status-warn]">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle className="h-4 w-4 text-[--color-status-warn]" />
        <span className="font-mono text-sm font-semibold text-text-bright">Contradictions</span>
        <span className="font-mono text-[10px] text-text-muted">{contradictions.length}</span>
      </div>

      <ul className="space-y-3">
        {contradictions.map((c) => (
          <li key={c.relation.id} className="space-y-1">
            <p className="font-mono text-xs text-text-secondary line-clamp-2">
              {c.claim_a.statement}
            </p>
            <p className="font-mono text-[10px] font-medium text-[--color-status-error]">
              contradicts
            </p>
            <p className="font-mono text-xs text-text-secondary line-clamp-2">
              {c.claim_b.statement}
            </p>
          </li>
        ))}
      </ul>
    </Card>
  );
}
