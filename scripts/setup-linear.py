#!/usr/bin/env python3
"""
Linear workspace setup script for DeepWork.
Archives EV debris and creates DW projects, cycles, labels, and issues.
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
EV_TEAM_ID = "8513b969-e338-4196-97f9-1a15bcaf9962"

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
# Phase 1: Archive EV debris
# ============================================================

def archive_ev():
    print("\n=== ARCHIVING EV DEBRIS ===\n")

    # Archive EV projects
    print("Fetching EV projects...")
    data = gql(f'{{ team(id: "{EV_TEAM_ID}") {{ projects(first: 100) {{ nodes {{ id name }} }} }} }}')
    projects = data["team"]["projects"]["nodes"]
    print(f"  Found {len(projects)} EV projects to archive")

    for p in projects:
        rate_limit()
        try:
            gql('mutation($id: String!) { projectArchive(id: $id) { success } }', {"id": p["id"]})
            print(f"  Archived project: {p['name']}")
        except Exception as e:
            print(f"  Failed to archive project {p['name']}: {e}")

    # Archive EV issues
    print("\nFetching EV issues...")
    data = gql(f'{{ team(id: "{EV_TEAM_ID}") {{ issues(first: 250) {{ nodes {{ id identifier }} }} }} }}')
    issues = data["team"]["issues"]["nodes"]
    print(f"  Found {len(issues)} EV issues to archive")

    for i in issues:
        rate_limit()
        try:
            gql('mutation($id: String!) { issueArchive(id: $id) { success } }', {"id": i["id"]})
        except Exception:
            pass
    print(f"  Archived {len(issues)} issues")

    # Archive EV cycles
    print("\nFetching EV cycles...")
    data = gql(f'{{ team(id: "{EV_TEAM_ID}") {{ cycles(first: 100) {{ nodes {{ id number }} }} }} }}')
    cycles = data["team"]["cycles"]["nodes"]
    print(f"  Found {len(cycles)} EV cycles to archive")

    for c in cycles:
        rate_limit()
        try:
            gql('mutation($id: String!) { cycleArchive(id: $id) { success } }', {"id": c["id"]})
        except Exception:
            pass
    print(f"  Archived {len(cycles)} cycles")


# ============================================================
# Phase 2: Create DW projects
# ============================================================

def create_projects() -> dict:
    print("\n=== CREATING DW PROJECTS ===\n")

    projects = [
        ("reasoning-gaps", "NeurIPS 2026 paper on reasoning gaps in LLMs. Deadline: May 5, 2026."),
        ("verification-complexity", "Formal verification complexity theory for LLM reasoning. Target: NeurIPS/ICLR."),
        ("self-improvement-limits", "Theoretical limits of LLM self-improvement. Target: ICLR 2027 (Oct 2026)."),
        ("agent-failure-taxonomy", "Taxonomy of agent failure modes. Target: ACL 2027 (Feb 2027)."),
        ("platform-infra", "VPS, SSL, monitoring, backups, Slack, Sentry — infrastructure serving research."),
        ("platform-intelligence", "Adaptive sessions, literature, meta-learning, closed-loop, review-sim."),
        ("dashboard", "site-next dashboard: API wiring, auth, real-time updates."),
    ]

    project_ids = {}
    for name, desc in projects:
        rate_limit()
        data = gql(
            'mutation($input: ProjectCreateInput!) { projectCreate(input: $input) { success project { id } } }',
            {"input": {"name": name, "description": desc, "teamIds": [DW_TEAM_ID]}},
        )
        pid = data["projectCreate"]["project"]["id"]
        project_ids[name] = pid
        print(f"  Created project: {name} ({pid[:8]})")

    return project_ids


# ============================================================
# Phase 3: Create cycles
# ============================================================

def create_cycles() -> dict:
    print("\n=== CREATING CYCLES ===\n")

    cycles = [
        ("Sprint 1: NeurIPS Crunch", "2026-03-23", "2026-04-05"),
        ("Sprint 2: NeurIPS Polish", "2026-04-06", "2026-04-19"),
        ("Sprint 3: NeurIPS Final", "2026-04-20", "2026-05-03"),
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
        print(f"  Created cycle: {name} ({cid[:8]})")

    return cycle_ids


# ============================================================
# Phase 4: Create labels
# ============================================================

def create_labels() -> dict:
    print("\n=== CREATING LABELS ===\n")

    # Already exist: Feature, Improvement, Bug
    existing = {
        "Feature": "bbe153b8-a16b-4394-8c3f-898fced08b87",
        "Improvement": "ad444d04-d5a5-4bd4-ab81-5b35b2705b21",
        "Bug": "1f417acd-5f38-49dc-ba5f-f417338e3b87",
    }

    new_labels = [
        "Research", "Infrastructure", "Documentation", "Tech Debt", "Security",
        "Submission", "Paper", "Experiment", "Daemon", "Blocking",
    ]

    label_ids = dict(existing)
    for name in new_labels:
        rate_limit()
        try:
            data = gql(
                'mutation($input: IssueLabelCreateInput!) { issueLabelCreate(input: $input) { success issueLabel { id } } }',
                {"input": {"name": name, "teamId": DW_TEAM_ID}},
            )
            lid = data["issueLabelCreate"]["issueLabel"]["id"]
            label_ids[name] = lid
            print(f"  Created label: {name} ({lid[:8]})")
        except Exception as e:
            print(f"  Failed to create label {name}: {e}")

    return label_ids


# ============================================================
# Phase 5: Create issues
# ============================================================

def create_issues(project_ids: dict, cycle_ids: dict, label_ids: dict):
    print("\n=== CREATING ISSUES ===\n")

    s1 = cycle_ids.get("Sprint 1: NeurIPS Crunch")
    s2 = cycle_ids.get("Sprint 2: NeurIPS Polish")
    s3 = cycle_ids.get("Sprint 3: NeurIPS Final")

    def L(*names):
        """Get label IDs by name."""
        return [label_ids[n] for n in names if n in label_ids]

    # Priority: 1=urgent, 2=high, 3=medium, 4=low
    issues = [
        # ---- Sprint 1: NeurIPS Crunch (Mar 23 – Apr 5) ----

        # reasoning-gaps
        {
            "title": "Page compression: cut main body 18→9 pages",
            "description": "Current paper is 18 pages. NeurIPS limit is 9 pages main body + unlimited appendix.\n\nApproach:\n- Move detailed proofs to supplementary\n- Compress related work\n- Tighten experimental results presentation\n- Move per-model breakdowns to appendix\n\nRef: docs/roadmaps/neurips-submission.md",
            "priority": 1, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper", "Submission", "Blocking"), "cycleId": s1,
        },
        {
            "title": "Switch to NeurIPS 2026 LaTeX format",
            "description": "Replace current custom preamble with official NeurIPS 2026 style files.\n- Download from neurips.cc\n- Update \\documentclass and preamble\n- Verify page limits and margins",
            "priority": 2, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper", "Submission"), "cycleId": s1,
        },
        {
            "title": "Double-blind anonymization pass",
            "description": "Remove all identifying information:\n- Author names and affiliations\n- Self-citations that reveal identity\n- Acknowledgments\n- GitHub/data URLs that could identify authors\n- Institution-specific references",
            "priority": 2, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper", "Submission"), "cycleId": s1,
        },

        # platform-infra
        {
            "title": "SSL/HTTPS: DNS A record + certbot for research.oddurs.com",
            "description": "Set up HTTPS on the VPS:\n1. Verify DNS A record for research.oddurs.com → 89.167.5.50\n2. Run certbot --nginx for SSL certificate\n3. Verify HTTPS works for both dashboard and API\n4. Set up auto-renewal",
            "priority": 2, "projectId": project_ids["platform-infra"],
            "labelIds": L("Infrastructure", "Blocking"), "cycleId": s1,
        },
        {
            "title": "Slack workspace + webhook for daemon notifications",
            "description": "Create Slack workspace and configure webhook:\n1. Create workspace or channel\n2. Set up incoming webhook\n3. Add SLACK_WEBHOOK_URL to VPS .env\n4. Verify notifier.ts sends to Slack",
            "priority": 2, "projectId": project_ids["platform-infra"],
            "labelIds": L("Infrastructure"), "cycleId": s1,
        },
        {
            "title": "Uptime monitoring with Betterstack",
            "description": "Set up Betterstack (or similar) to monitor:\n- API health endpoint\n- Dashboard availability\n- Alert via Slack/email on downtime",
            "priority": 2, "projectId": project_ids["platform-infra"],
            "labelIds": L("Infrastructure"), "cycleId": s1,
        },
        {
            "title": "Linear API integration for orchestrator",
            "description": "Build orchestrator/src/linear.ts — thin GraphQL client for Linear.\n\nMethods: getTodoIssues, getInProgressIssues, transitionIssue, addComment, createIssue, issueToBrief.\n\nWire into research-planner.ts (linear_driven strategy) and daemon.ts (post-session updates).\n\nThis issue tracks the work defined in the Linear integration plan.",
            "priority": 2, "projectId": project_ids["platform-infra"],
            "labelIds": L("Infrastructure", "Daemon"), "cycleId": s1,
        },
        {
            "title": "Merge main ↔ research/reasoning-gaps branches",
            "description": "These branches have diverged with conflicts in:\n- .claude/agents/*.md\n- orchestrator/package.json\n- TS utility files\n- site layout\n\nResolve conflicts and merge to unify the codebase.",
            "priority": 3, "projectId": project_ids["platform-infra"],
            "labelIds": L("Infrastructure", "Tech Debt"), "cycleId": s1,
        },

        # ---- Sprint 2: NeurIPS Polish (Apr 6 – Apr 19) ----

        # reasoning-gaps
        {
            "title": "NeurIPS checklist + ethics statement",
            "description": "Complete the NeurIPS paper checklist:\n- Broader impact statement\n- Ethics statement\n- Reproducibility checklist\n- Limitations section\n\nEnsure all checklist items are addressed in the paper.",
            "priority": 2, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper", "Submission"), "cycleId": s2,
        },
        {
            "title": "Supplementary materials package",
            "description": "Prepare supplementary PDF and code archive:\n- Extended proofs and derivations\n- Per-model detailed results\n- Additional figures and analysis\n- Code README for reproducibility\n- Dataset documentation",
            "priority": 2, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper", "Submission"), "cycleId": s2,
        },
        {
            "title": "Figure quality pass: vector PDF, colorblind-safe",
            "description": "Audit all figures:\n- Convert all to vector PDF (no rasterized plots)\n- Apply colorblind-safe palette (e.g., Okabe-Ito)\n- Verify legibility at print size\n- Consistent font sizes and styling\n- High-resolution for any raster elements",
            "priority": 2, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper"), "cycleId": s2,
        },
        {
            "title": "Number consistency audit (stat macros)",
            "description": "Ensure all numbers in the paper are generated from data:\n- Create LaTeX macros for key statistics\n- Cross-reference with analysis output\n- Verify all claims match actual results\n- Check p-values, effect sizes, confidence intervals",
            "priority": 2, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper"), "cycleId": s2,
        },
        {
            "title": "Upload datasets to Zenodo + HuggingFace",
            "description": "Prepare and upload benchmark datasets:\n- Clean and package B1-B9 datasets\n- Upload to Zenodo for DOI\n- Upload to HuggingFace Datasets for accessibility\n- Create dataset cards with documentation\n- Generate anonymized URLs for paper references",
            "priority": 3, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Research", "Submission"), "cycleId": s2,
        },

        # verification-complexity
        {
            "title": "Define VC(F) formally",
            "description": "Formalize the Verification Complexity function VC(F):\n- Define over function classes F\n- Establish relationship to computational complexity\n- Prove basic properties (monotonicity, compositionality)\n- Connect to existing complexity-theoretic notions",
            "priority": 2, "projectId": project_ids["verification-complexity"],
            "labelIds": L("Research"), "cycleId": s2,
        },
        {
            "title": "Prove Verification Advantage theorem",
            "description": "Prove the main theorem: there exist function classes where verification is asymptotically easier than generation.\n\nThis is the core theoretical contribution of the verification-complexity paper.",
            "priority": 2, "projectId": project_ids["verification-complexity"],
            "labelIds": L("Research"), "cycleId": s2,
        },

        # platform-infra
        {
            "title": "Sentry error tracking for orchestrator",
            "description": "Set up Sentry for the orchestrator:\n- Create Sentry project\n- Add @sentry/node dependency\n- Initialize in index.ts\n- Add SENTRY_DSN to VPS .env\n- Verify errors are captured",
            "priority": 3, "projectId": project_ids["platform-infra"],
            "labelIds": L("Infrastructure"), "cycleId": s2,
        },
        {
            "title": "Nightly DB backup to Hetzner Storage Box",
            "description": "Set up automated PostgreSQL backups:\n- Create Hetzner Storage Box (or use existing)\n- Write pg_dump backup script\n- Create systemd timer for nightly runs\n- Test restore procedure\n- Set up retention policy (keep 7 daily, 4 weekly)",
            "priority": 3, "projectId": project_ids["platform-infra"],
            "labelIds": L("Infrastructure"), "cycleId": s2,
        },

        # ---- Sprint 3: NeurIPS Final (Apr 20 – May 3) ----

        # reasoning-gaps
        {
            "title": "Final LaTeX checks: zero warnings, all refs resolved",
            "description": "Pre-submission LaTeX audit:\n- Fix all LaTeX warnings\n- Verify all \\ref and \\cite resolve\n- Check no overfull/underfull boxes\n- Verify page count within limits\n- Clean up temporary comments and TODOs",
            "priority": 1, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper", "Submission", "Blocking"), "cycleId": s3,
        },
        {
            "title": "Full proofreading pass",
            "description": "Complete proofreading of the entire paper:\n- Grammar and spelling\n- Logical flow between sections\n- Clarity of arguments\n- Consistency of notation\n- Abstract accurately reflects content",
            "priority": 1, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Paper", "Submission"), "cycleId": s3,
        },
        {
            "title": "Submit abstract on OpenReview",
            "description": "Submit the paper abstract on OpenReview before the abstract deadline.\n- Register on OpenReview if needed\n- Select NeurIPS 2026 submission track\n- Enter title, abstract, keywords\n- Confirm subject areas",
            "priority": 1, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Submission", "Blocking"), "cycleId": s3,
        },
        {
            "title": "Submit full paper on OpenReview",
            "description": "Submit the complete paper PDF + supplementary on OpenReview.\n- Upload main PDF\n- Upload supplementary materials\n- Upload code (if required)\n- Verify formatting compliance\n- Confirm submission",
            "priority": 1, "projectId": project_ids["reasoning-gaps"],
            "labelIds": L("Submission", "Blocking"), "cycleId": s3,
        },

        # verification-complexity
        {
            "title": "Prove GV-Gap Collapse for planning domains",
            "description": "Prove that the Generation-Verification gap collapses for planning domains:\n- Formalize planning domain as function class\n- Show VC(Planning) ~ GC(Planning)\n- Connect to PSPACE-completeness of planning\n- Implications for reasoning gap Type 5 (intractability)",
            "priority": 2, "projectId": project_ids["verification-complexity"],
            "labelIds": L("Research"), "cycleId": s3,
        },
        {
            "title": "Map VC onto 6 gap types from reasoning-gaps",
            "description": "Connect verification complexity to the 6 reasoning gap types:\n- Type 1 (attention): relate to circuit depth\n- Type 2 (serial): relate to sequential verification\n- Type 3 (knowledge): relate to lookup complexity\n- Type 4 (calibration): relate to distribution verification\n- Type 5 (intractability): relate to GV-Gap Collapse\n- Type 6 (architecture): relate to architectural VC",
            "priority": 2, "projectId": project_ids["verification-complexity"],
            "labelIds": L("Research"), "cycleId": s3,
        },
        {
            "title": "Design empirical validation experiments for VC theory",
            "description": "Design experiments to validate VC predictions:\n- Select function classes with known VC properties\n- Design tasks that probe verification vs generation\n- Plan model selection (small→large)\n- Define success metrics",
            "priority": 3, "projectId": project_ids["verification-complexity"],
            "labelIds": L("Research", "Experiment"), "cycleId": s3,
        },

        # ---- Backlog: Platform Intelligence ----

        {
            "title": "Adaptive session profiles (11 profiles)",
            "description": "Implement 11 session profiles for the daemon:\n- Profiles: deep-research, quick-fix, writing-sprint, analysis-run, etc.\n- Each profile has: max_turns, max_duration, model, budget, agent_type\n- Profile selection based on issue type/priority\n\nRef: docs/roadmaps/adaptive-sessions.md",
            "priority": 3, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature", "Daemon"), "cycleId": None,
        },
        {
            "title": "Session escalation mechanism",
            "description": "Allow sessions to escalate to a more capable model mid-session:\n- Detect when session is stuck or quality is low\n- Escalate from Haiku → Sonnet → Opus\n- Track escalation costs separately",
            "priority": 4, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature", "Daemon"), "cycleId": None,
        },
        {
            "title": "Session profile stats tracking",
            "description": "Track per-profile performance metrics:\n- Success rate by profile\n- Avg cost, duration, quality\n- Auto-tune profile parameters based on outcomes",
            "priority": 4, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature", "Daemon"), "cycleId": None,
        },
        {
            "title": "Review simulation: personas + simulator",
            "description": "Build review simulation system:\n- Define reviewer personas (harsh, constructive, domain-expert, etc.)\n- Implement review simulator using Claude\n- Generate mock reviews for paper drafts\n- Score reviews for actionability\n\nRef: docs/roadmaps/review-simulation.md",
            "priority": 3, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature", "Research"), "cycleId": None,
        },
        {
            "title": "Review simulation: prediction + API",
            "description": "Add prediction and API layer to review simulation:\n- Predict acceptance probability from reviews\n- Expose review results via API\n- Track prediction accuracy over time",
            "priority": 4, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature"), "cycleId": None,
        },
        {
            "title": "Meta-learning: effectiveness analysis",
            "description": "Analyze session effectiveness patterns:\n- Which strategies work best for which project phases?\n- What model/agent combinations produce highest quality?\n- Identify diminishing returns patterns\n\nRef: docs/roadmaps/meta-learning.md",
            "priority": 4, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Research", "Daemon"), "cycleId": None,
        },
        {
            "title": "Meta-learning: planner feedback loop",
            "description": "Close the loop between meta-learning insights and planner:\n- Feed effectiveness analysis back into strategy weights\n- Auto-adjust session parameters based on patterns\n- A/B test planning strategies",
            "priority": 4, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature", "Daemon"), "cycleId": None,
        },
        {
            "title": "Closed-loop experiments: core loop",
            "description": "Build closed-loop experiment runner:\n- Hypothesis → experiment → analysis → conclusion\n- Automatic experiment design from research questions\n- Results feed back into knowledge graph\n\nRef: docs/roadmaps/closed-loop-experiments.md",
            "priority": 4, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature", "Experiment"), "cycleId": None,
        },
        {
            "title": "Cross-project intelligence sharing",
            "description": "Share insights across research projects:\n- Common methodology patterns\n- Shared literature findings\n- Cross-project knowledge graph queries\n\nRef: docs/roadmaps/cross-project-intelligence.md",
            "priority": 4, "projectId": project_ids["platform-intelligence"],
            "labelIds": L("Feature", "Research"), "cycleId": None,
        },

        # ---- Backlog: Dashboard ----

        {
            "title": "Wire dashboard to live API (replace mock data)",
            "description": "Replace all mock/placeholder data in site-next with live API calls:\n- Projects list from /api/projects\n- Sessions from /api/sessions\n- Budget from /api/budget\n- Activity from /api/activity\n- Use TanStack Query for data fetching",
            "priority": 3, "projectId": project_ids["dashboard"],
            "labelIds": L("Feature"), "cycleId": None,
        },
        {
            "title": "Auth: GitHub OAuth with Auth.js",
            "description": "Add authentication to the dashboard:\n- Set up Auth.js with GitHub provider\n- Protect all routes\n- Allow only authorized GitHub accounts\n- Store sessions in PostgreSQL",
            "priority": 3, "projectId": project_ids["dashboard"],
            "labelIds": L("Feature", "Security"), "cycleId": None,
        },
        {
            "title": "Real-time WebSocket event streaming",
            "description": "Connect dashboard to orchestrator WebSocket:\n- Subscribe to session events\n- Live budget updates\n- Real-time activity feed\n- Session progress indicators",
            "priority": 4, "projectId": project_ids["dashboard"],
            "labelIds": L("Feature"), "cycleId": None,
        },
    ]

    created = 0
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
            print(f"  {ident}: {issue['title'][:60]}")
            created += 1
        except Exception as e:
            print(f"  FAILED: {issue['title'][:50]}: {e}")

    print(f"\n  Created {created}/{len(issues)} issues")


# ============================================================
# Main
# ============================================================

def main():
    print("DeepWork Linear Workspace Setup")
    print("=" * 40)

    # Step 1: Archive EV
    archive_ev()

    # Step 2: Create projects
    project_ids = create_projects()

    # Step 3: Create cycles
    cycle_ids = create_cycles()

    # Step 4: Create labels
    label_ids = create_labels()

    # Step 5: Create issues
    create_issues(project_ids, cycle_ids, label_ids)

    print("\n" + "=" * 40)
    print("DONE!")
    print(f"\nDW Team ID: {DW_TEAM_ID}")
    print("Add to VPS .env:")
    print(f"  LINEAR_API_KEY={API_KEY}")
    print(f"  LINEAR_TEAM_ID={DW_TEAM_ID}")


if __name__ == "__main__":
    main()
