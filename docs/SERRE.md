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

### Typography

IBM Plex Mono everywhere. No secondary font on public materials. Weights:
- **600 (SemiBold)** — headings, lab name, paper titles
- **500 (Medium)** — navigation, labels, emphasis
- **400 (Regular)** — body text, descriptions, abstracts

### Color Palette

```
Background          #0a0a0a
Surface             #111111
Border              #1a1a1a

Text (body)         #b0b0b0
Text (bright)       #e5e5e5
Text (muted)        #555555

Status: published   #10b981  (green)
Status: active      #60a5fa  (blue)
Status: draft       #555555  (muted)

Accent              #60a5fa  (blue — links, active states)
Error/warn          #ef4444 / #f59e0b
```

### Logo

The name in monospace IS the logo. No symbol, no icon, no mark.

```
SERRE AI
```

Rendered in IBM Plex Mono SemiBold, tracking-widest, uppercase. Use on dark backgrounds only. Minimum clear space: 2em on all sides.

For contexts requiring a very compact mark (favicon, avatar): `S` in monospace on dark bg.

### Design Principles

1. **No icons** — use text labels, Unicode glyphs (●, ─), or nothing
2. **No illustrations** — the content is the visual
3. **No rounded corners** — square everything
4. **No shadows** — flat, no depth illusions
5. **No gradients** — solid colors only
6. **Horizontal rules** as section dividers (1px, `#1a1a1a`)
7. **Generous whitespace** — let the text breathe

### Public Site (serre.ai)

Clean, vertical document flow. Dark background, monospace text, paper listings with venue/status. Not a TUI — no borders, no panels, no keyboard nav. Think: a well-formatted research document rendered in a terminal. Deployed on Vercel.

### Operations Dashboard (forge.serre.ai)

Full TUI terminal interface. CSS borders, focusable panels, keyboard navigation, status bars. Authenticated. Real-time session monitoring, budget tracking, project management. Deployed on VPS.

## Paper & Conference Identity

### LaTeX Affiliation Block

```latex
\author{Oddur Sigurdsson}
\affiliation{Serre AI}
\email{oddur@serre.ai}
```

For multi-author papers (future):
```latex
\author{Oddur Sigurdsson\textsuperscript{1}, [Collaborator]\textsuperscript{2}}
\affiliation{\textsuperscript{1}Serre AI, \textsuperscript{2}[Institution]}
```

### Conference Poster/Badge

```
Oddur Sigurdsson
Serre AI
serre.ai
```

No logo graphic. Name + institution + URL in monospace. Dark badge background if custom badges are supported.

### Paper Repository Naming

Public code releases: `serre-ai/<project-slug>`
Example: `serre-ai/reasoning-gaps`, `serre-ai/verification-complexity`

HuggingFace: `serre-ai/reasongap-benchmark`
WandB: `serre-ai`

## Email Signature

```
Oddur Sigurdsson
Serre AI
oddur@serre.ai · serre.ai
```

No image, no social links, no title. Plain text only.

## Social & External Accounts

Claim when ready (not urgent):
- GitHub org: `serre-ai`
- HuggingFace org: `serre-ai`
- Twitter/X: `@serre_ai`
- Google Scholar: update affiliation to "Serre AI"
- Semantic Scholar: claim author profile
- ORCID: update affiliation

## Rename Plan

### What changes

| Before | After |
|--------|-------|
| Deepwork | Serre AI (institution), Forge (platform) |
| deepwork (npm packages) | @serre/orchestrator, @serre/forge |
| research.oddurs.com | serre.ai (public), forge.serre.ai (dashboard) |
| darkreach.ai | Retired |
| site-next/ | forge/ (TUI dashboard) — done |
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
