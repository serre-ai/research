# Serre AI Multi-Agent System

**Version**: 1.0
**Updated**: 2026-03-11

---

## 1. Agent Philosophy

The Forge platform uses specialized agents rather than a single general-purpose agent. This design is rooted in three principles:

**Specialization over generality.** A researcher agent with a narrow mandate (find gaps, synthesize literature) produces better output than a general agent told to "work on the project." Constraints sharpen performance. Each agent has explicit permissions, budgets, and output formats.

**Adversarial debate over self-assessment.** The critic agent exists precisely because writers cannot reliably evaluate their own work. The critic is read-only on paper files -- it cannot fix problems, only identify them. This separation of concerns prevents the common failure mode where an agent writes a weak section and then rates it favorably.

**The critic is the most important agent.** Research quality is bounded by the quality of internal review, not the quality of first drafts. A strong critic that catches novelty gaps, logical errors, and missing baselines is worth more than a prolific writer. The critic's verdict gates all submission decisions.

### Current State vs. Target

The platform currently has three agent definitions (`.claude/agents/`):
- `researcher.md` -- literature review and gap identification
- `writer.md` -- paper drafting
- `reviewer.md` -- critical review

The daemon maps project phases to agent types:
```typescript
const PHASE_TO_AGENT = {
  "research": "researcher",
  "literature-review": "researcher",
  "drafting": "writer",
  "revision": "reviewer",
  "final": "editor",
};
```

This document specifies the full target agent system with six roles: Scout, Researcher, Theorist, Experimenter, Writer, and Critic (plus Editor for camera-ready preparation).

---

## 2. Agent Role Specifications

### 2.1 Scout

**Purpose**: Continuous literature monitoring, gap identification, and trend tracking. The Scout is the platform's eyes on the field.

**Trigger**: Daily cron job at 06:00 UTC. Also triggered on-demand when a project enters a new phase.

**Input**:
- arXiv RSS feeds for tracked categories (cs.AI, cs.CL, cs.LG, stat.ML)
- Semantic Scholar API (citation graph traversal, related paper discovery)
- Active project keywords and research questions (from BRIEF.md and status.yaml)
- Existing ideas.yaml backlog

**Output**:
- Daily digest message to Slack (relevant papers, research opportunities)
- Append entries to `ideas.yaml` with relevance scores
- Update project status.yaml `related_work` section if highly relevant paper found

**Tools**: WebSearch, WebFetch, Read, Write

**Constraints**:
- Read-only on all project files except ideas.yaml (append-only)
- Cannot modify paper drafts, code, or status.yaml phase/focus fields
- Must include paper title, authors, year, venue, and 1-sentence relevance note for every paper cited
- Relevance scoring must be explicit (0.0-1.0 with stated criteria)

**Session Parameters**:
| Parameter | Value |
|-----------|-------|
| Max turns | 20 |
| Max duration | 15 minutes |
| Budget per session | $2 |
| Daily budget | $2 |
| Model | Claude Sonnet 4 |

---

### 2.2 Researcher

**Purpose**: Deep investigation, literature synthesis, hypothesis development. The Researcher transforms a research question into a concrete plan with formal definitions and identified gaps.

**Trigger**: Project phase = `research` or `literature-review`. Also triggered when the Scout identifies a highly relevant new paper (relevance > 0.8).

**Input**:
- `BRIEF.md` -- research goals and scope
- `status.yaml` -- current state, next_steps, decisions_made
- `research-log.md` -- previous findings (if exists)
- `literature/` directory -- downloaded/summarized papers
- `notes/` directory -- prior research notes

**Output**:
- Research notes in `notes/` (structured markdown with citations)
- Literature summaries in `literature/` (per-paper or thematic)
- Formal definitions and conjectures (preliminary, refined by Theorist)
- Updated `status.yaml`: phase, current_focus, next_steps, decisions_made, confidence

**Tools**: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch (full toolset)

**Constraints**:
- All claims must cite sources with author, year, and title
- Must explicitly distinguish established facts from conjectures
- Must flag contradictions in the literature
- Must identify at least 3 candidate research directions before committing to one
- Decision to narrow scope must be logged in status.yaml with rationale
- Cannot skip literature review -- must survey >= 15 relevant papers before hypothesis formation

**Session Parameters**:
| Parameter | Value |
|-----------|-------|
| Max turns | 50 |
| Max duration | 45 minutes |
| Budget per session | $5 |
| Per-project daily budget | $10 |
| Model | Claude Sonnet 4 |

---

### 2.3 Theorist

**Purpose**: Formal framework development, proofs, and mathematical rigor. The Theorist takes informal research insights and gives them precise mathematical form.

**Trigger**: Project phase = `research` with `formal_framework` status = `in_progress` in status.yaml. Typically runs after the Researcher has identified the core contribution.

**Input**:
- Research notes and definitions from Researcher
- Proof sketches and conjectures
- Related formal frameworks from literature

**Output**:
- Formal definitions (LaTeX, in `paper/` directory)
- Theorem statements with complete proofs
- Proof sketches explicitly marked as `\begin{proofsketch}` (not presented as complete)
- Counterexamples or impossibility results where applicable
- Updated status.yaml with framework completion status

**Tools**: Read, Write, Edit, Bash (for LaTeX compilation and validation)

**Constraints**:
- All claims must be precisely stated with explicit assumptions
- Proofs must be complete or explicitly marked as sketches -- no hand-waving
- Must verify definitions are consistent (no circular definitions)
- Must check that theorems follow from stated assumptions (not unstated ones)
- Must compile LaTeX and verify it renders correctly
- Cannot introduce notation without defining it

**Session Parameters**:
| Parameter | Value |
|-----------|-------|
| Max turns | 50 |
| Max duration | 60 minutes |
| Budget per session | $8 |
| Per-project daily budget | $15 |
| Model | Claude Sonnet 4 |

---

### 2.4 Experimenter

**Purpose**: Design experiments, implement benchmarks, run evaluations, and analyze results. The Experimenter bridges theory and evidence.

**Trigger**: Project phase = `empirical-evaluation`.

**Input**:
- Formal framework (predictions to test)
- Benchmark specifications (from BRIEF.md or research notes)
- Analysis plan (pre-registered before running experiments)
- Existing code in `src/` and `benchmarks/`

**Output**:
- Benchmark code in `benchmarks/` or `src/`
- Evaluation scripts with checkpoint/resume support
- Results in JSONL format (for PostgreSQL backfill)
- Analysis outputs: tables (LaTeX), figures (PDF/PNG), statistical summaries
- Updated status.yaml with experiment status and key findings

**Tools**: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch (full toolset)

**Constraints**:
- Must pre-register analyses before running experiments (write analysis plan to notes/)
- Must use bootstrap confidence intervals (not just point estimates)
- Must test minimum 3 model families (to avoid single-provider bias)
- Must implement checkpoint/resume (no lost work on interruption)
- Must track API costs during evaluation runs
- Must report both positive and negative results
- Code must include random seed management for reproducibility
- Cannot cherry-pick results -- all pre-registered analyses must be reported

**Session Parameters**:
| Parameter | Value |
|-----------|-------|
| Max turns | 100 |
| Max duration | 2 hours |
| Budget per session | $15 (excluding API eval costs) |
| Per-project daily budget | $30 (including eval API costs) |
| Model | Claude Sonnet 4 |

---

### 2.5 Writer

**Purpose**: Draft and refine paper sections. The Writer transforms research notes, formal results, and experimental findings into polished academic prose.

**Trigger**: Project phase = `drafting` or `paper_writing` status = `in_progress`.

**Input**:
- Research notes (from Researcher)
- Formal framework: definitions, theorems, proofs (from Theorist)
- Experimental results: tables, figures, analysis (from Experimenter)
- Venue formatting requirements (e.g., neurips_2026.sty)
- Prior draft sections (if revising)
- Critic review (if in revision cycle)

**Output**:
- LaTeX paper sections in `paper/` directory
- Figures with complete, self-contained captions
- Tables with proper formatting and statistical annotations
- BibTeX entries in `paper/references.bib`
- Updated status.yaml with drafting progress (sections completed)

**Tools**: Read, Write, Edit, Bash (LaTeX compilation), Glob, Grep

**Constraints**:
- Active voice where possible
- Define all notation on first use in each section
- Every claim must be supported by a citation, proof reference, or experimental result
- Figures must be self-contained (reader should understand them without reading the body)
- Related work must be fair -- acknowledge strengths of prior approaches, not just weaknesses
- Must compile LaTeX after writing to verify no errors
- Page limit awareness -- know the venue's limits and track section lengths
- Cannot fabricate citations or results

**Session Parameters**:
| Parameter | Value |
|-----------|-------|
| Max turns | 50 |
| Max duration | 45 minutes |
| Budget per session | $5 |
| Per-project daily budget | $10 |
| Model | Claude Sonnet 4 |

---

### 2.6 Critic

**Purpose**: Adversarial review. Simulates a hostile conference reviewer who is looking for reasons to reject. The Critic is the quality gate for the entire system.

**Trigger**: After the Writer completes a draft, before any submission decision. Also triggered on-demand via `/review` command.

**Input**:
- Current paper draft (all sections)
- Related work (to verify novelty claims)
- Experimental results (to verify claims match data)
- Venue acceptance criteria (if known)

**Output**: A structured review document with the following sections:

```markdown
## Review: <paper-title>
Date: YYYY-MM-DD
Reviewer: Critic Agent

### Summary
[2-3 sentence summary of the paper's contribution]

### Strengths
- [Bulleted list, minimum 2 items]

### Weaknesses
- [Bulleted list, MINIMUM 3 items -- the critic MUST find weaknesses]

### Questions for Authors
- [Specific questions that would need answers for acceptance]

### Novelty Assessment
- [Explicit comparison to most similar prior work]
- [What is genuinely new vs. incremental]

### Missing References
- [Papers that should be cited but aren't]

### Verdict: ACCEPT / REVISE / REJECT
[1-paragraph justification]

### Required Changes (if REVISE)
- [Numbered, specific, actionable items]
```

**Tools**: Read, WebSearch (to verify novelty claims against existing work), Glob, Grep

**Constraints -- these are critical and non-negotiable**:
- **READ-ONLY on all paper files.** The Critic cannot edit the paper, only review it. This prevents the common failure mode of self-editing where problems get papered over instead of identified.
- **Must find at least 3 weaknesses.** Every paper has weaknesses. A review with fewer than 3 is not doing its job. If the paper is genuinely strong, the weaknesses may be minor (presentation, missing ablation, limited scope) -- but they must be identified.
- **Must check novelty claims.** Use WebSearch to verify that the paper's claimed contributions are actually novel. Check if similar results exist in recent preprints.
- **Must verify that experimental claims match the data.** If the paper claims "X outperforms Y by Z%", the Critic must find the table or figure that supports this and verify the numbers.
- **Verdict gates submission.** A "REVISE" verdict loops back to the Writer with the required changes list. A "REJECT" verdict escalates to the human operator -- the paper is not submitted without human review after a reject.

**Session Parameters**:
| Parameter | Value |
|-----------|-------|
| Max turns | 30 |
| Max duration | 30 minutes |
| Budget per session | $3 |
| Per-project daily budget | $6 |
| Model | Claude Sonnet 4 |

---

### 2.7 Editor

**Purpose**: Final polish, venue formatting, and camera-ready preparation. The Editor handles the mechanical aspects of publication preparation.

**Trigger**: Project phase = `final`, after the Critic has issued an ACCEPT verdict.

**Input**:
- Approved draft (post-Critic review)
- Venue style files (e.g., `neurips_2026.sty`, `acl_2027.sty`)
- Supplementary material requirements
- Page limits and formatting guidelines

**Output**:
- Camera-ready paper (compiles cleanly with venue style)
- Supplementary materials document
- Author response document (if venue requires one)
- Final compiled PDF
- Updated status.yaml: phase = completed

**Tools**: Read, Write, Edit, Bash (LaTeX compilation)

**Constraints**:
- Must not change the substance of any claim (only formatting, grammar, clarity)
- Must verify paper compiles cleanly with venue style files
- Must check page limits are met
- Must verify all figures render at correct resolution
- Must ensure all references are complete (no "?" in compiled output)

**Session Parameters**:
| Parameter | Value |
|-----------|-------|
| Max turns | 30 |
| Max duration | 30 minutes |
| Budget per session | $3 |
| Per-project daily budget | $6 |
| Model | Claude Sonnet 4 |

---

## 3. Agent Collaboration Patterns

### 3.1 Sequential Handoff

The default flow for a research project:

```
Researcher --> Theorist --> Experimenter --> Writer --> Critic --> Editor
```

Each agent reads the output of the previous agent via the project's files (notes/, paper/, status.yaml). The handoff is mediated by the daemon's phase-to-agent mapping: when the Researcher updates `phase: empirical-evaluation` in status.yaml, the next daemon cycle scores the project and launches an Experimenter session.

**Handoff data**:
| From | To | Data passed via |
|------|----|-----------------|
| Researcher | Theorist | notes/, status.yaml (definitions, conjectures) |
| Theorist | Experimenter | paper/ (formal framework), status.yaml (predictions) |
| Experimenter | Writer | benchmarks/results/, paper/tables/, paper/figures/ |
| Writer | Critic | paper/ (all sections) |
| Critic | Writer (revision) | reviews/ (structured review document) |
| Critic (accept) | Editor | paper/ (approved draft) |

### 3.2 Parallel Execution

Some agents can run concurrently when their outputs do not conflict:

```
Experimenter (running benchmarks, writing results)
     |
     +--- parallel ---> Writer (drafting introduction, related work, methodology)
     |                  (sections that don't depend on results)
     |
     v
Writer (drafting results section)  <-- needs Experimenter output
```

The daemon enables this by having 2+ session slots. Two agents for the same project can run simultaneously if they operate on non-overlapping files. The git worktree isolation prevents merge conflicts.

**Safe parallel pairs**:
- Experimenter + Writer (if Writer works on intro/related work/methodology)
- Scout + any other agent (Scout is read-only on project files)
- Researcher on Project A + Writer on Project B (different projects)

**Unsafe parallel pairs** (must not run simultaneously):
- Writer + Editor (both modify paper/)
- Writer + Critic (Critic must review a stable draft)
- Two agents of any type on the same project files

### 3.3 Debate Pattern (Critic-Writer Loop)

The most important collaboration pattern. After the Writer completes a draft:

```
Cycle 1:
  Writer produces draft v1
  Critic reviews -> verdict: REVISE
  Required changes: [list]

Cycle 2:
  Writer reads Critic review
  Writer addresses required changes, produces draft v2
  Critic reviews -> verdict: REVISE (fewer issues)
  Required changes: [shorter list]

Cycle 3:
  Writer reads Critic review
  Writer addresses remaining changes, produces draft v3
  Critic reviews -> verdict: ACCEPT

Maximum 3 revision cycles. If the Critic still says REVISE after cycle 3,
the verdict is escalated to the human operator as a de facto REJECT.
```

**Implementation**: The daemon tracks revision cycle count in status.yaml:

```yaml
review:
  cycle: 2
  last_critic_verdict: revise
  required_changes:
    - "Strengthen comparison with Chen et al. (2025)"
    - "Add ablation study removing difficulty scaling"
  changes_addressed: 1
```

### 3.4 Escalation Pattern

The Critic can issue three verdicts:

| Verdict | Action |
|---------|--------|
| **ACCEPT** | Proceed to Editor. Paper is ready for formatting. |
| **REVISE** | Loop back to Writer with required changes list. Max 3 cycles. |
| **REJECT** | Escalate to human operator via Slack notification. Paper is not submitted without human review. The human can override (force-accept), agree (archive), or redirect (new research direction). |

Escalation notification format:
```
:red_circle: *Critic Rejected Draft* [reasoning-gaps]
The Critic has rejected the current draft after review.

*Key issues:*
1. Main theorem (Theorem 3.2) has a gap in the proof of Lemma 3.1
2. Novelty claim overlaps with concurrent work by Chen et al. (arXiv:2026.xxxxx)
3. Experimental evaluation covers only 2 model families (need >= 3)

*Action required:* Review the critic's full assessment and decide next steps.
```

---

## 4. Agent Prompt Architecture

Each agent session receives a layered prompt constructed by `SessionRunner.buildPrompt()`. The layers are concatenated with `---` separators.

### Layer Structure

```
Layer 1: Global Platform Instructions
  Source: CLAUDE.md (repo root)
  Content: Git conventions, commit format, decision protocol, code style

          ---

Layer 2: Agent Role Definition
  Source: .claude/agents/<agent-type>.md
  Content: Agent-specific capabilities, process, constraints, output format

          ---

Layer 3: Project-Specific Instructions
  Source: projects/<name>/CLAUDE.md
  Content: Venue requirements, methodology notes, project-specific rules

          ---

Layer 4: Current Project Status
  Source: projects/<name>/status.yaml (wrapped in ```yaml code block)
  Content: Phase, confidence, next_steps, decisions_made, metrics

          ---

Layer 5: Session Workflow Instructions
  Generated at runtime by SessionRunner
  Content: Agent type, project name, today's date, numbered workflow steps
```

### Example Assembled Prompt (Researcher)

```markdown
# Global Platform Instructions

[Contents of CLAUDE.md -- git conventions, commit format, etc.]

---

# Agent Role Definition

# Researcher Agent

You are a deep research agent for the Forge platform. Your role is to
conduct thorough literature reviews, identify research gaps, and synthesize
findings.

## Capabilities
- Search the web for papers, articles, and technical content
- Read and analyze existing project files
[...]

---

# Project-Specific Instructions

# Reasoning Gaps in LLM Chain-of-Thought

See BRIEF.md for research goals.
[Project-specific venue requirements, methodology notes...]

---

# Current Project Status (status.yaml)

```yaml
project: reasoning-gaps
title: "Reasoning Gaps: When Chain-of-Thought Fails"
phase: empirical-evaluation
confidence: 0.75
next_steps:
  - "Run Sonnet 4.6 evaluations on B3-B9"
  - "Analyze difficulty scaling curves"
[...]
```

---

# Session Workflow

You are working autonomously on the "reasoning-gaps" project as a researcher agent.

1. Read project files to understand current state before making changes
2. Make all decisions autonomously using your best judgment
3. Use extended thinking for critical research decisions
4. Make frequent conventional commits: type(reasoning-gaps): description
5. Update status.yaml after significant progress
6. Log all decisions in decisions_made with date and rationale
7. Push changes to remote regularly
8. Create a PR to main when you reach a milestone

Today's date is 2026-03-11.
```

### Prompt Design Principles

1. **Most specific layer wins.** If CLAUDE.md says "use extended thinking for all decisions" but the project CLAUDE.md says "use extended thinking only for methodology choices," the project-level instruction takes precedence.

2. **Status.yaml is injected raw.** The agent sees the exact YAML content. This avoids lossy summarization and lets the agent parse structured fields directly.

3. **Session workflow is always last.** The final section serves as the agent's immediate action prompt. It ends with the current date to ground temporal reasoning.

4. **No conversation history between sessions.** Each session starts fresh with only file-based context. This prevents context window bloat and ensures all state is persisted to files (the durable medium).

---

## 5. Token Budget Management

### Budget Hierarchy

```
Global Monthly Budget: $1,000
  |
  +-- Global Daily Budget: $40 (monthly / 30, configurable)
       |
       +-- Per-Project Daily Budget: daily / active_project_count
            |
            +-- Per-Session Budget: varies by agent type (see specs above)
```

### Alert Levels

| Level | Trigger | Action |
|-------|---------|--------|
| **ok** | < 80% of daily or monthly limit | Normal operation |
| **warning** | >= 80% of daily or monthly limit | Slack notification, continue operating |
| **critical** | >= 95% of daily or monthly limit | Slack notification, log warning, continue with caution |
| **exceeded** | > 100% of daily or monthly limit | Skip daemon cycle, Slack error notification, no new sessions |

Implemented in `BudgetTracker.computeAlertLevel()`:
```typescript
if (dailyPct > 1 || monthlyPct > 1) return "exceeded";
if (dailyPct >= 0.95 || monthlyPct >= 0.95) return "critical";
if (dailyPct >= 0.8 || monthlyPct >= 0.8) return "warning";
return "ok";
```

### Cost Tracking

Each session records:
- `tokens_input`, `tokens_output` -- from Claude SDK result
- `cost_usd` -- from SDK `total_cost_usd` field, or calculated:
  ```
  cost = (input_tokens / 1M) * $3 + (output_tokens / 1M) * $15
  ```
  (Based on Claude Sonnet 4 pricing)

Records are written to:
1. `.logs/spending.jsonl` (append-only, durable)
2. `budget_events` PostgreSQL table (via API, queryable)

### Budget Enforcement Points

| Point | Enforcer | Behavior |
|-------|----------|----------|
| Before daemon cycle | Daemon.cycle() | Checks `budgetTracker.getStatus()`. Skips cycle if exceeded. |
| Project scoring | Daemon.scoreProjects() | -10 penalty if project exceeds per-project daily budget |
| During session | SessionRunner (SDK) | SDK's `maxBudgetUsd` parameter (if set) |
| After session | Daemon.runSession() | Records spending, triggers alert check |
| API display | api.ts /api/budget | Shows daily/monthly totals, by-project, by-model, 7-day burn rate |

---

## 6. Agent Evaluation

How to assess whether agents are performing well and improving over time.

### Metrics Per Session

| Metric | Source | What it measures |
|--------|--------|-----------------|
| Turns used | SDK result | Efficiency -- fewer turns for same output is better |
| Cost (USD) | Budget tracker | Cost-effectiveness |
| Duration (minutes) | Session result | Wall-clock efficiency |
| Commits created | Git log | Productivity (with quality caveat) |
| Status.yaml changes | Git diff | Meaningful progress vs. busywork |
| Errors | Session result | Reliability |

### Metrics Per Agent Type

**Researcher**:
- Papers reviewed (status.yaml metrics)
- Research notes created (file count in notes/)
- Decisions logged (decisions_made in status.yaml)
- Time to identify primary research gap

**Theorist**:
- Definitions formalized (count in paper/)
- Theorems stated and proved
- LaTeX compilation success rate
- Proof completeness (complete vs. sketch ratio)

**Experimenter**:
- Experiments designed and run
- Model families covered
- Results with confidence intervals (vs. bare numbers)
- Checkpoint/resume reliability (did it recover from interruptions?)
- API cost for evaluation runs

**Writer**:
- Sections drafted per session
- LaTeX compilation success rate
- Words per session (rough productivity measure)
- Citation count per section

**Critic**:
- Weaknesses identified per review (should be >= 3)
- Specificity of feedback (actionable vs. vague)
- Verdict distribution over time (accept/revise/reject ratio)
- False negatives caught in later revision cycles (critic missed something)
- WebSearch queries executed (novelty checking diligence)

**Editor**:
- Compilation errors fixed
- Formatting issues resolved
- Time to camera-ready

### Longitudinal Tracking

Track these across all sessions to detect trends:

1. **Critic scores over time**: Are papers improving? If the critic keeps finding the same class of weakness (e.g., "missing baselines"), the Experimenter's prompt may need strengthening.

2. **Revision cycle count**: Projects that consistently need 3 revision cycles before acceptance suggest the Writer's initial quality is too low.

3. **Failure rate by agent type**: If Researcher sessions fail at 30% but Writer sessions fail at 5%, investigate what makes research sessions fragile.

4. **Cost per phase**: Track total cost to move through each phase. Identify which phases are disproportionately expensive.

5. **Decision quality**: For logged decisions, retrospectively assess whether the decision was correct based on outcomes. This requires human review but builds a dataset for improving decision-making prompts.

### Evaluation Queries

These PostgreSQL queries support agent evaluation via the API:

```sql
-- Session cost and duration by agent type
SELECT agent_type,
       COUNT(*) AS sessions,
       ROUND(AVG(cost_usd)::numeric, 4) AS avg_cost,
       ROUND(AVG(duration_s)::numeric, 0) AS avg_duration_s,
       ROUND(AVG(tokens_used)::numeric, 0) AS avg_tokens,
       ROUND(AVG(commits_created)::numeric, 1) AS avg_commits,
       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failures
FROM sessions
GROUP BY agent_type
ORDER BY sessions DESC;

-- Failure rate trend (weekly)
SELECT DATE_TRUNC('week', started_at) AS week,
       agent_type,
       COUNT(*) AS total,
       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
       ROUND(AVG(CASE WHEN status = 'failed' THEN 1 ELSE 0 END)::numeric, 3) AS failure_rate
FROM sessions
GROUP BY week, agent_type
ORDER BY week DESC, agent_type;

-- Cost per project phase (approximated via agent type)
SELECT project, agent_type,
       SUM(cost_usd) AS total_cost,
       COUNT(*) AS sessions,
       SUM(duration_s) / 3600.0 AS total_hours
FROM sessions
WHERE status = 'completed'
GROUP BY project, agent_type
ORDER BY project, total_cost DESC;
```

---

## 7. Agent Definition File Format

Each agent is defined in `.claude/agents/<type>.md`. These files are loaded by `SessionRunner.buildPrompt()` and injected as Layer 2 of the prompt.

### Current Definitions

**`.claude/agents/researcher.md`** (24 lines):
- Capabilities: web search, file analysis, note writing, status updates
- Process: 5-step workflow from BRIEF.md reading to status update
- Output standards: cite sources, distinguish facts from conjectures, flag contradictions

**`.claude/agents/writer.md`** (23 lines):
- Capabilities: LaTeX/Markdown writing, academic structure, figure descriptions
- Process: 5-step workflow from notes reading to status update
- Writing standards: active voice, notation definition, evidence-backed claims, self-contained figures

**`.claude/agents/reviewer.md`** (25 lines):
- Capabilities: critical analysis, gap identification, improvement suggestions, novelty evaluation
- Review criteria: novelty, correctness, significance, clarity, completeness
- Output format: summary, strengths, weaknesses, questions, verdict

### Target Definition Template

New agent definitions should follow this structure:

```markdown
# <Agent Name> Agent

You are a <role description> for the Forge platform.

## Purpose
<1-2 sentences on what this agent does and why it matters>

## Capabilities
- <Bulleted list of what the agent can do>

## Process
1. <Numbered steps the agent should follow>

## Output Format
<Specific format requirements for the agent's output>

## Constraints
- <Explicit limitations and rules>
- <Things the agent must NOT do>

## Quality Criteria
- <How to judge if the output is good enough>
```

---

## 8. Adding New Agent Types

To add a new agent type to the platform:

1. **Create the agent definition file**: `.claude/agents/<type>.md` following the template above.

2. **Register in daemon.ts** phase-to-agent mapping:
   ```typescript
   const PHASE_TO_AGENT = {
     // ... existing mappings
     "new-phase": "new-agent-type",
   };
   ```

3. **Add to sessions table constraint** (PostgreSQL):
   ```sql
   ALTER TABLE sessions
     DROP CONSTRAINT sessions_agent_type_check,
     ADD CONSTRAINT sessions_agent_type_check
       CHECK (agent_type IN ('researcher', 'writer', 'reviewer', 'editor',
                             'strategist', 'new-agent-type'));
   ```

4. **Update SessionRunner** if the agent needs non-default session parameters (custom max turns, duration, or tools).

5. **Add budget allocation** in the daemon's per-project budget calculation if the agent type has different cost characteristics.

6. **Test**: Run a manual session with `forge start <project>` and verify the agent receives the correct prompt layers and operates within its constraints.
