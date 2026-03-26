#!/usr/bin/env python3
"""
Expand DeepWork Linear roadmap: Sprint 4–12 (May 4 – Sep 6, 2026).
Creates 9 new cycles and ~76 new issues on the DW team.
Does NOT touch the EV team.
"""

import json
import os
import time
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_URL = "https://api.linear.app/graphql"
API_KEY = os.environ.get("LINEAR_API_KEY")
if not API_KEY:
    sys.exit("ERROR: LINEAR_API_KEY environment variable not set")
DW_TEAM_ID = "77e7bcae-30d7-4257-b043-6f0b004abc65"

# DW team states
STATE_TODO = "834253df-cd32-4f85-bae7-55054f473c4b"
STATE_BACKLOG = "311c91d4-9830-4b87-8132-f26e6bb1f8ad"


def gql(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query against Linear API."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    req = Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": API_KEY,
        },
    )

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code}: {body[:200]}")
        raise

    if "errors" in data:
        print(f"  GraphQL errors: {data['errors']}")
        raise RuntimeError(data["errors"][0]["message"])

    return data["data"]


def rate_limit():
    """Respect Linear's rate limits."""
    time.sleep(0.15)


# ============================================================
# Fetch existing projects and labels
# ============================================================

def fetch_projects() -> dict:
    """Fetch existing DW project IDs by name."""
    print("Fetching existing projects...")
    data = gql(f'''{{
        team(id: "{DW_TEAM_ID}") {{
            projects(first: 50) {{
                nodes {{ id name }}
            }}
        }}
    }}''')
    projects = {}
    for p in data["team"]["projects"]["nodes"]:
        projects[p["name"]] = p["id"]
        print(f"  {p['name']}: {p['id'][:8]}...")
    return projects


def fetch_labels() -> dict:
    """Fetch existing DW label IDs by name."""
    print("Fetching existing labels...")
    data = gql(f'''{{
        team(id: "{DW_TEAM_ID}") {{
            labels(first: 100) {{
                nodes {{ id name }}
            }}
        }}
    }}''')
    labels = {}
    for l in data["team"]["labels"]["nodes"]:
        labels[l["name"]] = l["id"]
        print(f"  {l['name']}: {l['id'][:8]}...")
    return labels


# ============================================================
# Create cycles (Sprint 4–12)
# ============================================================

def create_cycles() -> dict:
    print("\n=== CREATING CYCLES (Sprint 4–12) ===\n")

    cycles = [
        ("Sprint 4: Post-Submission Stabilization", "2026-05-04", "2026-05-17"),
        ("Sprint 5: Research Velocity + Testing", "2026-05-18", "2026-05-31"),
        ("Sprint 6: VC Submission + SIL Core Theory", "2026-06-01", "2026-06-14"),
        ("Sprint 7: SIL Proofs + Dashboard Wiring", "2026-06-15", "2026-06-28"),
        ("Sprint 8: SIL Experiments + Platform Polish", "2026-06-29", "2026-07-12"),
        ("Sprint 9: SIL Paper + NeurIPS Review Prep", "2026-07-13", "2026-07-26"),
        ("Sprint 10: SIL Polish + Platform Intelligence", "2026-07-27", "2026-08-09"),
        ("Sprint 11: Submission Sprint + NeurIPS Response", "2026-08-10", "2026-08-23"),
        ("Sprint 12: Post-Submission + Q4 Planning", "2026-08-24", "2026-09-06"),
    ]

    cycle_ids = {}
    for name, start, end in cycles:
        rate_limit()
        data = gql(
            'mutation($input: CycleCreateInput!) { cycleCreate(input: $input) { success cycle { id } } }',
            {"input": {"name": name, "teamId": DW_TEAM_ID, "startsAt": start, "endsAt": end}},
        )
        cid = data["cycleCreate"]["cycle"]["id"]
        cycle_ids[name] = cid
        print(f"  Created: {name} ({cid[:8]}...)")

    return cycle_ids


# ============================================================
# Create issues
# ============================================================

def create_issues(project_ids: dict, cycle_ids: dict, label_ids: dict):
    print("\n=== CREATING ISSUES ===\n")

    # Cycle shortcuts
    s4 = cycle_ids.get("Sprint 4: Post-Submission Stabilization")
    s5 = cycle_ids.get("Sprint 5: Research Velocity + Testing")
    s6 = cycle_ids.get("Sprint 6: VC Submission + SIL Core Theory")
    s7 = cycle_ids.get("Sprint 7: SIL Proofs + Dashboard Wiring")
    s8 = cycle_ids.get("Sprint 8: SIL Experiments + Platform Polish")
    s9 = cycle_ids.get("Sprint 9: SIL Paper + NeurIPS Review Prep")
    s10 = cycle_ids.get("Sprint 10: SIL Polish + Platform Intelligence")
    s11 = cycle_ids.get("Sprint 11: Submission Sprint + NeurIPS Response")
    s12 = cycle_ids.get("Sprint 12: Post-Submission + Q4 Planning")

    # Project shortcuts
    RG = project_ids.get("reasoning-gaps")
    VC = project_ids.get("verification-complexity")
    SIL = project_ids.get("self-improvement-limits")
    AFT = project_ids.get("agent-failure-taxonomy")
    INFRA = project_ids.get("platform-infra")
    INTEL = project_ids.get("platform-intelligence")
    DASH = project_ids.get("dashboard")

    def L(*names):
        """Get label IDs by name."""
        return [label_ids[n] for n in names if n in label_ids]

    # Priority: 1=urgent, 2=high, 3=medium, 4=low
    issues = [
        # ================================================================
        # Sprint 4: Post-Submission Stabilization (May 4–17) — 10 issues
        # ================================================================

        # reasoning-gaps
        {
            "title": "Upload ReasonGap benchmark to HuggingFace",
            "description": "Publish the 9 benchmark tasks (B1-B9) as a HuggingFace dataset.\n\n- Create dataset card with documentation\n- Upload ~160K instances across all tasks\n- Include train/test splits and metadata\n- Tag with relevant categories\n- Reviewers expect accessible, downloadable benchmarks",
            "priority": 2, "projectId": RG,
            "labelIds": L("Research", "Submission"), "cycleId": s4,
        },

        # verification-complexity
        {
            "title": "VC: Define verification complexity hierarchy (Definitions 1-3)",
            "description": "Formalize the core definitions:\n- Definition 1: VC(F) — verification complexity of function class F\n- Definition 2: GV-Gap(F) — generation-verification gap\n- Definition 3: Model-relative variant VC_M(F)\n\nThese must be mathematically rigorous and connect to standard complexity theory.\nIf not solid by Apr 15, pivot target to ICLR 2027.",
            "priority": 1, "projectId": VC,
            "labelIds": L("Research"), "cycleId": s4,
        },
        {
            "title": "VC: Prove Verification Advantage theorem",
            "description": "First core theorem: prove that mitigation strategies (self-consistency, verification chains) work if and only if VC(F) falls within the augmented model class.\n\nThis establishes when and why verification-based approaches succeed or fail.",
            "priority": 1, "projectId": VC,
            "labelIds": L("Research"), "cycleId": s4,
        },

        # self-improvement-limits
        {
            "title": "SIL: Survey self-training literature",
            "description": "Systematic survey of self-training, self-refinement, and self-play papers.\n\n- Target 30+ papers including:\n  - Self-training: STaR, ReST, self-instruct\n  - Self-refinement: Self-Refine, Reflexion, iterative DPO\n  - Self-play: SPIN, debate, constitutional AI\n- Categorize by method, claims, theoretical backing\n- Phase 1 deliverable for the SIL project",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s4,
        },
        {
            "title": "SIL: Survey fixed-point theory and convergence",
            "description": "Survey mathematical foundations needed for SIL theory:\n\n- Banach fixed-point theorem and contraction mappings\n- Brouwer and Kakutani fixed-point theorems\n- PAC learning convergence bounds\n- Iterated function systems\n- Connections to self-improvement as fixed-point iteration",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s4,
        },

        # platform-infra
        {
            "title": "Merge main and research/reasoning-gaps branches",
            "description": "The two branches have diverged with conflicts in:\n- .claude/agents/*.md\n- orchestrator/package.json\n- TS utility files\n- site layout\n\nResolve all conflicts and unify into a clean main branch. This unblocks all other platform work.",
            "priority": 2, "projectId": INFRA,
            "labelIds": L("Infrastructure", "Tech Debt"), "cycleId": s4,
        },
        {
            "title": "Set up orchestrator unit test framework (Vitest)",
            "description": "Configure Vitest for the orchestrator package:\n\n- Add vitest dependency and config\n- Write initial tests for budget-tracker.ts (cost calculation, limit enforcement)\n- Write initial tests for backlog.ts (brief generation, prioritization)\n- Set up test utilities and mocks\n- Currently zero backend tests exist",
            "priority": 2, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s4,
        },
        {
            "title": "CI: Add test job to GitHub Actions",
            "description": "Extend the existing ci.yml workflow to run tests:\n\n- Add test step after build for orchestrator (vitest)\n- Add test step for site-next (if tests exist)\n- Run on PR and push to main\n- Currently CI only does build validation",
            "priority": 2, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s4,
        },
        {
            "title": "Add API rate limiting to Express server",
            "description": "Add express-rate-limit middleware to the orchestrator API:\n\n- Install express-rate-limit\n- Configure per-endpoint limits (e.g., 100/min for reads, 20/min for writes)\n- Exempt health check endpoint\n- Return proper 429 responses\n- No rate limiting currently exists",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure", "Security"), "cycleId": s4,
        },
        {
            "title": "Docker compose for local development",
            "description": "Create Docker setup for consistent local development:\n\n- Dockerfile for orchestrator (Node.js 22)\n- docker-compose.yml with orchestrator + PostgreSQL 16\n- Volume mounts for live reload\n- Environment variable configuration\n- README with setup instructions",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s4,
        },

        # ================================================================
        # Sprint 5: Research Velocity + Testing (May 18–31) — 10 issues
        # ================================================================

        # verification-complexity
        {
            "title": "VC: Prove Self-Consistency Condition theorem",
            "description": "Second core theorem: establish the conditions under which majority voting (self-consistency) improves accuracy.\n\nProve that self-consistency works when individual samples are weakly correct and errors are sufficiently independent — formalized via VC framework.",
            "priority": 1, "projectId": VC,
            "labelIds": L("Research"), "cycleId": s5,
        },
        {
            "title": "VC: Prove GV-Gap Collapse for planning tasks",
            "description": "Third core theorem: show that verification for HTN (Hierarchical Task Network) planning is coNP-hard, demonstrating that the generation-verification gap collapses.\n\nThis proves that some task classes cannot benefit from verification-based approaches.",
            "priority": 1, "projectId": VC,
            "labelIds": L("Research"), "cycleId": s5,
        },
        {
            "title": "VC: Run empirical validation experiments",
            "description": "Empirical validation of VC theory predictions:\n\n- Self-consistency on GSM8K (easy verification — expect improvement)\n- Self-consistency on PlanBench (hard verification — expect no improvement)\n- Compare improvement curves against theoretical predictions\n- Budget: ~$100",
            "priority": 2, "projectId": VC,
            "labelIds": L("Research", "Experiment"), "cycleId": s5,
        },

        # self-improvement-limits
        {
            "title": "SIL: Formalize self-improvement operators",
            "description": "Define the formal mathematical framework:\n\n- Capability space C and its metric\n- Self-training operator T: C → C\n- Self-refinement operator R: C → C\n- Self-play operator S: C × C → C\n- Properties: monotonicity, continuity, contraction conditions\n\nThis is the foundation for all subsequent proofs.",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s5,
        },

        # agent-failure-taxonomy
        {
            "title": "AFT: Survey agent failure reports",
            "description": "Collect and catalog 50+ documented agent failures:\n\n- Sources: ReAct, AutoGPT, Claude Code, SWE-agent papers and GitHub issues\n- LangChain, CrewAI, OpenDevin failure reports\n- Academic papers on agent limitations\n- For each: description, root cause, agent type, task type, severity\n- This forms the empirical basis for the taxonomy",
            "priority": 3, "projectId": AFT,
            "labelIds": L("Research"), "cycleId": s5,
        },

        # platform-infra
        {
            "title": "Add orchestrator integration tests",
            "description": "Write integration tests that hit real PostgreSQL:\n\n- Test daemon cycle (brief → session → result storage)\n- Test brief generation from different sources\n- Test knowledge graph queries\n- Test budget tracking with real DB operations\n- Requires test database setup in CI",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s5,
        },

        # dashboard
        {
            "title": "Wire dashboard project pages to live API",
            "description": "Connect site-next project pages to the orchestrator API through the Next.js proxy:\n\n- Project overview: /api/projects/:id\n- Eval results: /api/eval-results\n- Budget: /api/budget\n- Sessions: /api/sessions\n- Replace all mock/placeholder data with TanStack Query hooks\n- Currently all pages show static mock data",
            "priority": 2, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s5,
        },
        {
            "title": "Add site-next test coverage for API hooks",
            "description": "Write tests for TanStack Query hooks in site-next:\n\n- useProjects: fetching, caching, error states\n- useEvalData: filtering, pagination\n- useBudget: summary calculations\n- useSessions: real-time updates\n- Set up MSW (Mock Service Worker) for API mocking in tests",
            "priority": 3, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s5,
        },

        # reasoning-gaps
        {
            "title": "NeurIPS rebuttal preparation template",
            "description": "Pre-prepare a response framework for likely reviewer criticisms:\n\n- Benchmark scope (only 9 tasks, synthetic data)\n- Model selection (no GPT-4, no open-source frontier)\n- Complexity assumptions (gap taxonomy completeness)\n- Empirical vs theoretical balance\n- Template responses with placeholders for specific reviewer comments",
            "priority": 3, "projectId": RG,
            "labelIds": L("Paper"), "cycleId": s5,
        },

        # platform-intelligence
        {
            "title": "Implement adaptive session profiles (5 initial)",
            "description": "Create 5 session profiles with tailored configurations:\n\n- deep_proof: long duration, high budget, Opus model, formal verification focus\n- literature_sweep: medium duration, Sonnet model, breadth over depth\n- paper_writing: medium duration, Opus model, LaTeX-aware prompts\n- quick_fix: short duration, low budget, Haiku model, targeted fixes\n- latex_debug: short duration, Sonnet model, build error resolution\n\nEach profile: max_turns, max_duration, model, budget_cap, system_prompt_additions",
            "priority": 3, "projectId": INTEL,
            "labelIds": L("Feature", "Daemon"), "cycleId": s5,
        },

        # ================================================================
        # Sprint 6: VC Submission + SIL Core Theory (Jun 1–14) — 9 issues
        # ================================================================

        # verification-complexity
        {
            "title": "VC: Write paper draft",
            "description": "Write the full verification-complexity paper:\n\n- Introduction: verification as the key to reasoning improvement\n- Framework: VC(F), GV-Gap, model-relative variant\n- Theorem 1: Verification Advantage conditions\n- Theorem 2: Self-Consistency Condition\n- Theorem 3: GV-Gap Collapse for planning\n- Empirical validation results\n- Implications for reasoning improvement research\n\nTarget: NeurIPS 2026 or ICLR 2027 format.",
            "priority": 1, "projectId": VC,
            "labelIds": L("Paper"), "cycleId": s6,
        },
        {
            "title": "VC: Submit to NeurIPS or stage for ICLR 2027",
            "description": "Decision point based on paper readiness:\n\n- If paper is strong by May 6 NeurIPS deadline: submit to NeurIPS 2026\n- Otherwise: polish for ICLR 2027 (September deadline)\n- Prepare OpenReview submission or arXiv preprint\n- Ensure anonymization and checklist compliance",
            "priority": 1, "projectId": VC,
            "labelIds": L("Submission"), "cycleId": s6,
        },

        # self-improvement-limits
        {
            "title": "SIL: Prove self-training convergence bound",
            "description": "Core theorem: self-training without external verification converges to a fixed point bounded by the model's initial verification capability.\n\nProof strategy:\n- Model self-training as iterated operator T\n- Show T is a contraction mapping under verification capability bound\n- Apply Banach fixed-point theorem\n- Characterize the fixed point in terms of initial VC",
            "priority": 1, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s6,
        },
        {
            "title": "SIL: Prove self-refinement convergence bound",
            "description": "Extend convergence analysis to self-refinement (iterative editing):\n\n- Define self-refinement operator R\n- Show R also bounded by verification capability\n- Prove convergence rate may differ from self-training\n- Identify conditions where refinement outperforms training\n- Connect to Reflexion, Self-Refine empirical results",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s6,
        },

        # platform-intelligence
        {
            "title": "Integrate Semantic Scholar into scout workflow",
            "description": "Wire Semantic Scholar API into the literature monitoring pipeline:\n\n- Paper search by keyword and embedding similarity\n- Citation graph traversal (references and citations)\n- Author tracking for key researchers\n- Recommendations based on project knowledge graph\n- Feed results into literature.match events",
            "priority": 2, "projectId": INTEL,
            "labelIds": L("Feature"), "cycleId": s6,
        },
        {
            "title": "Set up arXiv daily ingestion pipeline",
            "description": "Automated daily monitoring of relevant arXiv papers:\n\n- RSS polling for cs.CL, cs.AI, cs.LG, cs.CC categories\n- Extract titles, abstracts, authors\n- Embed abstracts and match against project knowledge graph\n- Emit literature.match events for high-relevance papers\n- Store in PostgreSQL for deduplication",
            "priority": 2, "projectId": INTEL,
            "labelIds": L("Feature"), "cycleId": s6,
        },

        # platform-infra
        {
            "title": "CI: Add deploy verification step",
            "description": "Add post-deploy smoke test to CI/CD pipeline:\n\n- After deploy: curl /api/health on VPS\n- Verify response includes expected version\n- Check both orchestrator and site-next are responding\n- Alert on failure (Slack notification)\n- No deploy validation currently exists",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s6,
        },
        {
            "title": "Add CORS configuration to Express",
            "description": "Configure proper CORS on the orchestrator API:\n\n- Allowlist specific origins (research.oddurs.com, localhost:3000)\n- Set appropriate headers and methods\n- Handle preflight requests\n- Currently using permissive defaults which is a security risk",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure", "Security"), "cycleId": s6,
        },
        {
            "title": "Document operational runbooks",
            "description": "Create operational documentation for common VPS tasks:\n\n- VPS restart procedure\n- PostgreSQL recovery from backup\n- Daemon troubleshooting (stuck sessions, high memory)\n- SSL certificate renewal\n- Budget overspend response\n- Emergency contact and escalation",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure", "Documentation"), "cycleId": s6,
        },

        # ================================================================
        # Sprint 7: SIL Proofs + Dashboard Wiring (Jun 15–28) — 9 issues
        # ================================================================

        # self-improvement-limits
        {
            "title": "SIL: Characterize generation-verification gap",
            "description": "Key theoretical contribution: prove that the difficulty gap between generation and verification determines the maximum self-improvement gain.\n\n- Define GV-gap formally in capability space\n- Prove improvement bound is monotonic in GV-gap\n- Show large GV-gap → large improvement potential\n- Show collapsed GV-gap → no self-improvement possible\n- Connect to reasoning-gaps empirical findings",
            "priority": 1, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s7,
        },
        {
            "title": "SIL: Prove self-play separation result",
            "description": "Show that self-play can exceed self-training bounds when game structure provides implicit verification:\n\n- Define self-play operator S in terms of game-theoretic framework\n- Show S escapes self-training fixed point under specific conditions\n- Identify what makes games special (built-in verification via win/loss)\n- Connect to debate, constitutional AI, and SPIN results",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s7,
        },

        # dashboard
        {
            "title": "Wire eval heatmap to live data",
            "description": "Connect the AccuracyHeatmap component to real eval_results from the API:\n\n- Model × task accuracy grid with color coding\n- Click to drill down into per-condition results\n- Filter by model, task, condition\n- Pull data from /api/eval-results endpoint\n- Currently showing placeholder data",
            "priority": 2, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s7,
        },
        {
            "title": "Wire budget dashboard to live spending",
            "description": "Connect budget UI to real spending data:\n\n- Summary cards: total spent, remaining, burn rate\n- Burn chart: cumulative spending over time\n- Provider breakdown: Anthropic, OpenAI, OpenRouter\n- Pull from /api/budget and budget_logs table\n- Alert indicators for overspend thresholds",
            "priority": 2, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s7,
        },
        {
            "title": "Build real-time WebSocket event feed",
            "description": "Live daemon events in the dashboard logs page:\n\n- Connect to orchestrator WebSocket\n- Display session start/end, eval completions, errors\n- Connection status indicator with auto-reconnect\n- Filter by event type and project\n- Scrolling log with timestamps",
            "priority": 2, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s7,
        },
        {
            "title": "Build session transcript viewer",
            "description": "UI component for viewing daemon session transcripts:\n\n- Render conversation turns (human/assistant)\n- Expandable tool call details\n- Turn-by-turn navigation\n- Syntax highlighting for code blocks\n- Cost per turn display",
            "priority": 3, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s7,
        },

        # platform-intelligence
        {
            "title": "Implement review simulation system",
            "description": "Build a system to simulate peer reviews of paper drafts:\n\n- 5 reviewer personas: harsh methodologist, supportive mentor, domain skeptic, clarity stickler, novelty seeker\n- Generate synthetic reviews using Claude\n- Acceptance probability prediction\n- Estimated cost: ~$15-25 per review run\n- Feed results back into paper writing workflow",
            "priority": 3, "projectId": INTEL,
            "labelIds": L("Feature", "Research"), "cycleId": s7,
        },

        # agent-failure-taxonomy
        {
            "title": "AFT: Open coding of failure instances",
            "description": "Apply grounded theory open coding to the 50+ collected failure instances:\n\n- Read each failure report and assign initial codes\n- Group codes into preliminary categories\n- Identify recurring themes: tool misuse, planning failures, hallucination, context loss\n- Document coding decisions and rationale\n- This produces the initial taxonomy structure",
            "priority": 3, "projectId": AFT,
            "labelIds": L("Research"), "cycleId": s7,
        },

        # platform-infra
        {
            "title": "Add orchestrator integration tests (daemon cycle)",
            "description": "Integration tests for the full daemon cycle:\n\n- Test: brief generation → session creation → result storage\n- Test: knowledge graph query → response\n- Test: budget tracking with real PostgreSQL operations\n- Requires test database setup and teardown\n- Extends unit test framework from Sprint 4",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s7,
        },

        # ================================================================
        # Sprint 8: SIL Experiments + Platform Polish (Jun 29 – Jul 12) — 8 issues
        # ================================================================

        # self-improvement-limits
        {
            "title": "SIL: Fixed-point characterization",
            "description": "Complete the theoretical picture with fixed-point analysis:\n\n- Prove uniqueness conditions for self-improvement fixed points\n- Characterize dependence on initial conditions\n- Identify conditions for escaping local fixed points\n- Connect to empirical observations of training plateaus\n- Implications for curriculum design and data mixing",
            "priority": 1, "projectId": SIL,
            "labelIds": L("Research"), "cycleId": s8,
        },
        {
            "title": "SIL: Design empirical validation experiments",
            "description": "Design controlled experiments to validate SIL theory:\n\n- Arithmetic tasks: easy verification (check answer), expect convergence to high accuracy\n- Logic tasks: moderate verification, expect bounded improvement\n- Creative writing: hard verification, expect minimal self-improvement\n- Define metrics: accuracy trajectory, convergence rate, fixed-point gap\n- Budget: ~$200",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Research", "Experiment"), "cycleId": s8,
        },
        {
            "title": "SIL: Run empirical validation",
            "description": "Execute the designed self-improvement experiments:\n\n- Run self-training loops on arithmetic, logic, and writing tasks\n- Track accuracy trajectories over iterations\n- Measure convergence rates and final performance\n- Compare against theoretical predictions\n- Document any deviations from theory",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Research", "Experiment"), "cycleId": s8,
        },

        # dashboard
        {
            "title": "Build literature intelligence UI",
            "description": "Dashboard page for literature monitoring alerts:\n\n- List of matched papers with relevance scores\n- Project connections (which project each paper relates to)\n- Mark as read/relevant/irrelevant\n- Link to arXiv/Semantic Scholar\n- Filter by project, date range, relevance threshold",
            "priority": 3, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s8,
        },
        {
            "title": "Build paper build status UI",
            "description": "Dashboard component for LaTeX paper builds:\n\n- Trigger build button per project\n- Build progress indicator\n- Log output display (LaTeX warnings/errors)\n- PDF preview (embedded or download)\n- Build history with timestamps and status",
            "priority": 3, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s8,
        },

        # platform-intelligence
        {
            "title": "Add OpenReview API integration",
            "description": "Integrate with OpenReview for review intelligence:\n\n- Scrape reviewer comments from NeurIPS 2024/2025 papers\n- Extract common objection patterns and reviewer preferences\n- Build a database of review language and scoring patterns\n- Use for calibrating the review simulation system\n- Focus on papers similar to our research topics",
            "priority": 3, "projectId": INTEL,
            "labelIds": L("Feature", "Research"), "cycleId": s8,
        },

        # platform-infra
        {
            "title": "Update CI deploy to restart both services",
            "description": "Enhance CI/CD to handle full deployment:\n\n- Build orchestrator TypeScript\n- Build site-next\n- SSH to VPS and restart deepwork-daemon.service\n- SSH to VPS and restart deepwork-site.service\n- Sequential deployment with rollback on failure\n- Run deploy verification step after restart",
            "priority": 2, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s8,
        },
        {
            "title": "CI: Add lint job and pre-commit hooks",
            "description": "Add code quality checks to CI and local development:\n\n- Add ESLint step to GitHub Actions workflow\n- Configure pre-commit hooks (husky) for typecheck + lint\n- Ensure consistent code style across orchestrator and site-next\n- Fix any existing lint violations",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s8,
        },

        # ================================================================
        # Sprint 9: SIL Paper + NeurIPS Review Prep (Jul 13–26) — 7 issues
        # ================================================================

        # self-improvement-limits
        {
            "title": "SIL: Write paper draft (ICLR 2027 format)",
            "description": "Write the full self-improvement-limits paper for ICLR 2027:\n\n- Introduction: can AI systems improve themselves without bound?\n- Framework: capability space, operators T/R/S\n- Theorem 1: Self-training convergence bound\n- Theorem 2: Self-refinement convergence bound\n- Theorem 3: GV-gap determines improvement ceiling\n- Theorem 4: Self-play separation result\n- Empirical validation across task difficulties\n- Implications for AI safety and scaling",
            "priority": 1, "projectId": SIL,
            "labelIds": L("Paper"), "cycleId": s9,
        },
        {
            "title": "SIL: Internal review simulation",
            "description": "Run the review simulation system on the SIL paper draft:\n\n- Generate 5 synthetic reviews from different personas\n- Identify weaknesses and blind spots\n- Prioritize revisions based on review feedback\n- Iterate on paper to address major concerns\n- Target: predicted acceptance score 7.5+/10",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Paper", "Research"), "cycleId": s9,
        },

        # reasoning-gaps
        {
            "title": "NeurIPS: Prepare rebuttal materials",
            "description": "Pre-prepare responses to likely reviewer criticisms:\n\n- Benchmark scope: justify 9 tasks, plan for expansion\n- Model selection: explain budget constraints, coverage rationale\n- Complexity assumptions: defend gap taxonomy completeness\n- Additional experiments ready to run if requested\n- Template with placeholders for specific reviewer points",
            "priority": 2, "projectId": RG,
            "labelIds": L("Paper", "Submission"), "cycleId": s9,
        },

        # agent-failure-taxonomy
        {
            "title": "AFT: Controlled experiment design",
            "description": "Design experiments to reproduce key failure modes:\n\n- Select 10-15 representative failures from taxonomy\n- Define reproduction procedures across frameworks:\n  - LangChain agents\n  - AutoGPT\n  - CrewAI multi-agent\n- Define metrics: failure rate, time-to-failure, recovery rate\n- Controlled variables: model, prompt, task complexity",
            "priority": 3, "projectId": AFT,
            "labelIds": L("Research", "Experiment"), "cycleId": s9,
        },

        # platform-intelligence
        {
            "title": "Implement meta-learning data collection",
            "description": "Track session effectiveness for auto-tuning:\n\n- Log per-session: agent type, model, task type, project phase, outcome quality\n- Aggregation tables: effectiveness by profile, model, task type\n- Store in PostgreSQL with efficient querying\n- Foundation for automatic profile tuning in Sprint 10",
            "priority": 3, "projectId": INTEL,
            "labelIds": L("Feature", "Daemon"), "cycleId": s9,
        },

        # dashboard
        {
            "title": "Build command palette (Cmd+K)",
            "description": "Implement a cmdk-based command palette for the dashboard:\n\n- Cmd+K to open\n- Search projects by name\n- Jump to specific agents/sessions\n- Trigger paper builds\n- Quick navigation to any page\n- Recent actions history",
            "priority": 3, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s9,
        },

        # platform-infra
        {
            "title": "Implement structured JSON logging",
            "description": "Replace unstructured console output with structured logging:\n\n- JSON log format for orchestrator\n- Include: timestamp, level, component, message, metadata\n- Log rotation (daily, 7-day retention)\n- Filtering by level and component\n- Foundation for future alerting\n- Currently relies on unstructured journalctl output",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s9,
        },

        # ================================================================
        # Sprint 10: SIL Polish + Platform Intelligence (Jul 27 – Aug 9) — 7 issues
        # ================================================================

        # self-improvement-limits
        {
            "title": "SIL: Paper revision and polish",
            "description": "Incorporate review simulation feedback and polish the paper:\n\n- Address all major concerns from synthetic reviews\n- Tighten proof presentations\n- Strengthen empirical analysis\n- Improve clarity and flow\n- Target predicted acceptance score 7.5+/10",
            "priority": 1, "projectId": SIL,
            "labelIds": L("Paper"), "cycleId": s10,
        },
        {
            "title": "SIL: Supplementary materials preparation",
            "description": "Prepare supplementary materials for ICLR submission:\n\n- Full proofs appendix (all lemmas and theorems)\n- Experiment configurations and hyperparameters\n- Additional empirical results and ablations\n- Code archive for reproducibility\n- Dataset documentation",
            "priority": 2, "projectId": SIL,
            "labelIds": L("Paper", "Submission"), "cycleId": s10,
        },

        # platform-intelligence
        {
            "title": "Implement cross-project knowledge transfer",
            "description": "Build CrossProjectAnalyzer for sharing insights across research projects:\n\n- Find insights from project A relevant to project B via KG similarity\n- Detect overlapping literature and methodology\n- Surface connections between theoretical frameworks\n- Auto-suggest cross-references for papers\n- Example: SIL verification bounds ↔ VC theory",
            "priority": 3, "projectId": INTEL,
            "labelIds": L("Feature", "Research"), "cycleId": s10,
        },
        {
            "title": "Implement session profile auto-tuning",
            "description": "Use meta-learning data to automatically adjust session profiles:\n\n- Analyze effectiveness data from Sprint 9 collection\n- Identify which profile parameters correlate with success\n- Auto-adjust: budget caps, model selection, max_turns\n- A/B test profile variants\n- Report tuning decisions to dashboard",
            "priority": 4, "projectId": INTEL,
            "labelIds": L("Feature", "Daemon"), "cycleId": s10,
        },

        # agent-failure-taxonomy
        {
            "title": "AFT: Run controlled failure reproduction",
            "description": "Execute the controlled experiments designed in Sprint 9:\n\n- Run reproduction procedures across LangChain, AutoGPT, CrewAI\n- Document failure rates, conditions, and patterns\n- Compare observed failures against taxonomy predictions\n- Identify any new failure modes not in initial taxonomy\n- Budget: ~$200-300",
            "priority": 3, "projectId": AFT,
            "labelIds": L("Research", "Experiment"), "cycleId": s10,
        },

        # dashboard
        {
            "title": "Build agent activity heatmap",
            "description": "Calendar heatmap visualization of session activity:\n\n- GitHub contribution graph style layout\n- Color intensity = number of sessions per day\n- Click to see session details for that day\n- Filter by project and agent type\n- Show last 6 months of activity",
            "priority": 3, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s10,
        },

        # platform-infra
        {
            "title": "Add API versioning headers",
            "description": "Add version information to the orchestrator API:\n\n- X-API-Version response header on all endpoints\n- Support /v1/ prefix for future versioning\n- Version from package.json\n- Document versioning strategy",
            "priority": 4, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": s10,
        },

        # ================================================================
        # Sprint 11: Submission Sprint + NeurIPS Response (Aug 10–23) — 6 issues
        # ================================================================

        # self-improvement-limits
        {
            "title": "SIL: Submit to ICLR 2027",
            "description": "Final submission of the self-improvement-limits paper:\n\n- Final package: main paper, supplementary materials\n- Submit on OpenReview for ICLR 2027\n- Post arXiv preprint (anonymous version)\n- Prepare anonymous code repository\n- Verify all checklist items and compliance",
            "priority": 1, "projectId": SIL,
            "labelIds": L("Submission"), "cycleId": s11,
        },

        # verification-complexity
        {
            "title": "VC: ICLR 2027 submission (if pivoted from NeurIPS)",
            "description": "If VC paper was deferred from NeurIPS 2026:\n\n- Polish with extended proofs and additional experiments\n- Submit to ICLR 2027 (September deadline)\n- Include improvements based on any informal feedback\n- Post arXiv preprint",
            "priority": 1, "projectId": VC,
            "labelIds": L("Submission"), "cycleId": s11,
        },

        # reasoning-gaps
        {
            "title": "NeurIPS: Process reviews and draft rebuttal",
            "description": "Handle NeurIPS review response:\n\n- Analyze all reviewer comments carefully\n- Draft point-by-point responses\n- Identify any additional experiments needed\n- Run quick experiments if requested by reviewers\n- Prepare revised paper sections if allowed",
            "priority": 1, "projectId": RG,
            "labelIds": L("Paper", "Submission"), "cycleId": s11,
        },

        # agent-failure-taxonomy
        {
            "title": "AFT: Draft taxonomy and paper outline",
            "description": "Consolidate research into paper-ready form:\n\n- Finalize hierarchical taxonomy from coding and experiments\n- Write paper outline with section structure\n- Include frequency distributions of failure types\n- Preliminary related work section\n- Target venue: ACL 2027 (deadline Feb 2027)",
            "priority": 3, "projectId": AFT,
            "labelIds": L("Paper", "Research"), "cycleId": s11,
        },

        # dashboard
        {
            "title": "Add e2e smoke tests (Playwright)",
            "description": "End-to-end tests for critical dashboard flows:\n\n- Sign in flow\n- View dashboard overview\n- Navigate to project page\n- View eval data with filters\n- Check responsive layout\n- Run in CI on deploy",
            "priority": 3, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s11,
        },

        # platform-infra
        {
            "title": "Implement secrets rotation automation",
            "description": "Script for rotating API keys and secrets:\n\n- Rotate: ANTHROPIC_API_KEY, OPENAI_API_KEY, LINEAR_API_KEY, DEEPWORK_API_KEY\n- Update .env on VPS\n- Restart affected services\n- Verify services healthy after rotation\n- Document rotation schedule (quarterly)",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Infrastructure", "Security"), "cycleId": s11,
        },

        # ================================================================
        # Sprint 12: Post-Submission + Q4 Planning (Aug 24 – Sep 6) — 7 issues
        # ================================================================

        # reasoning-gaps
        {
            "title": "NeurIPS: Submit rebuttal",
            "description": "Submit final rebuttal responses during the NeurIPS review period:\n\n- Finalize point-by-point responses\n- Include any additional experiment results\n- Submit within deadline\n- Monitor for reviewer follow-up questions",
            "priority": 1, "projectId": RG,
            "labelIds": L("Submission"), "cycleId": s12,
        },
        {
            "title": "NeurIPS: Camera-ready preparation (conditional)",
            "description": "If paper is accepted, prepare camera-ready version:\n\n- De-anonymize: add author names, affiliations, acknowledgments\n- Final figure polish\n- Update supplementary materials\n- Prepare poster/presentation materials\n- Upload to OpenReview by camera-ready deadline",
            "priority": 2, "projectId": RG,
            "labelIds": L("Paper", "Submission"), "cycleId": s12,
        },
        {
            "title": "NeurIPS: Rejection contingency plan",
            "description": "If paper is rejected, prepare recovery plan:\n\n- Analyze reviewer feedback thoroughly\n- Identify major revision priorities\n- Select resubmission venue (ICLR 2027, ICML 2027, or workshop)\n- Create revision timeline\n- Decide whether to pivot scope or double down",
            "priority": 2, "projectId": RG,
            "labelIds": L("Paper"), "cycleId": s12,
        },

        # platform-intelligence
        {
            "title": "Q4 research portfolio planning",
            "description": "Strategic planning for Q4 2026:\n\n- Kill/pivot decisions for all active projects\n- Plan ICML 2027 (January deadline) targets\n- Plan ACL 2027 (February deadline) targets\n- Resource allocation across projects\n- Budget planning for Q4",
            "priority": 2, "projectId": INTEL,
            "labelIds": L("Research"), "cycleId": s12,
        },
        {
            "title": "Implement cost optimization feedback loop",
            "description": "Analyze and optimize API spending:\n\n- Calculate cost-per-insight by model and task type\n- Auto-suggest cheaper models where expensive ones don't add value\n- Identify sessions with poor cost/value ratio\n- Dashboard widget showing optimization recommendations\n- Target: 20% cost reduction without quality loss",
            "priority": 3, "projectId": INTEL,
            "labelIds": L("Feature", "Daemon"), "cycleId": s12,
        },

        # platform-infra
        {
            "title": "Year 1 retrospective data collection",
            "description": "Collect metrics for the first year of DeepWork operation:\n\n- Papers submitted and acceptance rates\n- Total API costs by provider and project\n- Session counts and success rates\n- Knowledge graph growth metrics\n- Platform uptime and reliability\n- Generate retrospective report",
            "priority": 3, "projectId": INFRA,
            "labelIds": L("Documentation"), "cycleId": s12,
        },

        # dashboard
        {
            "title": "Build knowledge graph visualization UI",
            "description": "Interactive visualization of the knowledge graph:\n\n- D3 or visx force-directed graph layout\n- Nodes: claims, evidence, papers, contradictions\n- Edges: supports, contradicts, cites, extends\n- Click to expand node details\n- Filter by project and relationship type\n- Zoom and pan controls",
            "priority": 4, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": s12,
        },

        # ================================================================
        # Backlog (no sprint) — 3 issues
        # ================================================================

        {
            "title": "HuggingFace leaderboard for ReasonGap benchmark",
            "description": "Create a community leaderboard for external submissions to the ReasonGap benchmark:\n\n- Set up HuggingFace Spaces leaderboard\n- Define submission format and evaluation criteria\n- Automated evaluation pipeline\n- Drives citations and community engagement\n- Depends on benchmark upload (Sprint 4)",
            "priority": 4, "projectId": RG,
            "labelIds": L("Research"), "cycleId": None,
        },
        {
            "title": "VPS scale-up evaluation (CPX21 → CPX31)",
            "description": "Evaluate whether to upgrade the Hetzner VPS:\n\n- Current: CPX21 (3 vCPU, 4GB RAM, 80GB disk)\n- Target: CPX31 (4 vCPU, 8GB RAM, 160GB disk)\n- Monitor peak memory usage during concurrent sessions\n- Cost comparison (~€4/month difference)\n- Decision: upgrade if >80% memory utilization during sessions",
            "priority": 4, "projectId": INFRA,
            "labelIds": L("Infrastructure"), "cycleId": None,
        },
        {
            "title": "Build mobile-responsive dashboard",
            "description": "Make the site-next dashboard work on mobile devices:\n\n- Responsive breakpoints for tablet and phone\n- Sidebar collapse to hamburger menu\n- Touch-friendly targets (44px minimum)\n- Test on iOS Safari and Android Chrome\n- Priority pages: overview, budget, sessions",
            "priority": 4, "projectId": DASH,
            "labelIds": L("Feature"), "cycleId": None,
        },
    ]

    created = 0
    failed = 0
    for issue in issues:
        rate_limit()

        inp = {
            "title": issue["title"],
            "description": issue.get("description", ""),
            "teamId": DW_TEAM_ID,
            "priority": issue.get("priority", 3),
            "labelIds": issue.get("labelIds", []),
        }

        if issue.get("projectId"):
            inp["projectId"] = issue["projectId"]

        if issue.get("cycleId"):
            inp["cycleId"] = issue["cycleId"]
            inp["stateId"] = STATE_TODO
        else:
            inp["stateId"] = STATE_BACKLOG

        try:
            data = gql(
                'mutation($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { identifier title } } }',
                {"input": inp},
            )
            ident = data["issueCreate"]["issue"]["identifier"]
            print(f"  {ident}: {issue['title'][:70]}")
            created += 1
        except Exception as e:
            print(f"  FAILED: {issue['title'][:50]}: {e}")
            failed += 1

    print(f"\n  Created {created}/{len(issues)} issues ({failed} failed)")


# ============================================================
# Main
# ============================================================

def main():
    print("DeepWork Linear Roadmap Expansion")
    print("Sprints 4–12 (May 4 – Sep 6, 2026)")
    print("=" * 50)

    # Fetch existing data
    project_ids = fetch_projects()
    label_ids = fetch_labels()

    # Verify required projects exist
    required = ["reasoning-gaps", "verification-complexity", "self-improvement-limits",
                "agent-failure-taxonomy", "platform-infra", "platform-intelligence", "dashboard"]
    missing = [p for p in required if p not in project_ids]
    if missing:
        print(f"\nERROR: Missing projects: {missing}")
        print("Run setup-linear.py first to create projects.")
        sys.exit(1)

    # Create cycles
    cycle_ids = create_cycles()

    # Create issues
    create_issues(project_ids, cycle_ids, label_ids)

    print("\n" + "=" * 50)
    print("DONE!")
    print(f"\nSummary:")
    print(f"  Cycles created: 9 (Sprint 4–12)")
    print(f"  Issues created: ~76")
    print(f"  Timeframe: May 4 – Sep 6, 2026")


if __name__ == "__main__":
    main()
