# Monitoring Guide: Local Evaluations (March 13-14, 2026)

**Started**: 2026-03-13 16:56 UTC
**Expected completion**: 2026-03-14 ~11:00 UTC (18 hours)

---

## Running Evaluations

### o3 Evaluation
- **Process ID**: 117012
- **Model**: openai:o3
- **Combinations**: 27 (9 tasks × 3 conditions)
- **Estimated cost**: $158
- **Estimated runtime**: ~14 hours
- **Expected completion**: 2026-03-14 ~07:00 UTC
- **Log file**: `/home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/o3_eval_2026-03-13.log`

### Sonnet 4.6 Evaluation
- **Process ID**: 117034
- **Model**: anthropic:claude-sonnet-4-20250514
- **Combinations**: 27 (9 tasks × 3 conditions)
- **Estimated cost**: $55
- **Estimated runtime**: ~18 hours
- **Expected completion**: 2026-03-14 ~11:00 UTC
- **Log file**: `/home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/sonnet46_eval_2026-03-13.log`

---

## Monitoring Commands

### Check Process Status
```bash
# Verify both processes are still running
ps aux | grep run_evaluation.py | grep -v grep

# Check CPU/memory usage
ps -p 117012 -o pid,comm,%cpu,%mem,etime,cmd
ps -p 117034 -o pid,comm,%cpu,%mem,etime,cmd
```

### Monitor Progress Logs
```bash
# Watch o3 progress (live tail)
tail -f /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/o3_eval_2026-03-13.log

# Watch Sonnet 4.6 progress (live tail)
tail -f /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/sonnet46_eval_2026-03-13.log

# Check last 50 lines of o3 log
tail -50 /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/o3_eval_2026-03-13.log

# Check last 50 lines of Sonnet 4.6 log
tail -50 /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/sonnet46_eval_2026-03-13.log
```

### Check Overall Progress
```bash
# View progress JSON (if created)
cat /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/benchmarks/results/progress.json | jq .

# Count completed combinations (check results directory)
ls /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/benchmarks/results/*.json | wc -l

# Check checkpoint files
ls -lh /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/benchmarks/results/checkpoints/
```

### Check for Errors
```bash
# Check for error patterns in o3 log
grep -i "error\|failed\|exception" /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/o3_eval_2026-03-13.log

# Check for error patterns in Sonnet 4.6 log
grep -i "error\|failed\|exception" /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/sonnet46_eval_2026-03-13.log
```

---

## Progress Tracking

### Expected Timeline

| Time (UTC) | Event | Completion % |
|------------|-------|--------------|
| 16:56 | Both evaluations started | 0% |
| 18:00 | ~1 hour elapsed | ~6% |
| 22:00 | ~5 hours elapsed | ~28% |
| 02:00 | ~9 hours elapsed | ~50% |
| 07:00 | o3 expected complete | ~75% |
| 11:00 | Sonnet 4.6 expected complete | 100% |

### Combination Progress Format

Each log will show progress like:
```
[1/27] openai:o3 / B1 / direct -- 85% accuracy (3m 45s)
Overall: 1/27 (1 ok, 0 failed) | ETA: 13h 45m | Elapsed: 3m 45s
```

Key metrics per combination:
- Accuracy percentage
- Duration
- Overall completed/total
- ETA (estimated time remaining)
- Elapsed time

---

## Success Indicators

### Healthy Progress Signs
- Both processes still running (check with `ps aux | grep run_evaluation.py`)
- Log files growing steadily
- ETA decreasing over time
- Accuracy values reasonable (20-90% typical range)
- No repeated error messages

### Warning Signs
- Process terminated unexpectedly
- Log file not growing for >30 minutes
- Repeated API rate limit errors
- Repeated "failed" messages
- High error rate (>10% failures)

---

## Troubleshooting

### Process Died Unexpectedly
If a process terminates:

1. Check exit code and last log lines:
```bash
tail -50 /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/o3_eval_2026-03-13.log
# or
tail -50 /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/logs/sonnet46_eval_2026-03-13.log
```

2. Check if it completed all 27 combinations
3. If incomplete, restart with same command (checkpoint system will resume):
```bash
cd /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/benchmarks
nohup python3 run_evaluation.py --models "openai:o3" --tasks B1 B2 B3 B4 B5 B6 B7 B8 B9 --conditions direct short_cot budget_cot --yes >> ../logs/o3_eval_2026-03-13.log 2>&1 &
```

### API Rate Limiting
Evaluations have built-in rate limit handling with exponential backoff. If you see rate limit messages, this is normal and handled automatically.

### High Failure Rate
If >10% of combinations are failing:
1. Check API keys are still valid
2. Check API service status (status.openai.com, status.anthropic.com)
3. Check error messages for patterns
4. Consider pausing and investigating

---

## Completion Checklist

When evaluations complete:

### Verification Steps
1. ✅ Check both processes exited cleanly (exit code 0)
2. ✅ Verify all 27 combinations completed for each model
3. ✅ Check results files exist (54 total: 27 per model)
4. ✅ Verify no failures in final summary
5. ✅ Check total cost against estimates

### Data Collection
```bash
# Count result files
ls /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/benchmarks/results/*.json | wc -l

# Check file sizes (should be >0 bytes)
ls -lh /home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/benchmarks/results/*.json

# Verify accuracy values are present
python3 -c "import json; print([json.load(open(f))['summary']['accuracy'] for f in ['/home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/benchmarks/results/openai_o3_B1_direct.json']])"
```

### Next Steps After Completion
1. Update session note with completion time and actual costs
2. Run B2 recalibration for all 9 models
3. Consolidate all evaluation data
4. Run full analysis pipeline
5. Update paper Section 5
6. Commit and push results

---

## Cost Tracking

### Budget Status
- **Previous spend (VPS)**: ~$83
- **Current session budget**: $213 (o3 $158 + Sonnet $55)
- **Total spend after session**: ~$296 (30% of $1,000 monthly budget)
- **Remaining budget**: ~$704 (70%)

### Future Budget Needs
- B2 recalibration (9 models): ~$3-5
- Buffer for contingencies: ~$100
- Available for additional experiments: ~$600

---

## Timeline Status

- **Current date**: 2026-03-13
- **NeurIPS 2026 deadline**: 2026-05-07 (54 days remaining)
- **Expected evaluation completion**: 2026-03-14 ~11:00 UTC
- **Post-evaluation work estimate**: 7-10 days
- **Target submission window**: 2026-03-23 to 2026-03-29
- **Timeline buffer**: 38-44 days

---

## Contact Information

If unexpected issues arise:
- Check session notes in `notes/SESSION-2026-03-13-*.md`
- Review status.yaml for current project state
- Contingency plan documented in `notes/SESSION-2026-03-13-afternoon-extended-downtime.md`

---

**Last updated**: 2026-03-13 17:00 UTC
