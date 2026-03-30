'use client';

import type { KnowledgeSubgraph, ClaimType, RelationType } from '@/lib/knowledge-types';

interface KnowledgeGraphVizProps {
  subgraph: KnowledgeSubgraph;
  selectedId?: string;
  onSelectClaim?: (id: string) => void;
}

function nodeColor(type: ClaimType): string {
  switch (type) {
    case 'hypothesis':
    case 'question':
      return '#f59e0b';
    case 'finding':
    case 'result':
    case 'proof':
      return '#10b981';
    case 'definition':
    case 'method':
    case 'citation':
      return '#737373';
    case 'observation':
    case 'decision':
      return '#a1a1a1';
  }
}

function edgeColor(type: RelationType): string {
  switch (type) {
    case 'supports':
      return '#10b981';
    case 'contradicts':
      return '#ef4444';
    case 'derives_from':
      return '#60a5fa';
    default:
      return '#525252';
  }
}

function edgeDash(type: RelationType): string | undefined {
  return type === 'contradicts' ? '4 2' : undefined;
}

export function KnowledgeGraphViz({ subgraph, selectedId, onSelectClaim }: KnowledgeGraphVizProps) {
  const { claims, relations } = subgraph;
  const cx = 280;
  const cy = 240;
  const ring1 = 120;
  const ring2 = 220;

  // Build adjacency from relations
  const connected = new Set<string>();
  for (const rel of relations) {
    if (rel.source_id === selectedId) connected.add(rel.target_id);
    if (rel.target_id === selectedId) connected.add(rel.source_id);
  }

  // Partition claims into center, depth-1, depth-2
  const center = claims.find((c) => c.id === selectedId);
  const depth1 = claims.filter((c) => c.id !== selectedId && connected.has(c.id));
  const depth2 = claims.filter((c) => c.id !== selectedId && !connected.has(c.id));

  // Position map
  const posMap = new Map<string, { x: number; y: number }>();

  if (center) {
    posMap.set(center.id, { x: cx, y: cy });
  }

  depth1.forEach((claim, i) => {
    const angle = (2 * Math.PI * i) / depth1.length - Math.PI / 2;
    posMap.set(claim.id, {
      x: cx + ring1 * Math.cos(angle),
      y: cy + ring1 * Math.sin(angle),
    });
  });

  depth2.forEach((claim, i) => {
    const angle = (2 * Math.PI * i) / depth2.length - Math.PI / 2;
    posMap.set(claim.id, {
      x: cx + ring2 * Math.cos(angle),
      y: cy + ring2 * Math.sin(angle),
    });
  });

  return (
    <svg viewBox="0 0 560 480" className="w-full h-auto">
      {/* Edges */}
      {relations.map((rel) => {
        const from = posMap.get(rel.source_id);
        const to = posMap.get(rel.target_id);
        if (!from || !to) return null;
        return (
          <line
            key={rel.id}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke={edgeColor(rel.relation_type)}
            strokeWidth={1.5}
            strokeDasharray={edgeDash(rel.relation_type)}
            opacity={0.6}
          />
        );
      })}

      {/* Nodes */}
      {claims.map((claim) => {
        const pos = posMap.get(claim.id);
        if (!pos) return null;
        const color = nodeColor(claim.type);
        const isCenter = claim.id === selectedId;
        const size = isCenter ? 22 : 18;
        const label = claim.statement.slice(0, 12);

        return (
          <g
            key={claim.id}
            className="cursor-pointer"
            onClick={() => onSelectClaim?.(claim.id)}
          >
            <rect
              x={pos.x - size}
              y={pos.y - size}
              width={size * 2}
              height={size * 2}
              fill="#0a0a0a"
              stroke={color}
              strokeWidth={isCenter ? 3 : 2}
            />
            <text
              x={pos.x}
              y={pos.y + 1}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#e5e5e5"
              fontSize={11}
              fontFamily="IBM Plex Mono"
              fontWeight={600}
            >
              {claim.type.slice(0, 3).toUpperCase()}
            </text>
            <text
              x={pos.x}
              y={pos.y + size + 12}
              textAnchor="middle"
              fill="#a1a1a1"
              fontSize={9}
              fontFamily="IBM Plex Mono"
            >
              {label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
