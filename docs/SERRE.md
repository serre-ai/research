# Serre AI — Research Group Identity

## The Name

**Jean-Pierre Serre** (b. 1926). Youngest-ever Fields Medalist at 27. Abel Prize laureate. Fundamental contributions to algebraic geometry, algebraic topology, and number theory. Still active at 99. Known for rigor, breadth across fields, and clarity in exposition.

The name signals:
- **Formal rigor** — we prove things, we don't just benchmark
- **Cross-domain thinking** — complexity theory applied to LLM reasoning, verification across domains
- **Mathematical lineage** — positioning within the tradition of foundational research
- **Institutional weight** — "a paper from Serre AI" carries authority

## Identity

**Serre AI** is an independent research lab focused on the formal foundations of AI reasoning. We prove theorems about what language models can and cannot do. Our work spans computational complexity, verification theory, and empirical evaluation at scale.

We built our own autonomous research infrastructure — an orchestrator that runs Claude Code agents to survey literature, design experiments, write papers, and verify claims. This is how the lab operates, not what the lab is. The point is the research.

### Byline

```
Oddur Sigurdsson
Serre AI
oddur@serre.ai
```

In citations: *Sigurdsson, O. (Serre AI, 2026)*

### Domain

- **serre.ai** — institutional homepage (papers, blog, about)
- **forge.serre.ai** — research operations dashboard (authenticated, TUI)

## Structure

```
Serre AI                          ← the institution
├── Research                      ← papers, experiments, theory
│   ├── reasoning-gaps            NeurIPS 2026
│   ├── verification-complexity   ICLR 2027
│   ├── self-improvement-limits   ICLR 2027
│   └── agent-failure-taxonomy    ACL 2027
├── Forge                         ← autonomous research platform
│   ├── orchestrator              agent scheduling, quality gates
│   ├── daemon                    autonomous session management
│   └── dashboard                 TUI operations interface
└── Open Source                   ← public artifacts
    ├── benchmarks
    └── datasets
```

**Serre AI** is the research group. It publishes papers, maintains a research portfolio, and is the byline on everything.

**Forge** is the autonomous research platform (formerly "Deepwork"). It's a project of Serre AI — the tooling that powers the lab. Like how DeepMind builds AlphaFold, Serre AI builds Forge.

## Visual Identity

- **Typography**: IBM Plex Mono (monospace everywhere)
- **Palette**: Dark, minimal. Terminal-inspired but not a TUI on the public site
- **Logo**: The name in monospace IS the logo: `SERRE AI`
- **No icons, no illustrations** — authority through content, not decoration

### Public Site (serre.ai)

Clean, authoritative research portfolio. NOT a TUI. Think Anthropic's research page or Mila's. Monospace typography, dark theme, clean whitespace. Paper cards with abstracts, simple nav. The rigor is in the content, not the chrome.

### Operations Dashboard (forge.serre.ai)

Full TUI terminal interface. Authenticated. Real-time session monitoring, budget tracking, project management. This is the internal tool, not the public face.

## Rename Plan

### What changes

| Before | After |
|--------|-------|
| Deepwork | Serre AI (institution), Forge (platform) |
| deepwork (npm packages) | @serre/orchestrator, @serre/forge |
| research.oddurs.com | serre.ai (public), forge.serre.ai (dashboard) |
| darkreach.ai | Retired |
| site-next/ | forge/ (TUI dashboard) |
| New: site/ | Institutional website |
| deepwork-daemon.service | forge-daemon.service |
| deepwork-site.service | forge-site.service |

### What stays (for now)

- VPS user `deepwork` and paths `/opt/deepwork` — rename later to avoid breaking running services
- Database name `deepwork` — rename later
- GitHub repo `oddurs/deepwork` — rename on GitHub (old URLs auto-redirect)

### Timeline

Phase 1: Domain + DNS + institutional site scaffold
Phase 2: Repo rename + package names + documentation
Phase 3: VPS infrastructure rename (services, paths, user)
Phase 4: Database rename (requires migration + downtime)

## Previous Identity

- **Darkreach AI** (darkreach.ai) — placeholder domain, retired
- **Deepwork** — platform name, replaced by "Forge"
- **research.oddurs.com** — temporary domain, redirects to serre.ai
