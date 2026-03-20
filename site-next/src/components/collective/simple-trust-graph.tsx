'use client';

import { getAgent } from '@/lib/agents';
import type { AgentGraph } from '@/lib/collective-types';

interface SimpleTrustGraphProps {
  graph: AgentGraph;
}

export function SimpleTrustGraph({ graph }: SimpleTrustGraphProps) {
  const { nodes, edges } = graph;
  const cx = 280;
  const cy = 240;
  const radius = 180;

  // Position nodes in a circle
  const positions = nodes.map((node, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
    return {
      ...node,
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  });

  const posMap = new Map(positions.map((p) => [p.id, { x: p.x, y: p.y }]));

  return (
    <svg viewBox="0 0 560 480" className="w-full h-auto">
      {/* Edges */}
      {edges.map((edge) => {
        const from = posMap.get(edge.source);
        const to = posMap.get(edge.target);
        if (!from || !to) return null;
        const color = edge.trust >= 0.75 ? '#10b981' : edge.trust >= 0.5 ? '#f59e0b' : '#ef4444';
        return (
          <line
            key={`${edge.source}-${edge.target}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke={color}
            strokeWidth={1.5}
            opacity={Math.max(0.15, edge.trust)}
          />
        );
      })}

      {/* Nodes */}
      {positions.map((node) => {
        const agent = getAgent(node.id);
        const color = agent?.color ?? '#737373';
        const label = agent?.displayName ?? node.id;

        return (
          <g key={node.id}>
            <rect
              x={node.x - 18}
              y={node.y - 18}
              width={36}
              height={36}
              fill="#0a0a0a"
              stroke={color}
              strokeWidth={2}
            />
            <text
              x={node.x}
              y={node.y + 1}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#e5e5e5"
              fontSize={11}
              fontFamily="IBM Plex Mono"
              fontWeight={600}
            >
              {label.slice(0, 2).toUpperCase()}
            </text>
            <text
              x={node.x}
              y={node.y + 30}
              textAnchor="middle"
              fill="#a1a1a1"
              fontSize={10}
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
