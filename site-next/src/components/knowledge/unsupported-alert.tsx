import { AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import type { UnsupportedClaim } from '@/lib/knowledge-types';

interface UnsupportedAlertProps {
  unsupported: UnsupportedClaim[];
}

export function UnsupportedAlert({ unsupported }: UnsupportedAlertProps) {
  if (unsupported.length === 0) return null;

  return (
    <Card className="border-l-4 border-l-[#f97316]">
      <div className="flex items-center gap-2 mb-3">
        <AlertCircle className="h-4 w-4 text-[#f97316]" />
        <span className="font-mono text-sm font-semibold text-text-bright">Unsupported Claims</span>
        <span className="font-mono text-[10px] text-text-muted">{unsupported.length}</span>
      </div>

      <ul className="space-y-3">
        {unsupported.map((u) => (
          <li key={u.claim.id} className="space-y-1">
            <p className="font-mono text-xs text-text-secondary line-clamp-2">
              {u.claim.statement}
            </p>
            <p className="font-mono text-[10px] text-text-muted">{u.reason}</p>
          </li>
        ))}
      </ul>
    </Card>
  );
}
