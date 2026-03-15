# Sol — Heartbeat (Cron: 07:00 UTC daily)

## On Each Tick

1. **Read daily digest**: Call `memory-write` latest to get Archivist's digest from last night
2. **Query activity**: Call `deepwork-api` for sessions completed since last standup
3. **Check budget**: Call `budget-check` for daily/monthly spend and projections
4. **Read project status**: Call `project-status` for all active projects
5. **Identify priorities**: Based on digest context, project phases, deadlines, and blockers
6. **Dispatch priority sessions**: Use `session-dispatch` to trigger the day's most important work
   - Identify which projects need attention based on digest and status
   - Dispatch up to 2 sessions for highest-priority work
   - Log dispatch reasoning in standup
7. **Write standup**: Format your standup report as your response. Your output IS the Slack message — cron announce mode delivers it automatically. Do not use the send tool.
   - Include dispatch actions taken
   - If a session completed with significant output → mention @vera for review
   - If a project entered paper_writing phase → mention @maren
   - If budget projection exceeds $800/month → flag it
8. **Check for stale projects**: If a project has had no activity for 48+ hours, flag it
9. **Review backlog**: Call `backlog-manager` list — if critical tickets exist, mention @dev
