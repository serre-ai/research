import { Badge } from '@/components/ui/badge';
import type { ClaimType } from '@/lib/knowledge-types';

interface ClaimTypeBadgeProps {
  type: ClaimType;
}

function variantFor(type: ClaimType) {
  switch (type) {
    case 'hypothesis':
    case 'question':
      return 'warning' as const;
    case 'finding':
    case 'result':
    case 'proof':
      return 'success' as const;
    case 'definition':
    case 'method':
    case 'citation':
      return 'outline' as const;
    case 'observation':
    case 'decision':
      return 'default' as const;
  }
}

export function ClaimTypeBadge({ type }: ClaimTypeBadgeProps) {
  return (
    <Badge variant={variantFor(type)}>
      {type.charAt(0).toUpperCase() + type.slice(1)}
    </Badge>
  );
}
