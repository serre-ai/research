Conduct deep research for the specified project.

Usage: /research <project-name>

1. Read projects/<project-name>/BRIEF.md and status.yaml
2. Based on current phase and next_steps, conduct web research
3. Search for relevant papers, recent advances, and key results
4. Write findings to projects/<project-name>/notes/
5. Update status.yaml with progress
6. Identify and log any decisions needed
7. If the project has reached a milestone (framework defined, first results,
   major methodology change), update the research explainer page at
   site/src/pages/research/<project-name>.astro:
   - Refine the problem/insight/method sections based on what you've learned
   - Add results data if available (use the callout box pattern from reasoning-gaps)
   - Update the glossary with any new terms that emerged
   - Keep the tone accessible — write for smart non-experts, not reviewers
8. Commit with: research(<project-name>): <description>
