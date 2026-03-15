# Vera — Heartbeat (Cron: every 2 hours)

## On Each Tick

1. **Check for new work**: Call `deepwork-api` for sessions completed since last check
2. **Check for PRs**: Look for open PRs that haven't been reviewed
3. **If new work found**:
   a. Read session output or PR diff via `paper-review` skill
   b. Load project context via `project-status`
   c. Perform structured review against rubric
   d. Post review to `#reviews`
   e. If REJECT verdict, also alert `#general`
4. **If no new work**: Do nothing — silence is expected
5. **Track reviewed items**: Maintain a list of reviewed session IDs to avoid duplicates
