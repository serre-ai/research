# Vera — Heartbeat (Cron: every 2 hours)

## On Each Tick

1. **Check for new work**: Call `deepwork-api` for sessions completed since last check
2. **Check for PRs**: Look for open PRs that haven't been reviewed
3. **If new work found**:
   a. Read session output or PR diff via `paper-review` skill
   b. Load project context via `project-status`
   c. Perform structured review against rubric
   d. Post review to `#reviews`
   e. **Auto-dispatch based on verdict**:
      - REVISE → `session-dispatch` a `writer` session with reason "REVISE verdict — {summary of required changes}"
      - ACCEPT → `session-dispatch` an `editor` session with reason "ACCEPT verdict — final polish"
      - REJECT → `backlog-manager create` a ticket describing the fundamental issues, alert `#general`
   f. If REJECT verdict, also alert `#general`
4. **If no new work**: Do nothing — silence is expected
5. **Track reviewed items**: Maintain a list of reviewed session IDs to avoid duplicates
6. **Check for platform issues**: If review reveals tool/pipeline problems, file a backlog ticket
