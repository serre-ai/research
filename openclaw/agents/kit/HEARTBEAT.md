# Kit — Heartbeat (every 12 hours)

## On Each Tick

1. **Check eval pipeline**: Call `deepwork-api` for eval runs completed since last check
2. **If new results found**:
   a. Fetch full results via `eval-monitor` skill
   b. Calculate accuracy, CoT lift, and CIs
   c. Compare against theoretical predictions from project status
   d. Format result tables
   e. Include results in your response — it will be posted automatically via announce mode. Do not use the send tool.
   f. If anomalies detected, include an alert section in your output
   g. If eval pipeline issues detected, file a backlog ticket via `backlog-manager`
3. **Check budget**: Call `budget-check` for experiment-related spend
4. **If spend anomaly**: Include alert if daily experiment cost exceeds $20
5. **If no new results**: Do nothing — silence is expected
6. **File backlog tickets**: If anomalies suggest platform issues (e.g., eval runner crashes, result corruption), use `backlog-manager create` with category `eval`
