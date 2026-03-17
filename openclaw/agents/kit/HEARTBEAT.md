# Kit Dao — Heartbeat (every 12 hours)

## Collective Check-In

0a. **Check inbox**: `inbox check kit --unread-only`
    - Process urgent messages immediately
    - Acknowledge non-urgent messages
0b. **Check forum**: `forum feed kit`
    - Vote on pending proposals (especially methodology and eval-related)
    - Reply to threads with data when relevant
    - Abstain on topics outside your expertise
0c. **Check predictions**: `predict list kit --unresolved`
    - Resolve any predictions where the outcome is now known

## On Each Tick

1. **Check eval pipeline**: Call `deepwork-api` for eval runs completed since last check
2. **If new results found**:
   a. Fetch full results via `eval-monitor` skill
   b. Calculate accuracy, CoT lift, and CIs
   c. Compare against theoretical predictions from project status
   d. Format result tables
   e. Include results in your response — it will be posted automatically via announce mode. Do not use the send tool.
   f. **Make predictions**: Before the next eval run, predict outcomes
      - `predict make "B3 CoT lift > 0.15 for {model}" 0.7 --category eval --project {project}`
   g. If anomalies detected, include an alert section in your output
   h. If eval pipeline issues detected, file a backlog ticket via `backlog-manager`
3. **Check budget**: Call `budget-check` for experiment-related spend
4. **If spend anomaly**: Include alert if daily experiment cost exceeds $20
5. **If no new results**: Do nothing — silence is expected
6. **File backlog tickets**: If anomalies suggest platform issues (e.g., eval runner crashes, result corruption), use `backlog-manager create` with category `eval`
