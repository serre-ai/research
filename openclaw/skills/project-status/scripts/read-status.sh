#!/usr/bin/env bash
# Read project status.yaml files
# Usage: read-status.sh {all|<project-name>}

set -euo pipefail

REPO_ROOT="${DEEPWORK_ROOT:-/home/deepwork/deepwork}"
PROJECTS_DIR="$REPO_ROOT/projects"

PROJECT="${1:?Usage: read-status.sh {all|<project-name>}}"

if [ "$PROJECT" = "all" ]; then
  for dir in "$PROJECTS_DIR"/*/; do
    name="$(basename "$dir")"
    status_file="$dir/status.yaml"
    if [ -f "$status_file" ]; then
      echo "=== $name ==="
      cat "$status_file"
      echo ""
    fi
  done
else
  status_file="$PROJECTS_DIR/$PROJECT/status.yaml"
  if [ -f "$status_file" ]; then
    cat "$status_file"
  else
    echo "Error: status.yaml not found for project '$PROJECT'" >&2
    exit 1
  fi
fi
