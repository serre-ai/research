# project-status

Project status reading and summarization skill.

## Usage
Used by all agents to read `projects/*/status.yaml` files and summarize project state.

## Functions

### Read All Projects
```bash
./scripts/read-status.sh all
```

### Read Specific Project
```bash
./scripts/read-status.sh reasoning-gaps
```

## Output
Returns structured summary per project:
- Project name and title
- Current phase (literature_review / framework / experiments / paper_writing / revision)
- Confidence level
- Key metrics and recent decisions
- Next steps and blockers

## Notes
- status.yaml is the single source of truth for project state
- Always check status before making any coordination decisions
- Phase transitions are significant events — flag them to Sol
