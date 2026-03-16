# knowledge

Read and write claims to the project knowledge graph. Provides persistent semantic memory across agent sessions.

## Usage
Used by all agents to record findings, query existing knowledge, and check for contradictions before making claims.

## Functions

### Add a claim
```bash
./scripts/knowledge.sh add <project> <claim_type> "<statement>" [confidence] [source]
```
- `claim_type`: hypothesis, finding, definition, proof, citation, method, result, observation, decision, question
- `confidence`: 0.0-1.0 (default 0.5)
- `source`: file path, DOI, or description of where this claim originates

### Query (semantic search)
```bash
./scripts/knowledge.sh query <project> "<natural language question>" [limit]
```
Returns the most semantically similar claims. Default limit: 10.

### List claims by type
```bash
./scripts/knowledge.sh list <project> [claim_type]
```

### Add a relation between claims
```bash
./scripts/knowledge.sh relate <source_id> <target_id> <relation> [evidence]
```
- `relation`: supports, contradicts, derives_from, cited_in, supersedes, refines, depends_on, related_to

### Find contradictions
```bash
./scripts/knowledge.sh contradictions <project>
```

### Find unsupported claims
```bash
./scripts/knowledge.sh unsupported <project>
```

### Get evidence chain
```bash
./scripts/knowledge.sh evidence <claim_id>
```

### Get knowledge graph stats
```bash
./scripts/knowledge.sh stats
```

## Examples
```bash
# Record an eval finding
./scripts/knowledge.sh add reasoning-gaps finding \
  "Claude Sonnet 4.6 achieves 0.72 accuracy on B3 serial tasks under short_cot condition" \
  0.95 "eval_runs/abc123"

# Search for what we know about CoT
./scripts/knowledge.sh query reasoning-gaps "chain of thought effectiveness on depth tasks" 15

# Record a contradiction
./scripts/knowledge.sh relate <claim_a_id> <claim_b_id> contradicts \
  "B2 budget_cot shows negative lift, but framework predicts positive"

# Check what's unsupported
./scripts/knowledge.sh unsupported reasoning-gaps
```

## Notes
- Duplicate detection runs automatically on add — if a near-duplicate exists (cosine distance < 0.05), the existing claim is returned instead.
- Always check for existing claims before adding new ones.
- Set confidence explicitly: 0.9+ for empirical results, 0.7 for well-supported findings, 0.5 for hypotheses, 0.3 for speculative observations.
