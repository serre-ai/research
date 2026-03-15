# Noor — Heartbeat (every 6 hours)

## On Each Tick

1. **Load project context**: Call `project-status` to get active projects and their phases
2. **Scan arxiv**: Use `arxiv-scout` to query recent papers in cs.CL, cs.AI, cs.LG, cs.CC
3. **Filter and score**: Apply relevance scoring against active project keywords
4. **Deep analysis**: For score 4+ papers, switch to Sonnet for detailed read
5. **Post discoveries**: Send score 3+ papers to `#discoveries` in structured format
6. **Alert on critical**: For score 5 papers, also post alert to `#general` with scoop risk warning
7. **Check Semantic Scholar**: Look for new citations on key references from active projects
8. **Log scan**: Record number of papers scanned and findings count (for Sol's standup)
