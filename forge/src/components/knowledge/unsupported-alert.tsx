import type { UnsupportedClaim } from '@/lib/knowledge-types';

interface UnsupportedAlertProps {
  unsupported: UnsupportedClaim[];
}

export function UnsupportedAlert({ unsupported }: UnsupportedAlertProps) {
  if (unsupported.length === 0) return null;

  return (
    <div className="space-y-2">
      <span className="text-text-muted">{unsupported.length} unsupported claim(s)</span>
      {unsupported.map((u) => (
        <div key={u.claim.id} className="border-b border-border py-1.5 last:border-0 last:pb-0 first:pt-0">
          <span className="text-text-secondary">{u.claim.statement}</span>
          <span className="text-text-muted block">{u.reason}</span>
        </div>
      ))}
    </div>
  );
}
