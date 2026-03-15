# Platform Engineering

## Overview
Ongoing maintenance and improvement of the Deepwork research platform. This is not a research project — it is the infrastructure that enables all research projects.

## Scope
- Daemon reliability and performance
- API endpoints and data pipeline
- Agent framework (OpenClaw) improvements
- Eval pipeline stability
- Build and deployment tooling
- Monitoring and observability

## How Work Gets Here
1. Any OpenClaw agent files a backlog ticket via `POST /api/backlog`
2. Dev (Platform Engineer agent) reviews the backlog daily
3. Dev dispatches an `engineer` session to the daemon
4. The session reads the ticket, makes targeted changes, runs typecheck, commits, creates PR
5. Vera reviews the PR
6. Human merges

## Principles
- Small, focused changes — one ticket per session
- Always run `npm run build` before committing
- Never break existing functionality
- Prefer fixing bugs over adding features
- Conservative approach — when in doubt, don't change it
