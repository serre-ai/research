# Archivist — Heartbeat (Cron: 23:00 UTC daily)

## On Each Tick

1. **Query sessions**: Call `deepwork-api` for all sessions completed today
   - Count by status (completed, failed), agent type, and project
   - Sum costs
2. **Query reviews**: Check `#reviews` activity or API for review posts today
3. **Query budget**: Call `deepwork-api` for today's budget status and projection
4. **Query decisions**: Call `project-status` for any decisions logged today
5. **Query backlog**: Call `backlog-manager` for tickets filed and resolved today
6. **Synthesize digest**: Compile all data into the digest format
7. **Write digest**: Call `memory-write` to save to `/api/memory/digest`
8. **Write summary**: Write your digest as your response. It will be posted automatically via announce mode. Do not use the send tool.
9. **If critical events**: Include an alert section in your output (e.g., budget exceeded, multiple failures)
