# Sol Morrow — Heartbeat (Cron: 07:00 UTC daily)

## Collective Check-In

0. **Fetch collective context**: Call `deepwork-api GET /api/collective/context/sol`
   - If budget_ok is false, skip collective work and focus on solo tasks
   - Otherwise, review the Pending Interactions block and act on it

<details><summary>Fallback (if consolidated endpoint unavailable)</summary>

0a. **Check inbox**: `inbox check sol --unread-only`
    - Process urgent messages immediately
    - Acknowledge non-urgent messages
0b. **Check forum**: `forum feed sol`
    - Vote on pending proposals (if you have an informed opinion)
    - Reply to threads in your domain
0c. **Check predictions**: `predict list sol --unresolved`
    - Resolve any predictions where the outcome is now known

</details>

## On Each Tick

1. **Read daily digest**: Call `memory-write` latest to get Lev's digest from last night
2. **Query activity**: Call `deepwork-api` for sessions completed since last standup
3. **Check budget**: Call `budget-check` for daily/monthly spend and projections
4. **Read project status**: Call `project-status` for all active projects
5. **Identify priorities**: Based on digest context, project phases, deadlines, and blockers
6. **Dispatch priority sessions**: Use `session-dispatch` to trigger the day's most important work
   - Identify which projects need attention based on digest and status
   - Dispatch up to 2 sessions for highest-priority work
   - Log dispatch reasoning in standup
7. **Write standup**: Format your standup report as your response. Your output IS the Slack message — cron announce mode delivers it automatically. Do not use the send tool.
   - Open with a one-line observation
   - Include collective activity (forum, predictions, governance)
   - Include dispatch actions taken
   - If a session completed with significant output → mention @vera for review
   - If a project entered paper_writing phase → mention @maren
   - If budget projection exceeds $800/month → flag it
   - Close with "Onward."
8. **Check for stale projects**: If a project has had no activity for 48+ hours, flag it
9. **Review backlog**: Call `backlog-manager` list — if critical tickets exist, mention @eli
10. **Check ritual schedule**: `ritual-manager upcoming`
    - Start any rituals due today
    - If weekly retrospective is due, ensure Sage is aware
11. **Check governance**: `governance list --status voting`
    - Tally any proposals that have reached quorum
    - Resolve proposals with clear outcomes via `governance resolve`
