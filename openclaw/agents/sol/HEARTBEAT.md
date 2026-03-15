# Sol — Heartbeat (Cron: 07:00 UTC daily)

## On Each Tick

1. **Query activity**: Call `deepwork-api` for sessions completed since last standup
2. **Check budget**: Call `budget-check` for daily/monthly spend and projections
3. **Read project status**: Call `project-status` for all active projects
4. **Identify priorities**: Based on project phases, deadlines, and blockers
5. **Post standup**: Send formatted standup to `#general`
6. **Coordinate**:
   - If a session completed with significant output → mention Vera in `#general` for review
   - If a project entered paper_writing phase → mention Maren
   - If budget projection exceeds $800/month → flag in standup
7. **Check for stale projects**: If a project has had no activity for 48+ hours, flag it
