# Research Log: agent-failure-taxonomy

**Project**: A Taxonomy of Failure Modes in LLM-Based Autonomous Agents
**Venue**: ACL 2027 (February 2027 submission)
**Created**: 2026-03-11
**Format**: Append-only chronological log. Every agent reads this before starting work. New entries go at the bottom.

---

## 2026-03-10 | Project Initialization

**Agent**: Researcher

Initialized the agent-failure-taxonomy project targeting ACL 2027. Core thesis: LLM-based autonomous agents fail in systematic, categorizable ways that map to underlying LLM limitations. No comprehensive taxonomy currently exists connecting agent-level failures to root causes.

**Key decisions**:
- Target ACL 2027 as venue (strong fit for survey-style work on language agents; February 2027 deadline gives ~11 months).
- Use grounded theory methodology for taxonomy development (avoids imposing categories prematurely; iterative coding from data produces more natural taxonomies).

**Hypotheses**:
- H1: Agent failures cluster into 5-7 distinct categories largely independent of the underlying LLM (architectural, not model-specific).
- H2: Most agent failures (>60%) stem from planning and state tracking limitations rather than knowledge gaps or tool-use errors.
- H3: Failure mode frequency shifts predictably with agent architecture choices (e.g., ReAct vs. plan-then-execute).

**Methodology**: Literature survey (100+ failure instances) -> open coding -> axial coding -> controlled experiments (3+ frameworks) -> architecture analysis -> mitigation evaluation.

**Connection to reasoning-gaps**: This project connects agent-level failures to the formal reasoning gap framework. Agent failures in planning and state tracking should map to Types 3-5 (serial composition, algorithmic, and intractability gaps). This cross-project connection is a secondary contribution.

---

## Current Status (2026-03-11)

Project is in early research phase. All work streams are at not_started status:
- Literature review: Target 100+ failure instances from published work and public demonstrations
- Taxonomy development: Grounded theory methodology planned
- Controlled experiments: Target 3+ agent frameworks
- Paper writing: ACL 2027 format

**Next steps**: Begin systematic literature survey of LLM agent papers from 2023-2026, focusing on collecting concrete, documented failure instances with enough detail to categorize.
