# budget-check

Budget monitoring and projection skill.

## Usage
Used by Sol and Kit to query budget status, calculate burn rates, and project end-of-month spending.

## Functions

### Current Budget
```bash
./scripts/budget-query.sh status
```

### Daily Breakdown
```bash
./scripts/budget-query.sh daily
```

### Projection
```bash
./scripts/budget-query.sh projection
```

## Limits
- Monthly budget: $1,000
- Daily budget: $40
- Alert when monthly projection exceeds $800
- Alert when daily spend exceeds $30

## Output
Returns structured budget data:
- Today's spend so far
- Month-to-date spend
- Daily average this month
- Projected end-of-month total
- Remaining budget
- Breakdown by category (API calls, compute, data services)
