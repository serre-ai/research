export default function IntroducingDeepworkPage() {
  return (
    <div className="mx-auto max-w-6xl px-6 pt-24 pb-24">
      <header className="mb-16">
        <div className="flex items-center gap-4 mb-6">
          <span className="stat-label">2026-03-10</span>
          <span className="text-[var(--color-text-muted)]">&middot;</span>
          <span className="stat-label">8 min read</span>
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-mono font-bold tracking-tight text-[var(--color-text-bright)] leading-[1.1]">
          Introducing Deepwork Research
        </h1>
      </header>

      <div className="prose max-w-3xl">
        <p>
          Deepwork Research is an autonomous AI research platform. It is a solo project by me, Oddur Sigurdsson, built around a single question: can AI agents, given the right tools and structure, conduct meaningful academic research?
        </p>
        <p>
          Not &quot;assist with&quot; research. Not autocomplete a paragraph or suggest a citation. Actually do it — read the literature, identify open questions, develop frameworks, design experiments, write papers, respond to their own weaknesses, and iterate until the work is good enough to submit to a top venue.
        </p>
        <p>
          I do not know the answer yet. This platform is the experiment that will produce one.
        </p>

        <h2>The Approach</h2>
        <p>
          The core idea is simple: treat research projects the way a well-run engineering team treats software. Each project gets a brief (goals, hypotheses, methodology, timeline), a status file that serves as the single source of truth, and a Claude Code agent that works on it autonomously.
        </p>
        <p>
          In practice, this means Claude Code agents run in isolated git worktrees, each on its own branch. An agent reads its project brief, checks the current status, then picks up where it left off — reviewing a paper, refining a formal definition, drafting a section, or designing an experiment. When it finishes a chunk of work, it commits, pushes, and updates its status file. At significant milestones, it opens a pull request to main.
        </p>
        <p>
          Above the agents sits a daemon scheduler written in TypeScript. It prioritizes projects based on deadlines and phase, enforces a monthly compute budget, handles session failures, and keeps everything moving. A CLI dashboard lets me monitor progress across all active projects in real time — what phase each project is in, how many commits have landed, whether anything is stuck.
        </p>
        <p>
          Everything is tracked in YAML status files and conventional git commits. There is no hidden state. If you read the git log and the status files, you know exactly what happened, what decisions were made, and why. This transparency is not incidental — it is a design requirement. If autonomous research is going to be credible, the process needs to be fully auditable.
        </p>
        <p>
          Decision-making is fully autonomous. The agents use extended thinking for critical choices (research direction, methodology, scope of theoretical claims) and log every decision with a rationale in the status file. No human approval step. I read the logs, review PRs, and intervene only if something is fundamentally off track. So far, I have not needed to.
        </p>

        <h2>Current Projects</h2>
        <p>
          Two projects are active right now.
        </p>
        <p>
          <strong>Reasoning Gaps</strong> (targeting NeurIPS 2026) is a formal characterization of where and why large language models fail at reasoning. The premise: LLM reasoning failures are not random. They cluster around specific problem structures — tasks requiring unbounded working memory, recursive variable binding, or certain compositions of operations that correspond to known boundaries in computational complexity theory (particularly TC<sup>0</sup> and NC<sup>1</sup>). The project aims to develop a formal framework connecting empirical reasoning failures to these complexity-theoretic properties, build a diagnostic benchmark suite that isolates specific failure types, and evaluate which gaps can be closed via prompting or scaffolding versus which require architectural changes. The agent is currently in the literature review phase, working through the transformer expressiveness and circuit complexity literature.
        </p>
        <p>
          <strong>Agent Failure Taxonomy</strong> (targeting ACL 2027) takes a different angle on a related problem. LLM-based autonomous agents — ReAct, AutoGPT, Claude Code, Voyager, and others — fail in systematic, recurring ways that are poorly documented. Individual failure reports exist scattered across papers, blog posts, and GitHub issues, but no comprehensive taxonomy connects them. This project aims to collect 100+ documented agent failures, categorize them into a rigorous hierarchical taxonomy using grounded theory methodology, and then validate the categories through controlled experiments across multiple agent frameworks. One of the hypotheses: most agent failures (more than 60%) stem from planning and state-tracking limitations, not knowledge gaps or tool-use errors. If that holds, it has direct implications for where architectural investment should go.
        </p>
        <p>
          The two projects are designed to connect. The reasoning gaps framework provides the theoretical foundation; the agent failure taxonomy maps how those abstract limitations manifest in the wild. A clean finding in one informs the other.
        </p>

        <h2>Why This Matters</h2>
        <p>
          There is an obvious meta-quality to this work: AI agents researching the limitations of AI agents. I want to be direct about that, because it is the most interesting part.
        </p>
        <p>
          If the agents produce research that holds up to peer review — papers with rigorous methodology, novel contributions, and sound reasoning — then that itself is a data point about what autonomous agents can do. Not a benchmark score, not a demo, but a months-long sustained effort producing work evaluated by the same standards as human researchers.
        </p>
        <p>
          If they fail, that is also valuable. Every place where the agent gets stuck, makes a poor judgment call, loses coherence over a long research arc, or produces work that does not meet the bar — those failure modes become data for the agent failure taxonomy project. The platform is designed so that its own failures are captured, categorized, and studied.
        </p>
        <p>
          Either outcome produces something worth publishing. That is not an accident. It is the reason I chose these specific research topics first.
        </p>
        <p>
          There is a broader point here about how AI research will be conducted going forward. Today, AI agents are used as tools within a human-led research process — they help with literature search, code generation, maybe drafting. But the gap between &quot;tool&quot; and &quot;researcher&quot; is narrowing. Understanding where exactly that gap exists, and how fast it is closing, seems like one of the more important questions in the field right now. Deepwork is one attempt to get concrete evidence rather than speculation.
        </p>

        <h2>What&apos;s Next</h2>
        <p>
          Beyond the two active projects, I maintain a scored research backlog — a list of potential projects ranked by estimated impact, feasibility, timeline fit, and resource requirements. As the current projects reach milestones, new ones will spin up. The platform can run multiple projects in parallel, limited mainly by the compute budget ($1,000/month for API calls and external services).
        </p>
        <p>
          This website will serve as the public-facing side of the work. Papers and preprints will be posted here as they reach maturity. Blog posts will cover methodology, findings, and the meta-level observations about running autonomous research. Everything that can be open will be open.
        </p>
        <p>
          I have no lab affiliation, no grant funding, no team. The goal is to build credibility the only way that actually works in research: through the quality of the output. If the papers are good, they will stand on their own regardless of who — or what — wrote them. If they are not good enough, I will know exactly why, because the entire process is logged.
        </p>
        <p>
          The first paper drafts should start appearing in the coming weeks. I will share them here as they develop.
        </p>
      </div>
    </div>
  );
}
