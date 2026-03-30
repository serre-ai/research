# Design Inspiration: AI & Research Lab Websites

*Last updated: 2026-03-29*

Reference collection for Forge's web design direction. Our TUI aesthetic (monospace, keyboard-navigable, dark) is unique in the space — no one else ships a literal terminal UI as a website.

---

## Tier 1: Major AI Labs

### Anthropic — [anthropic.com](https://anthropic.com)
- **Aesthetic**: Warm minimalism, editorial sophistication
- **Color**: Cream/beige (#e8e6dc), deep charcoal text, rust-orange (#d97757) accents. Deliberately avoids cold white/dark mode.
- **Typography**: Serif headlines + sans-serif body. Academic gravitas while remaining approachable.
- **Interactions**: Staggered word animations, Lottie SVGs, 3D interactive globe.
- **Takeaway**: Personality through color alone. Reads like a high-end editorial publication, not a tech company. One of the strongest brand-through-palette examples.

### Google DeepMind — [deepmind.google](https://deepmind.google/)
- **Aesthetic**: Rich, cinematic, illustrated
- **Color**: Dynamic light/dark mode, Google four-color accents via CSS variables.
- **Layout**: Card-based mega-grid. Custom artwork per project (AlphaFold, Genie). Video-heavy with fallback posters.
- **Takeaway**: Unmatched density of custom illustration and video. Feels like a science museum. Every project gets bespoke visual treatment.

### Mistral AI — [mistral.ai](https://mistral.ai)
- **Aesthetic**: Dark-mode enterprise minimalism with signature gradient
- **Color**: Black (#1E1E1E) with orange/amber gradient (#FFD800 → #FF8205 → #E10500).
- **Typography**: Clean sans-serif, 64-96px section dividers.
- **Takeaway**: The orange gradient on black is immediately recognizable. Geometric logo blocks echoed throughout as section dividers — cohesive visual language.

### Cohere Labs — [cohere.com/research](https://cohere.com/research)
- **Aesthetic**: Dark academic-meets-tech
- **Typography**: Variable font with custom "cuts" axis. Responsive sizing via `clamp()`.
- **Interactions**: Staggered fade-in, animated character reveals, smooth accordion rotations.
- **Takeaway**: Variable font with custom axes is technically sophisticated. Community-first messaging ("4500+ Open Science collaborators").

### Stability AI — [stability.ai](https://stability.ai)
- **Aesthetic**: Dark, cinematic, enterprise-grade
- **Layout**: Asymmetric CSS grid (8-col mobile, 24-col desktop), 4-6vw padding.
- **Interactions**: Video backgrounds on hover/scroll, touch carousels, auto-rotating quotes.
- **Takeaway**: Asymmetric grid gives magazine-like editorial feel. Video-heavy but performance-conscious.

---

## Tier 2: Distinctive AI Startups

### Sakana AI — [sakana.ai](https://sakana.ai)
- **Aesthetic**: Ultra-minimal, content-focused
- **Color**: Dark (#1e1e1e), white text, bright blue links (#68f).
- **Typography**: Poppins light (200), monospace for code (Monaco/Menlo). Centered 850px column.
- **Takeaway**: Deliberately stripped-down, almost brutalist. Light-weight Poppins on dark is elegant. Strong counterpoint to flashy sites.

### Nous Research — [nousresearch.com](https://nousresearch.com)
- **Aesthetic**: Developer-brutalist, technical
- **Color**: Blue accent (#0171A9) on neutral backgrounds.
- **Typography**: Geist Mono for ALL headings. Bold 700, tight letter-spacing (-0.05em).
- **Takeaway**: All-monospace headings is rare and bold. "OUTPUTS" and "NODES" instead of generic nav. Every choice reinforces open-source hacker credibility. **Closest to our aesthetic.**

### Twelve Labs — [twelvelabs.io](https://twelvelabs.io)
- **Design by Pentagram**: [case study](https://www.pentagram.com/work/twelvelabs)
- **Aesthetic**: Spatial, dimensional, purpose-led
- **Visual language**: Thread-based diagrams, lozenge-shaped elements, Muybridge horse animation.
- **Takeaway**: Concept-driven design — "video is a volume, not a timeline" drives every visual decision. One of the few AI companies with genuine conceptual design thinking.

### Runway — [runwayml.com](https://runwayml.com)
- **Aesthetic**: Cinematic, dark, immersive
- **Color**: Deep blacks (#0C0C0C), semi-transparent white overlays.
- **Typography**: Three font families — "ABCNormal" (sans), "JHA Times Now" (serif display), system monospace.
- **Takeaway**: Most cinematic AI site. Full-screen video IS the design. Art-house film credits aesthetic. No traditional marketing copy, only stunning AI-generated art.

### Isomorphic Labs — [isomorphiclabs.com](https://isomorphiclabs.com)
- **Aesthetic**: Scientific luxury minimalism
- **Color**: Pure white, deep carbon black, accent blue (#4d65ff).
- **Typography**: Multi-tiered type system (display through XS). Anti-aliased rendering.
- **Interactions**: GSAP staggered reveals, progressive image scaling on scroll, 3D molecular viewer, character-level text stagger, progressive blur (2px to 32px).
- **Takeaway**: Most technically sophisticated animation system of any research site. Scientific precision embodied in design. White-space-heavy with merged borders.

### Perplexity — [perplexity.ai](https://perplexity.ai)
- **Aesthetic**: Swiss minimalism with warmth — "Scandinavian subway system"
- **Design philosophy**: "Clean and considered but invisible" — brand is a vessel for facts, not personality.
- **Built with**: Framer for all marketing pages. Ships pages in hours.
- **Takeaway**: Intentionally anti-flashy. "Invisible brand" concept — design recedes so content dominates. Vintage ad campaign posters contrast beautifully with clean product UI.

---

## Tier 3: Academic & Non-Profit Research

### Mila (Quebec AI Institute) — [mila.quebec/en](https://mila.quebec/en)
- Colorful geometric SVG shapes floating around hero images. Playfulness + institutional gravitas. 140+ affiliated professors browseable.

### Allen Institute for AI (Ai2) — [allenai.org](https://allenai.org)
- Container-query responsive design (cutting-edge CSS). Abstract generative illustrations feel AI-native. Openness as design value.

### Arc Institute — [arcinstitute.org](https://arcinstitute.org)
- Design almost disappears. Lab attributions + temporal organization. Pure vessel for research output. **Best "let the work speak" model.**

### HHMI Beautiful Biology — [hhmi.org/beautifulbiology](https://www.hhmi.org/beautifulbiology)
- 425+ microscopy images from 140+ scientists. Three viewing modes (Spectacle, Scroll, Visual Map). 2025 Best Science Website. The imagery IS the design.

### Campbell-Staton Group — [campbellstaton.com](https://www.campbellstaton.com)
- Afro-futurist storytelling meets academic research. Comic book / Black Panther / Spider-Verse inspiration. Custom color-block animal illustrations. Proof research sites don't have to look institutional.

---

## Tier 4: Design-Influential (Non-Research)

### Linear — [linear.app](https://linear.app)
- THE defining dark SaaS aesthetic of 2024-2026. Dark mode, Inter font, gradient purple, pixel-precise animations. Stratified text colors (primary/secondary/tertiary/quaternary). Grid-dot CSS keyframe animations. Copied by hundreds.

### Replicate — [replicate.com](https://replicate.com)
- Developer-friendly clarity. Code-first hero (Node/Python/HTTP tabs), grid model cards, contributor avatars. Balances developer docs aesthetic with AI-generated visual excitement.

---

## Design Patterns Across the Best Sites

**What they share:**
- Custom or variable fonts (not just Inter/system defaults)
- Intentional whitespace (64-96px section gaps)
- Content-first hierarchy — the work/research is the visual centerpiece
- One strong signature element (Anthropic's warm palette, Mistral's gradient, Runway's video)
- Scroll-triggered animations that feel purposeful, not decorative

**Two dominant archetypes:**

| | Dark / Cinematic | Light / Editorial |
|---|---|---|
| Examples | Mistral, Runway, Stability, Cohere, Linear | Anthropic, Isomorphic, Arc Institute, Perplexity |
| Backgrounds | Black/charcoal (#0C0C0C to #1E1E1E) | White/cream (#FFFFFF to #e8e6dc) |
| Accents | Gradients, neon, saturated color | Muted tones, serif type, whitespace |
| Feel | Technical, cinematic, confident | Editorial, academic, warm |

---

## Forge Positioning

Our TUI aesthetic is genuinely unique — no one else ships a literal terminal UI as a website. Closest precedents:

1. **Nous Research** — monospace-everything, hacker credibility
2. **Sakana AI** — minimal dark, content-first, light font weight
3. **Mistral** — black + signature accent, geometric language
4. **Linear** — dark mode precision (our dashboard already channels this)

**Our differentiator**: Not another dark-mode SaaS site. An actual keyboard-navigable terminal interface where the research is the content. The TUI IS the brand — it signals "we build autonomous research agents" more than any illustration or animation could.

**Design principles for Forge:**
- Monospace everywhere (IBM Plex Mono)
- Keyboard-first navigation (Tab, arrows, Enter)
- Information density over whitespace
- Status indicators and live data as visual interest
- No decorative elements — every pixel is functional
- Dark only, high contrast
- The interface communicates what we build
