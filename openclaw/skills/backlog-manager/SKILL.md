# backlog-manager

Manage the engineering backlog via the Deepwork API. Any agent can file tickets; Dev reviews and prioritizes them.

## Usage
- **Filing**: All agents can file tickets when they detect issues
- **Managing**: Dev reviews, prioritizes, and dispatches work for tickets
- **Tracking**: Sol oversees backlog health in standups

## Endpoints

### List tickets
```bash
./scripts/backlog.sh list [--status open] [--priority high] [--category daemon]
```

### Create a ticket
```bash
./scripts/backlog.sh create <title> <priority> <category> <filed_by> [description]
```
- `title`: Short description of the issue
- `priority`: `low`, `medium`, `high`, `critical`
- `category`: `daemon`, `api`, `agents`, `eval`, `infra`, `other`
- `filed_by`: Agent filing the ticket
- `description`: Optional longer description

### Update a ticket
```bash
./scripts/backlog.sh update <id> <field> <value>
```
- Fields: `status` (open/in_progress/done/wont_fix), `priority`, `assigned_to`

### Get a ticket
```bash
./scripts/backlog.sh get <id>
```

## Examples
```bash
# Vera files a ticket about eval pipeline issues
./scripts/backlog.sh create "Add confidence intervals to quality scoring" medium daemon vera

# Kit files a ticket about an eval anomaly
./scripts/backlog.sh create "B2 budget_cot negative CoT lift anomaly" high eval kit "CoT lift is -0.254 for B2, suggesting budget_cot condition needs recalibration"

# Dev marks a ticket as in progress
./scripts/backlog.sh update abc123 status in_progress

# List open high-priority tickets
./scripts/backlog.sh list --status open --priority high
```
