"""B5: Graph Reachability (Depth/Algorithmic Gap -- NC^1/NL boundary).

Task: Determine if there is a path from node s to node t in a directed graph.

Complexity: STCON in NL (NL-complete). If TC^0 != NL, no constant-depth
transformer can solve this.
Prediction: Accuracy degrades with graph diameter. CoT helps but requires
Omega(d) steps for diameter-d graphs.
"""

import random as _random
from collections import deque

TASK_NAME = "B5_graph_reachability"
DIFFICULTY_PARAMS: dict[int, int] = {1: 5, 2: 10, 3: 20, 4: 50, 5: 100}


def _bfs_reachable(adj: dict[int, list[int]], source: int, target: int) -> bool:
    """Check if target is reachable from source using BFS."""
    visited: set[int] = set()
    queue: deque[int] = deque([source])
    visited.add(source)
    while queue:
        node = queue.popleft()
        if node == target:
            return True
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False


def _generate_graph(
    rng: _random.Random, n: int, ensure_path: bool, source: int, target: int
) -> list[tuple[int, int]]:
    """Generate a random directed graph.

    Uses Erdos-Renyi model with edge probability tuned to create
    interesting instances (not too sparse, not too dense).

    If ensure_path is True, plants a path from source to target.
    """
    # Edge probability: aim for average degree ~ log(n) + 1
    import math
    p = min(0.3, (math.log(n) + 1) / n)

    edges: set[tuple[int, int]] = set()

    if ensure_path:
        # Plant a path of random intermediate nodes
        path_len = rng.randint(2, min(n - 1, max(2, n // 3)))
        intermediates = rng.sample(
            [x for x in range(1, n + 1) if x != source and x != target],
            min(path_len - 1, n - 2),
        )
        path = [source] + intermediates + [target]
        for j in range(len(path) - 1):
            edges.add((path[j], path[j + 1]))

    # Add random edges
    for u in range(1, n + 1):
        for v in range(1, n + 1):
            if u != v and (u, v) not in edges:
                if rng.random() < p:
                    edges.add((u, v))

    return sorted(edges)


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate graph reachability instances.

    Generates a balanced mix of reachable and unreachable instances.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls number of nodes).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    n = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        # Choose source and target
        source = rng.randint(1, n)
        target = rng.randint(1, n)
        while target == source:
            target = rng.randint(1, n)

        # Alternate between ensuring and not ensuring a path
        ensure_path = (i % 2 == 0)
        edges = _generate_graph(rng, n, ensure_path, source, target)

        # Build adjacency list and compute ground truth
        adj: dict[int, list[int]] = {}
        for u, v in edges:
            adj.setdefault(u, []).append(v)

        reachable = _bfs_reachable(adj, source, target)
        answer = "Yes" if reachable else "No"

        # Format edges for prompt
        if len(edges) <= 50:
            edge_str = ", ".join(f"{u}->{v}" for u, v in edges)
        else:
            # For large graphs, show edges in a more compact format
            edge_str = ", ".join(f"{u}->{v}" for u, v in edges[:50])
            edge_str += f", ... ({len(edges)} edges total)"
            # Actually, show all edges -- the model needs them
            edge_str = ", ".join(f"{u}->{v}" for u, v in edges)

        prompt = (
            f"Consider a directed graph with {n} nodes (labeled 1 to {n}) "
            f"and the following edges:\n"
            f"{edge_str}\n\n"
            f"Is there a directed path from node {source} to node {target}?\n"
            f"Answer with just 'Yes' or 'No'."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "n_nodes": n,
                "n_edges": len(edges),
                "source": source,
                "target": target,
                "reachable": reachable,
            },
        })

    return instances
