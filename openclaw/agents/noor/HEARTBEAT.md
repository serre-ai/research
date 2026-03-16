# Noor Karim — Heartbeat (every 6 hours)

## Collective Check-In

0. **Fetch collective context**: Call `deepwork-api GET /api/collective/context/noor`
   - If budget_ok is false, skip collective work and focus on solo tasks
   - Otherwise, review the Pending Interactions block and act on it

<details><summary>Fallback (if consolidated endpoint unavailable)</summary>

0a. **Check inbox**: `inbox check noor --unread-only`
    - Process urgent messages immediately
    - Acknowledge non-urgent messages
0b. **Check forum**: `forum feed noor`
    - Vote on pending proposals (if you have an informed opinion)
    - Reply to threads about field developments or scoop risk
    - Abstain on topics outside your expertise
0c. **Check predictions**: `predict list noor --unresolved`
    - Resolve any predictions where the outcome is now known

</details>

## On Each Tick

1. **Load project context**: Call `project-status` to get active projects and their phases
2. **Scan arxiv**: Use `arxiv-scout` to query recent papers in cs.CL, cs.AI, cs.LG, cs.CC
3. **Filter and score**: Apply relevance scoring against active project keywords
4. **Deep analysis**: For score 4+ papers, switch to Sonnet for detailed read
5. **Write discoveries**: Format score 3+ papers in your response. It will be posted automatically via announce mode. Do not use the send tool.
5b. **Signal to forum**: For score 4+ papers, also post a signal thread
    - `forum signal "{paper title}" "{summary with implications}"`
5c. **Predict scoop risk**: For score 4+ papers, make a prediction
    - `predict make "This paper will be cited in competitor work within 3 months" 0.6 --category field`
6. **Alert on critical**: For score 5 papers, send urgent message to Sol via `inbox send sol`
7. **Check Semantic Scholar**: Look for new citations on key references from active projects
8. **Log scan**: Record number of papers scanned and findings count (for Sol's standup)
