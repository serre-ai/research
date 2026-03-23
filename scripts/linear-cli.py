#!/usr/bin/env python3
"""Linear CLI — wraps the Linear GraphQL API for the strategist agent.

Usage:
    python scripts/linear-cli.py list-issues [--project NAME] [--state STATE] [--label NAME]
    python scripts/linear-cli.py show-issue IDENTIFIER
    python scripts/linear-cli.py create-issue --title T --description D --project NAME [--labels L1,L2] [--priority P]
    python scripts/linear-cli.py update-issue IDENTIFIER [--title T] [--description D] [--priority P] [--add-labels L1,L2]
    python scripts/linear-cli.py add-comment IDENTIFIER --body BODY
    python scripts/linear-cli.py set-blocked-by ISSUE BLOCKER
    python scripts/linear-cli.py create-sub-issue PARENT --title T [--description D] [--labels L1,L2] [--priority P]
"""

import argparse
import json
import os
import sys
import urllib.request

# ── Constants ────────────────────────────────────────────────────────────────

DW_TEAM_ID = "77e7bcae-30d7-4257-b043-6f0b004abc65"
EV_TEAM_ID = "8513b969-e338-4196-97f9-1a15bcaf9962"  # DO NOT TOUCH

DEFAULT_STATE_ID = "834253df-cd32-4f85-bae7-55054f473c4b"  # Todo

PROJECT_IDS = {
    "reasoning-gaps": "d709e076-ec45-4cc0-b8f7-a6e325399e0c",
    "verification-complexity": "06169b0c-7275-4674-80d4-c63eccfda24a",
    "self-improvement-limits": "54ab21e9-a38b-43a8-8528-05fa5c197f1d",
    "platform-infra": "a10d081e-bfbd-4c54-abd3-39b956d3c657",
}

LABEL_IDS = {
    "Paper": "23944908-2c49-46f8-b06e-99cf71c450c1",
    "Research": "43acfa1e-8aa5-45f1-8dca-f84e107bbabd",
    "Experiment": "2478e058-1cac-44f1-b0f3-559f4237bbc9",
    "Submission": "edbdf28b-c098-487c-bced-ae801553b71f",
    "Infrastructure": "23c3bd19-9ea8-4847-93ae-393820a056a6",
    "Feature": "bbe153b8-a16b-4394-8c3f-898fced08b87",
    "Bug": "1f417acd-5f38-49dc-ba5f-f417338e3b87",
    "Improvement": "ad444d04-d5a5-4bd4-ab81-5b35b2705b21",
    "Daemon": "a7557f2e-2373-469d-955e-1749165273fb",
}

# Map state filter names to Linear workflow state category names
STATE_FILTERS = {
    "todo": "unstarted",
    "in-progress": "started",
    "done": "completed",
    "all": None,
}

# ── API helpers ──────────────────────────────────────────────────────────────

API_KEY = os.environ.get("LINEAR_API_KEY", "")
_api_call_count = 0
_API_CALL_LIMIT = 20


def gql(query, variables=None):
    """Execute a GraphQL query against the Linear API."""
    global _api_call_count
    _api_call_count += 1
    if _api_call_count > _API_CALL_LIMIT:
        print(f"ERROR: API call limit ({_API_CALL_LIMIT}) exceeded. Aborting.", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": API_KEY},
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    if "errors" in resp:
        print(f"GraphQL errors: {json.dumps(resp['errors'], indent=2)}", file=sys.stderr)
        sys.exit(1)
    return resp


def resolve_issue_id(identifier):
    """Resolve a Linear issue identifier (e.g. DW-42) to its internal UUID."""
    resp = gql(
        """
        query($filter: IssueFilter) {
            issues(filter: $filter, first: 1) {
                nodes { id identifier }
            }
        }
        """,
        {
            "filter": {
                "team": {"id": {"eq": DW_TEAM_ID}},
                "number": {"eq": int(identifier.split("-")[-1])},
            }
        },
    )
    nodes = resp["data"]["issues"]["nodes"]
    if not nodes:
        print(f"Issue {identifier} not found in DW team.", file=sys.stderr)
        sys.exit(1)
    return nodes[0]["id"]


def resolve_label_ids(label_names):
    """Resolve a list of label names to their UUIDs."""
    ids = []
    for name in label_names:
        name_stripped = name.strip()
        if name_stripped in LABEL_IDS:
            ids.append(LABEL_IDS[name_stripped])
        else:
            # Try case-insensitive match
            for k, v in LABEL_IDS.items():
                if k.lower() == name_stripped.lower():
                    ids.append(v)
                    break
            else:
                print(f"WARNING: Unknown label '{name_stripped}', skipping.", file=sys.stderr)
    return ids


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_list_issues(args):
    state_name = args.state or "todo"
    state_category = STATE_FILTERS.get(state_name)

    issue_filter = {"team": {"id": {"eq": DW_TEAM_ID}}}

    if state_category is not None:
        issue_filter["state"] = {"type": {"eq": state_category}}

    if args.project:
        project_id = PROJECT_IDS.get(args.project)
        if not project_id:
            print(f"Unknown project: {args.project}. Known: {', '.join(PROJECT_IDS.keys())}", file=sys.stderr)
            sys.exit(1)
        issue_filter["project"] = {"id": {"eq": project_id}}

    if args.label:
        label_ids = resolve_label_ids([args.label])
        if label_ids:
            issue_filter["labels"] = {"id": {"in": label_ids}}

    resp = gql(
        """
        query($filter: IssueFilter) {
            issues(filter: $filter, first: 50, orderBy: updatedAt) {
                nodes {
                    identifier
                    priority
                    state { name }
                    title
                }
            }
        }
        """,
        {"filter": issue_filter},
    )

    priority_labels = {0: "None", 1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}
    for issue in resp["data"]["issues"]["nodes"]:
        pri = priority_labels.get(issue["priority"], str(issue["priority"]))
        state = issue["state"]["name"]
        print(f"{issue['identifier']}\t{pri}\t{state}\t{issue['title']}")


def cmd_show_issue(args):
    identifier = args.identifier.upper()
    resp = gql(
        """
        query($filter: IssueFilter) {
            issues(filter: $filter, first: 1) {
                nodes {
                    identifier
                    title
                    description
                    priority
                    state { name }
                    labels { nodes { name } }
                    project { name }
                    parent { identifier title }
                    children { nodes { identifier title state { name } } }
                    relations { nodes { type relatedIssue { identifier title } } }
                    comments(first: 5) { nodes { body createdAt user { name } } }
                }
            }
        }
        """,
        {
            "filter": {
                "team": {"id": {"eq": DW_TEAM_ID}},
                "number": {"eq": int(identifier.split("-")[-1])},
            }
        },
    )

    nodes = resp["data"]["issues"]["nodes"]
    if not nodes:
        print(f"Issue {identifier} not found in DW team.", file=sys.stderr)
        sys.exit(1)

    issue = nodes[0]
    priority_labels = {0: "None", 1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}

    print(f"# {issue['identifier']}: {issue['title']}")
    print()
    print(f"**State:** {issue['state']['name']}")
    print(f"**Priority:** {priority_labels.get(issue['priority'], str(issue['priority']))}")

    labels = [l["name"] for l in issue.get("labels", {}).get("nodes", [])]
    if labels:
        print(f"**Labels:** {', '.join(labels)}")

    if issue.get("project"):
        print(f"**Project:** {issue['project']['name']}")

    if issue.get("parent"):
        print(f"**Parent:** {issue['parent']['identifier']} — {issue['parent']['title']}")

    print()

    if issue.get("description"):
        print("## Description")
        print(issue["description"])
        print()

    children = issue.get("children", {}).get("nodes", [])
    if children:
        print("## Sub-issues")
        for child in children:
            print(f"- {child['identifier']}: {child['title']} [{child['state']['name']}]")
        print()

    relations = issue.get("relations", {}).get("nodes", [])
    if relations:
        print("## Relations")
        for rel in relations:
            ri = rel["relatedIssue"]
            print(f"- {rel['type']}: {ri['identifier']} — {ri['title']}")
        print()

    comments = issue.get("comments", {}).get("nodes", [])
    if comments:
        print("## Recent Comments")
        for comment in comments:
            user = comment.get("user", {}).get("name", "Unknown")
            print(f"**{user}** ({comment['createdAt'][:10]}):")
            print(comment["body"])
            print()


def cmd_create_issue(args):
    project_id = PROJECT_IDS.get(args.project)
    if not project_id:
        print(f"Unknown project: {args.project}. Known: {', '.join(PROJECT_IDS.keys())}", file=sys.stderr)
        sys.exit(1)

    input_data = {
        "teamId": DW_TEAM_ID,
        "title": args.title,
        "description": args.description,
        "projectId": project_id,
        "stateId": DEFAULT_STATE_ID,
    }

    if args.priority:
        input_data["priority"] = int(args.priority)

    if args.labels:
        label_ids = resolve_label_ids(args.labels.split(","))
        if label_ids:
            input_data["labelIds"] = label_ids

    resp = gql(
        """
        mutation($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue { identifier title }
            }
        }
        """,
        {"input": input_data},
    )

    result = resp["data"]["issueCreate"]
    if result["success"]:
        print(f"Created {result['issue']['identifier']}: {result['issue']['title']}")
    else:
        print("Failed to create issue.", file=sys.stderr)
        sys.exit(1)


def cmd_update_issue(args):
    identifier = args.identifier.upper()
    issue_id = resolve_issue_id(identifier)

    input_data = {}
    if args.title:
        input_data["title"] = args.title
    if args.description:
        input_data["description"] = args.description
    if args.priority:
        input_data["priority"] = int(args.priority)
    if args.add_labels:
        label_ids = resolve_label_ids(args.add_labels.split(","))
        if label_ids:
            # Fetch current labels first to append
            current = gql(
                """
                query($id: String!) {
                    issue(id: $id) { labels { nodes { id } } }
                }
                """,
                {"id": issue_id},
            )
            current_ids = [l["id"] for l in current["data"]["issue"]["labels"]["nodes"]]
            input_data["labelIds"] = list(set(current_ids + label_ids))

    if not input_data:
        print("No updates specified.", file=sys.stderr)
        sys.exit(1)

    resp = gql(
        """
        mutation($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
            }
        }
        """,
        {"id": issue_id, "input": input_data},
    )

    if resp["data"]["issueUpdate"]["success"]:
        print(f"Updated {identifier}")
    else:
        print(f"Failed to update {identifier}.", file=sys.stderr)
        sys.exit(1)


def cmd_add_comment(args):
    identifier = args.identifier.upper()
    issue_id = resolve_issue_id(identifier)

    resp = gql(
        """
        mutation($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
            }
        }
        """,
        {"input": {"issueId": issue_id, "body": args.body}},
    )

    if resp["data"]["commentCreate"]["success"]:
        print(f"Comment added to {identifier}")
    else:
        print(f"Failed to add comment to {identifier}.", file=sys.stderr)
        sys.exit(1)


def cmd_set_blocked_by(args):
    issue_identifier = args.issue.upper()
    blocker_identifier = args.blocker.upper()

    issue_id = resolve_issue_id(issue_identifier)
    blocker_id = resolve_issue_id(blocker_identifier)

    resp = gql(
        """
        mutation($input: IssueRelationCreateInput!) {
            issueRelationCreate(input: $input) {
                success
            }
        }
        """,
        {
            "input": {
                "issueId": blocker_id,
                "relatedIssueId": issue_id,
                "type": "blocks",
            }
        },
    )

    if resp["data"]["issueRelationCreate"]["success"]:
        print(f"Set {issue_identifier} blocked by {blocker_identifier}")
    else:
        print(f"Failed to set relation.", file=sys.stderr)
        sys.exit(1)


def cmd_create_sub_issue(args):
    parent_identifier = args.parent.upper()
    parent_id = resolve_issue_id(parent_identifier)

    input_data = {
        "teamId": DW_TEAM_ID,
        "title": args.title,
        "parentId": parent_id,
        "stateId": DEFAULT_STATE_ID,
    }

    if args.description:
        input_data["description"] = args.description
    if args.priority:
        input_data["priority"] = int(args.priority)
    if args.labels:
        label_ids = resolve_label_ids(args.labels.split(","))
        if label_ids:
            input_data["labelIds"] = label_ids

    resp = gql(
        """
        mutation($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue { identifier title }
            }
        }
        """,
        {"input": input_data},
    )

    result = resp["data"]["issueCreate"]
    if result["success"]:
        print(f"Created {result['issue']['identifier']} as sub-issue of {parent_identifier}")
    else:
        print("Failed to create sub-issue.", file=sys.stderr)
        sys.exit(1)


# ── CLI entrypoint ───────────────────────────────────────────────────────────


def main():
    if not API_KEY:
        print("ERROR: LINEAR_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Linear CLI for the DW team — strategist agent tool"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list-issues
    p_list = sub.add_parser("list-issues", help="List team issues with filters")
    p_list.add_argument("--project", help="Filter by project name")
    p_list.add_argument(
        "--state",
        choices=["todo", "in-progress", "done", "all"],
        default="todo",
        help="Filter by state (default: todo)",
    )
    p_list.add_argument("--label", help="Filter by label name")

    # show-issue
    p_show = sub.add_parser("show-issue", help="Show full issue details")
    p_show.add_argument("identifier", help="Issue identifier (e.g. DW-42)")

    # create-issue
    p_create = sub.add_parser("create-issue", help="Create a new issue")
    p_create.add_argument("--title", required=True, help="Issue title")
    p_create.add_argument("--description", required=True, help="Issue description")
    p_create.add_argument("--project", required=True, help="Project name")
    p_create.add_argument("--labels", help="Comma-separated label names")
    p_create.add_argument("--priority", type=int, choices=[1, 2, 3, 4], help="Priority (1=Urgent, 4=Low)")

    # update-issue
    p_update = sub.add_parser("update-issue", help="Update an issue")
    p_update.add_argument("identifier", help="Issue identifier (e.g. DW-42)")
    p_update.add_argument("--title", help="New title")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--priority", type=int, choices=[1, 2, 3, 4], help="New priority")
    p_update.add_argument("--add-labels", help="Comma-separated label names to add")

    # add-comment
    p_comment = sub.add_parser("add-comment", help="Add a comment to an issue")
    p_comment.add_argument("identifier", help="Issue identifier (e.g. DW-42)")
    p_comment.add_argument("--body", required=True, help="Comment body")

    # set-blocked-by
    p_blocked = sub.add_parser("set-blocked-by", help="Set issue blocked by another")
    p_blocked.add_argument("issue", help="Issue that is blocked")
    p_blocked.add_argument("blocker", help="Issue that blocks")

    # create-sub-issue
    p_sub = sub.add_parser("create-sub-issue", help="Create a sub-issue")
    p_sub.add_argument("parent", help="Parent issue identifier")
    p_sub.add_argument("--title", required=True, help="Sub-issue title")
    p_sub.add_argument("--description", help="Sub-issue description")
    p_sub.add_argument("--labels", help="Comma-separated label names")
    p_sub.add_argument("--priority", type=int, choices=[1, 2, 3, 4], help="Priority")

    args = parser.parse_args()

    dispatch = {
        "list-issues": cmd_list_issues,
        "show-issue": cmd_show_issue,
        "create-issue": cmd_create_issue,
        "update-issue": cmd_update_issue,
        "add-comment": cmd_add_comment,
        "set-blocked-by": cmd_set_blocked_by,
        "create-sub-issue": cmd_create_sub_issue,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
