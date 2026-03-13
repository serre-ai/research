Create a new research project. Ask for:
1. Project name (kebab-case)
2. Title
3. Research area and goals
4. Target venue (if known)

Then:
1. Create the project directory under projects/<name>/
2. Create BRIEF.md with the research goals
3. Create status.yaml with initial state
4. Create CLAUDE.md with project-specific instructions
5. Create research explainer page at site/src/pages/research/<name>.astro
   - Use shared/templates/explainer.astro as the template
   - Write for technically-minded non-experts (not paper-level formalism)
   - Include: the problem, the insight, the planned method, why it matters
   - Add a glossary of 8-15 key terms from the research domain
   - See site/src/pages/research/reasoning-gaps.astro for tone and style reference
6. Create a git branch: research/<name>
7. Make an initial commit: research(<name>): initialize project
