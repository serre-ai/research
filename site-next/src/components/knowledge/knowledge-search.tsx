'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
import { ClaimTypeBadge } from './claim-type-badge';
import { useKnowledgeSearch } from '@/hooks/use-knowledge-mutations';
import type { Claim } from '@/lib/knowledge-types';

interface KnowledgeSearchProps {
  onSelectClaim?: (id: string) => void;
}

export function KnowledgeSearch({ onSelectClaim }: KnowledgeSearchProps) {
  const [query, setQuery] = useState('');
  const search = useKnowledgeSearch();

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    search.mutate({ query: query.trim() });
  }

  return (
    <div className="space-y-3">
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-muted" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search knowledge..."
            className="w-full bg-bg border border-border pl-8 pr-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
          />
        </div>
      </form>
      {search.isPending && (
        <p className="font-mono text-xs text-text-muted">Searching...</p>
      )}
      {search.data && search.data.length > 0 && (
        <div className="space-y-2">
          {search.data.map((claim: Claim) => (
            <div
              key={claim.id}
              onClick={() => onSelectClaim?.(claim.id)}
              className="p-3 border border-border bg-bg-elevated cursor-pointer hover:border-primary transition-colors"
            >
              <div className="flex items-center gap-2 mb-1">
                <ClaimTypeBadge type={claim.type} />
                <span className="font-mono text-[10px] text-text-muted">{claim.project}</span>
              </div>
              <p className="font-mono text-xs text-text-secondary line-clamp-2">{claim.statement}</p>
            </div>
          ))}
        </div>
      )}
      {search.data && search.data.length === 0 && (
        <p className="font-mono text-xs text-text-muted">No results found.</p>
      )}
    </div>
  );
}
