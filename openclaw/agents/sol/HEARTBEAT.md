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
7. **Post standup**: Send formatted standup to `#general` (include dispatch actions)
8. **Coordinate**:
   - If a session completed with significant output → mention Vera in `#general` for review
   - If a project entered paper_writing phase → mention Maren
   - If budget projection exceeds $800/month → flag in standup
9. **Check for stale projects**: If a project has had no activity for 48+ hours, flag it
10. **Review backlog**: Call `backlog-manager` list — if critical tickets exist, mention Dev
