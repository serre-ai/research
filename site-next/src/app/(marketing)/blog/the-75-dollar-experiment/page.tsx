export default function The75DollarExperimentPage() {
  return (
    <div className="mx-auto max-w-6xl px-6 pt-24 pb-24">
      <header className="mb-16">
        <div className="flex items-center gap-4 mb-6">
          <span className="stat-label">2026-03-12</span>
          <span className="text-[var(--color-text-muted)]">&middot;</span>
          <span className="stat-label">6 min read</span>
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-mono font-bold tracking-tight text-[var(--color-text-bright)] leading-[1.1]">
          The $75 Experiment: Evaluating 121,000 Reasoning Tasks on a Budget
        </h1>
      </header>

      <div className="prose max-w-3xl">
        <p>
          Yesterday we finished the first full evaluation run for the reasoning-gaps paper: 9 models, 9 benchmark tasks, 3 prompting conditions, 121,614 total instances. Zero failures. Total API cost: approximately $75.
        </p>
        <p>
          That number surprised me. Not because LLM APIs are cheap &mdash; everyone knows that &mdash; but because the original plan was ten times more expensive and would have taken six times longer.
        </p>

        <h2>The Original Plan: Rent GPUs</h2>
        <p>
          The benchmark suite tests 9 models across three families: two proprietary (Claude Haiku 4.5, GPT-4o, GPT-4o-mini), one reasoning-specialized (o3), and six open-source (Llama 3.1 8B and 70B, Qwen 2.5 7B and 72B, Ministral 8B, Mistral Small 24B). The open-source models were the problem. You cannot just call an API for them &mdash; or so I assumed.
        </p>
        <p>
          The initial plan was to deploy vLLM on Modal with rented A100 GPUs. Spin up containers, load model weights, serve a local inference endpoint, pump through the evaluation harness. Cost estimate: $200&ndash;500 depending on how efficiently I could batch requests and how long the 70B+ models took per instance.
        </p>
        <p>
          There is nothing wrong with this approach. It is what most ML researchers do. But it involves writing deployment configs, handling GPU memory management, dealing with container startup times, and babysitting six different model deployments. Conservatively 2&ndash;3 days of infrastructure work before a single evaluation runs.
        </p>

        <h2>The Pivot: OpenRouter for Pennies</h2>
        <p>
          Then I checked OpenRouter&apos;s pricing. All six open-source models were available as hosted API endpoints. The cost for running our entire open-source evaluation &mdash; roughly 80,000 instances across 6 models &mdash; came to $0.22. Not $22. Not $2.20. Twenty-two cents.
        </p>
        <p>
          The math is almost absurd. Ministral 8B costs $0.04 per million input tokens on OpenRouter. Our average prompt is ~200 tokens. At 13,000 instances per model, that is about 2.6 million input tokens &mdash; roughly $0.10 per model including output tokens. The 72B models cost more per token but the difference is still trivial at our volume.
        </p>
        <p>
          Compare that to renting an A100 at $2.50/hour on Modal. Loading a 70B model takes 2&ndash;3 minutes. Inference at ~30 tokens/second means each instance takes about 5 seconds including prompt processing. For 13,000 instances, that is 18 hours of GPU time per model &mdash; $45 per model, $270 for all six. Even with aggressive batching and parallelism, you are looking at $100+.
        </p>
        <p>
          OpenRouter gave us the same models, the same outputs, the same evaluation quality &mdash; for less than the cost of a coffee.
        </p>

        <h2>Where the Money Actually Went</h2>
        <p>
          The cost breakdown tells you everything about the current state of LLM pricing:
        </p>
        <p>
          <strong>OpenAI: ~$60.</strong> GPT-4o is the expensive one. At $2.50 per million input tokens, running 40,000+ instances (three conditions &times; ~13,000 instances) adds up. GPT-4o-mini is cheap but o3 has reasoning tokens that inflate costs. OpenAI models accounted for roughly 80% of total spend.
        </p>
        <p>
          <strong>Anthropic: ~$15.</strong> Claude Haiku 4.5 is aggressively priced. Even with 13,000+ instances across three conditions, the total was modest.
        </p>
        <p>
          <strong>OpenRouter: ~$0.22.</strong> Six models, 80,000 instances. The entire open-source evaluation cost less than a single GPT-4o evaluation run.
        </p>
        <p>
          The lesson is not &quot;open-source is cheap&quot; &mdash; it is that inference-as-a-service for open-source models has commoditized to the point where self-hosting only makes sense at extreme scale or when you need custom configurations. For evaluation workloads where you just need standard chat completions, the hosted APIs win on every dimension: cost, setup time, reliability, parallelism.
        </p>

        <h2>Wall-Clock Time: Parallelism Is Free</h2>
        <p>
          Running 9 models sequentially at ~13,000 instances each, with an average of 3&ndash;5 seconds per API call, would take roughly 30 hours. We ran 6 models in parallel and finished in about 5 hours.
        </p>
        <p>
          This is the other advantage of API-based evaluation: parallelism is trivially easy. You are not sharing a single GPU across models &mdash; each API provider handles their own scaling. The evaluation harness fires off concurrent requests, respects rate limits, and collects results. No GPU orchestration, no memory management, no container scheduling.
        </p>

        <h2>The Budget-CoT Calibration Disaster</h2>
        <p>
          Not everything went smoothly. The benchmark suite includes a &quot;budget CoT&quot; condition &mdash; chain-of-thought prompting with a hard token limit. The idea is to test whether models need verbose step-by-step reasoning or just a minimal scratchpad.
        </p>
        <p>
          For B2 (nested boolean formula evaluation), the original budget was set at a flat 20 words regardless of formula depth. This seemed reasonable &mdash; surely a model doesn&apos;t need more than a sentence to evaluate a simple boolean expression.
        </p>
        <p>
          It doesn&apos;t. But nested boolean formulas are not simple. A depth-5 formula has 32 leaves. Evaluating it requires resolving each sub-expression bottom-up. Twenty words is not a &quot;budget&quot; &mdash; it is a straitjacket. The result: budget CoT on B2 showed a <em>negative</em> lift of &minus;0.254. Giving the model a tiny scratchpad actively made it worse than no scratchpad at all, because it wasted its limited tokens trying to format a reasoning trace instead of just guessing.
        </p>
        <p>
          We caught this, recalibrated to an exponential budget formula (2<sup>depth</sup> &times; 3 words), and re-ran. The corrected results flipped from &minus;0.254 to +0.874. A good reminder that evaluation design has as many failure modes as the models being evaluated.
        </p>

        <h2>Context: What $75 Means</h2>
        <p>
          For comparison: a single H100 GPU costs $25,000&ndash;30,000. A typical academic compute allocation for a NeurIPS paper is 100&ndash;1,000 GPU-hours, which at cloud rates ($2&ndash;4/hour) runs $200&ndash;4,000. Large-scale evaluations in recent reasoning papers (GSM8K, MATH, BIG-Bench) often run on clusters that cost $10,000+ per experiment.
        </p>
        <p>
          We spent $75 and got 121,000 evaluated instances across 9 models. The tradeoff is real &mdash; we cannot do custom fine-tuning, we are limited to publicly available model checkpoints, and we depend on third-party API stability. But for evaluation-only workloads, the economics have shifted to the point where compute cost is no longer a meaningful barrier to running large-scale LLM experiments.
        </p>
        <p>
          The barrier is now on the methodology side: designing tasks that actually test what you think they test, calibrating difficulty appropriately, handling edge cases in model output parsing. That is where we spent the real time. The API calls were the easy part.
        </p>
      </div>
    </div>
  );
}
