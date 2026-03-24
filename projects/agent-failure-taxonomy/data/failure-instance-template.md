# Failure Instance Template

Use this template to document each distinct agent failure instance collected from literature, GitHub issues, blog posts, or controlled experiments.

## Instance ID
`FI-[number]` (e.g., FI-001, FI-002)

## Source Information
- **Source type**: [Paper | GitHub Issue | Blog Post | Controlled Experiment | Documentation | User Report]
- **Source URL/Citation**: [Full citation or URL]
- **Date reported**: YYYY-MM-DD
- **Agent framework**: [ReAct | AutoGPT | Voyager | LangChain | CrewAI | SWE-agent | Custom | Other]
- **Base LLM**: [GPT-4 | GPT-3.5 | Claude | Gemini | Open-source model | Not specified]

## Task Context
- **Task type**: [Software engineering | Web navigation | Knowledge retrieval | Embodied/robotics | Data analysis | Code generation | Customer service | Other]
- **Task complexity**: [Simple | Moderate | Complex]
- **Task horizon**: [Single-turn | Multi-turn (<5) | Long-running (5-20 turns) | Extended (>20 turns)]
- **Task description**: [1-2 sentence description of what the agent was trying to accomplish]

## Failure Description
### Observable Behavior
[Describe what actually happened - what was observed externally]

### Expected Behavior
[What should have happened - the correct agent behavior]

### Failure Impact
- **Impact severity**: [Critical | High | Moderate | Low]
- **Recovery**: [Automatic | Manual intervention | Restart required | Not recoverable]
- **Consequences**: [Cost overrun | Security incident | Incorrect output | User frustration | System crash | Other]

## Root Cause Hypothesis
### Immediate Cause
[The proximate technical cause - e.g., malformed API call, parsing error, incorrect tool selection]

### Underlying Cause
[Deeper reason - e.g., insufficient state tracking, planning limitation, hallucination, prompt ambiguity]

### LLM-Level Limitation (if applicable)
[Connection to fundamental LLM capability - e.g., long-range dependency, causal reasoning, numerical reasoning, instruction following]

## Failure Category (preliminary)
[To be filled during open coding - may be revised]
- **Provisional category**: [Planning | Tool-use | State tracking | Error propagation | Grounding | Security | Self-correction | Resource management | Coordination | Other]
- **Sub-category** (if applicable):

## Architecture Factors
- **Agent architecture**: [ReAct (interleaved) | Plan-then-execute | Tree-of-thought | Reflection/Reflexion | Multi-agent | Other]
- **Architecture-specific factors**: [Features of the architecture that contributed to or amplified the failure]

## Reproducibility
- **Reproducible**: [Yes | No | Unknown | Partially]
- **Reproduction notes**: [Conditions required to reproduce, or why it's not reproducible]

## Mitigation Strategies
### Attempted (if any)
[What was tried to fix or prevent this failure, and whether it worked]

### Potential
[Hypothetical mitigation strategies that might work]

### Limitations
[Why some mitigation strategies won't work or are impractical]

## Related Failures
[List other failure instance IDs that are similar or related]

## Notes
[Any additional context, quotes from source, or observations]

## Coding Tags
[Tags added during iterative coding process]
- **Open codes**: [Initial descriptive codes]
- **Axial codes**: [Refined categorical codes]
- **Theoretical codes**: [Codes connecting to broader patterns or theory]
