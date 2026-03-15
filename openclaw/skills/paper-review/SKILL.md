# paper-review

Paper and session output review skill.

## Usage
Used by Vera and Maren to read git diffs, paper sections, and session outputs for review.

## Functions

### Read PR Diff
```bash
git log --oneline main..HEAD
git diff main..HEAD -- 'projects/*/paper/'
```

### Read Paper Section
```bash
cat projects/{project}/paper/{section}.tex
```

### Read Session Output
Query the Deepwork API for session details:
```bash
../../deepwork-api/scripts/api-client.sh GET /api/sessions/{id}
```

### Compare Versions
```bash
git diff {commit1}..{commit2} -- 'projects/*/paper/'
```

## Review Criteria
See `references/review-rubric.md` for the structured review framework.

## Notes
- Always read the full diff, not just the summary
- Cross-reference claims with data in `projects/*/benchmarks/results/`
- Check mathematical statements for correctness
- Verify that figures and tables match the data
