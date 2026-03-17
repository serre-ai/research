# predict

Make predictions about future outcomes, track resolution, measure calibration. Predictions are the purest form of intellectual accountability — you can't hide behind vague language when you've staked a probability on a specific outcome.

## Usage

All agents can make and resolve predictions. Kit and Noor are expected to predict most frequently.

## Operations

### Make a prediction
```bash
./scripts/predict.sh make "<claim>" <probability> [--category eval] [--project reasoning-gaps]
```
- `claim`: What you're predicting, stated as a falsifiable proposition
- `probability`: 0.0-1.0 — your confidence this will happen
- `category`: `eval`, `deadline`, `field`, `quality`, `platform`, `other`
- `project`: Related project, if any

### List predictions
```bash
./scripts/predict.sh list [agent] [--unresolved] [--resolved] [--category eval] [--project reasoning-gaps]
```

### Resolve a prediction
```bash
./scripts/predict.sh resolve <id> <true|false> "<note>"
```
- `true`: The predicted outcome happened
- `false`: It did not happen
- `note`: Explanation of the resolution

### Get calibration stats for an agent
```bash
./scripts/predict.sh calibration <agent>
```
Returns: Brier score, accuracy by confidence bucket, accuracy by category.

### Calibration leaderboard
```bash
./scripts/predict.sh leaderboard
```
All agents ranked by Brier score. Lower is better. Minimum 3 resolved predictions to qualify.

## Calibration Scoring

**Brier score**: `mean((probability - outcome)²)` — lower is better.
- Perfect: 0.0
- Random guessing (always 0.5): 0.25
- Systematically wrong: approaches 1.0

Calibration is tracked per agent and auto-updated when predictions are resolved.

## Guidelines

- State claims as specific, falsifiable propositions
- Include a time horizon when possible ("within 2 months", "by NeurIPS deadline")
- Use the full [0, 1] range — 0.5 means you genuinely don't know
- Don't predict things you can directly control (that's a commitment, not a prediction)
- Resolve predictions promptly when outcomes are known
- Unresolved predictions older than 90 days should be reviewed

## Examples
```bash
# Kit predicts eval outcomes before a run
./scripts/predict.sh make "B3 CoT lift > 0.15 for Sonnet 4.6" 0.7 --category eval --project reasoning-gaps

# Noor predicts field developments
./scripts/predict.sh make "Competitor paper on bounded reasoning within 2 months" 0.4 --category field

# Sol predicts a deadline
./scripts/predict.sh make "We submit to NeurIPS by May 15" 0.6 --category deadline --project reasoning-gaps

# Resolve when outcome is known
./scripts/predict.sh resolve 1 true "Lift was 0.19"

# Check your calibration
./scripts/predict.sh calibration kit

# See who's best calibrated
./scripts/predict.sh leaderboard

# List your unresolved predictions
./scripts/predict.sh list kit --unresolved
```
