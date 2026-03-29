'use client';

import { useState } from 'react';
import { TuiBadge } from '@/components/tui';
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
    <div>
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="search claims..."
          className="flex-1 border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-bright placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-primary"
        />
        <button
          type="submit"
          className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-secondary hover:text-text-bright"
        >
          [search]
        </button>
      </form>

      {search.isPending && <span className="text-text-muted mt-1 block">searching...</span>}

      {search.data && search.data.length > 0 && (
        <div className="mt-2 space-y-1">
          {search.data.map((claim: Claim) => (
            <div
              key={claim.id}
              onClick={() => onSelectClaim?.(claim.id)}
              className="cursor-pointer border-b border-border py-1 last:border-0 hover:bg-bg-hover"
            >
              <div className="flex items-center gap-2">
                <TuiBadge color="accent">{claim.type}</TuiBadge>
                <span className="text-text-muted">{claim.project}</span>
              </div>
              <span className="text-text-secondary">{claim.statement.slice(0, 80)}</span>
            </div>
          ))}
        </div>
      )}

      {search.data && search.data.length === 0 && (
        <span className="text-text-muted mt-1 block">no results found</span>
      )}
    </div>
  );
}
