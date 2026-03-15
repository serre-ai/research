# memory-write

Write and read daily digests via the Deepwork API. Provides persistent memory across agent runs.

## Usage
Used by Archivist to write end-of-day digests. Sol reads digests for morning context.

## Endpoints

### Write a digest
```bash
./scripts/digest.sh write <date> <filed_by> <digest_text> [key_events...]
```
- `date`: ISO date (YYYY-MM-DD)
- `filed_by`: Agent writing the digest (typically `archivist`)
- `digest_text`: Markdown-formatted digest content
- `key_events`: Comma-separated list of event types

### Read latest digest
```bash
./scripts/digest.sh latest
```

### Read digest by date
```bash
./scripts/digest.sh read <date>
```

### List available dates
```bash
./scripts/digest.sh list
```

## Retention
Digests are retained for 30 days. Older digests are automatically pruned.

## Examples
```bash
# Archivist writes the daily digest
./scripts/digest.sh write 2026-03-15 archivist "## Daily Digest\n\n### Sessions\n- 2 sessions completed..." "session_completed,review_posted"

# Sol reads the latest digest
./scripts/digest.sh latest

# Read a specific date
./scripts/digest.sh read 2026-03-14
```
