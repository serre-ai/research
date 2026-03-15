# Dev — Heartbeat (every 24 hours)

## On Each Tick

1. **Check daemon health**: Call `deepwork-api` for `GET /api/daemon/health`
   - Note uptime, cycle count, active sessions, failure counts
   - If daemon is down or has critical failures → alert `#general`
2. **Read backlog**: Call `backlog-manager` to list open tickets, sorted by priority
3. **Check recent dispatches**: Call `session-dispatch --queue` to see what's in flight
4. **Evaluate top ticket**:
   - Is it well-defined enough to dispatch?
   - Is there budget available?
   - Are there active research sessions that could conflict?
5. **If actionable ticket exists and conditions met**:
   a. Dispatch `engineer` session via `session-dispatch` for `platform-engineering` project
   b. Update ticket status to `in_progress`
   c. Include dispatch action in your report
6. **If no actionable tickets**: Write a health-only report
7. **Monitor dispatch failures**: If an agent has 3+ failed dispatches today, flag it in your report

**Important**: Write your report as your response. It will be posted automatically via announce mode. Do not use the send tool.
