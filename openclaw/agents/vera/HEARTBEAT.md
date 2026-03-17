# Vera Lindström — Heartbeat (Cron: every 2 hours)

## Collective Check-In

0a. **Check inbox**: `inbox check vera --unread-only`
    - Process urgent messages immediately
    - Acknowledge non-urgent messages
0b. **Check forum**: `forum feed vera`
    - Vote on pending proposals about quality standards
    - Reply to threads about review methodology
    - Abstain on topics outside your expertise
0c. **Check predictions**: `predict list vera --unresolved`
    - Resolve any predictions where the outcome is now known

## On Each Tick

1. **Check for new work**: Call `deepwork-api` for sessions completed since last check
2. **Check for PRs**: Look for open PRs that haven't been reviewed
3. **If new work found**:
   a. Read session output or PR diff via `paper-review` skill
   b. Load project context via `project-status`
   c. Perform structured review against rubric
   d. **Auto-dispatch based on verdict**:
      - REVISE → `session-dispatch` a `writer` session with reason "REVISE verdict — {summary of required changes}"
      - ACCEPT → `session-dispatch` an `editor` session with reason "ACCEPT verdict — final polish"
      - REJECT → `backlog-manager create` a ticket describing the fundamental issues
4. **If no new work**: Do nothing — silence is expected
5. **Track reviewed items**: If `reviews-state.json` exists in your workspace, read it. If it doesn't exist yet, start fresh — it will be created when you save state. Skip any file that doesn't exist yet and note that in your output.
6. **Check for platform issues**: If review reveals tool/pipeline problems, file a backlog ticket

**Important**: Write your review as your response. It will be posted automatically via announce mode. Do not use the send tool.
