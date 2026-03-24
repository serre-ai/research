const ASCII_ART = `
 ██████╗ ███████╗███████╗██████╗ ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
 ██╔══██╗██╔════╝██╔════╝██╔══██╗██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
 ██║  ██║█████╗  █████╗  ██████╔╝██║ █╗ ██║██║   ██║██████╔╝█████╔╝
 ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ ██║███╗██║██║   ██║██╔══██╗██╔═██╗
 ██████╔╝███████╗███████╗██║     ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
 ╚═════╝ ╚══════╝╚══════╝╚═╝      ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝`.trimStart();

export function TerminalHero() {
  return (
    <div className="py-16 md:py-24">
      {/* ASCII art — hidden on very small screens */}
      <div className="hidden sm:block mb-6">
        <pre className="ascii-art" aria-label="DEEPWORK">{ASCII_ART}</pre>
      </div>
      {/* Text fallback for mobile */}
      <h1 className="sm:hidden font-mono text-4xl font-bold text-text-bright">
        DEEPWORK
      </h1>

      <p className="mt-6 font-mono text-text-secondary">
        Autonomous AI research platform<span className="terminal-cursor">_</span>
      </p>
      <p className="mt-3 max-w-2xl font-mono text-xs text-text-muted leading-relaxed">
        An independent lab using Claude Code to autonomously investigate, write,
        and iterate on papers targeting top-tier venues. Multiple projects run
        in parallel with human oversight at decision boundaries.
      </p>
    </div>
  );
}
