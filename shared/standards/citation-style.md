# Citation Standards

## General Principles

- Every factual claim must be cited. If you write "Transformers struggle with compositional reasoning," cite the paper(s) that demonstrated this.
- Every comparison must be cited. If you mention a baseline or competing method, cite its source.
- Cite the original work, not a survey that mentions it. Go to the primary source.
- When a concept has been independently discovered by multiple groups, cite all of them.

## BibTeX Formatting

### Key Format
Use `AuthorYear` or `AuthorYearKeyword` for disambiguation:
- `Vaswani2017` — single key paper by this author in this year
- `Brown2020GPT3` — when the author has multiple papers in the same year
- `Wei2022ChainOfThought` — keyword helps identify the paper at a glance

### Entry Types

**Conference paper** (`@inproceedings`):
```bibtex
@inproceedings{Vaswani2017,
  title     = {Attention Is All You Need},
  author    = {Vaswani, Ashish and Shazeer, Noam and ...},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {30},
  year      = {2017},
  url       = {https://...},
}
```

**Journal article** (`@article`):
```bibtex
@article{Hochreiter1997,
  title   = {Long Short-Term Memory},
  author  = {Hochreiter, Sepp and Schmidhuber, J{\"u}rgen},
  journal = {Neural Computation},
  volume  = {9},
  number  = {8},
  pages   = {1735--1780},
  year    = {1997},
  doi     = {10.1162/neco.1997.9.8.1735},
}
```

**Arxiv preprint** (`@misc`):
```bibtex
@misc{Wei2022ChainOfThought,
  title         = {Chain-of-Thought Prompting Elicits Reasoning in Large Language Models},
  author        = {Wei, Jason and Wang, Xuezhi and ...},
  year          = {2022},
  eprint        = {2201.11903},
  archiveprefix = {arXiv},
  primaryclass  = {cs.CL},
  url           = {https://arxiv.org/abs/2201.11903},
}
```

**Book or book chapter** (`@incollection` or `@book`):
```bibtex
@incollection{Goodfellow2016,
  title     = {Deep Learning},
  author    = {Goodfellow, Ian and Bengio, Yoshua and Courville, Aaron},
  booktitle = {Deep Learning},
  chapter   = {10},
  publisher = {MIT Press},
  year      = {2016},
}
```

### Required Fields by Type

| Field | inproceedings | article | misc (arxiv) | incollection |
|-------|:---:|:---:|:---:|:---:|
| title | required | required | required | required |
| author | required | required | required | required |
| year | required | required | required | required |
| booktitle | required | - | - | required |
| journal | - | required | - | - |
| volume | recommended | required | - | - |
| pages | recommended | required | - | recommended |
| eprint | - | - | required | - |
| archiveprefix | - | - | required | - |
| url/doi | recommended | recommended | recommended | recommended |

### Formatting Rules
- Author names: `LastName, FirstName` format, separated by `and`
- Use full first names, not initials, when available
- Protect capitalization in titles with braces: `{GPT-3}`, `{BERT}`, `{Transformer}`
- Use en-dashes for page ranges: `1735--1780`
- Use LaTeX encoding for special characters: `{\"u}` for u-umlaut
- Include DOI for journal articles; include URL for conference papers
- End every field value with a comma (except the last before closing brace)

## Arxiv vs. Published Versions

**Always prefer the published venue version over arxiv.** If a paper appeared at NeurIPS and is also on arxiv, cite the NeurIPS proceedings version.

Exceptions where arxiv is acceptable:
- The paper has not been published at a venue yet
- The arxiv version contains substantial material not in the published version (and you're citing that material)
- The paper is a technical report not intended for venue publication

When switching from arxiv to published: update the BibTeX entry type, add venue information, and remove arxiv-specific fields. Keep both versions in a comment if useful for traceability.

## Self-Citation Policy

- Cite your own prior work when genuinely relevant, using the same standard as any other citation
- During anonymous review: use third-person references ("Author et al. (2024) showed...") even for your own work. Do not say "In our prior work" as this breaks anonymity.
- Do not pad the references with self-citations that aren't substantively relevant

## Minimum Coverage Requirements

A well-cited paper in ML typically has:
- **30+ references** for a full conference paper
- Coverage of all major related work streams (a reviewer should not be able to name a key missing reference)
- At least 3-5 references from the last 2 years (showing awareness of current work)
- At least 3-5 foundational references (showing awareness of the field's history)
- References from multiple research groups (not just one lab's work)

## When to Cite

| Situation | Citation needed? |
|-----------|:---:|
| Factual claim about model capabilities | Yes |
| Description of a method or algorithm | Yes (original paper) |
| Comparison to a baseline | Yes |
| Use of a dataset | Yes (dataset paper) |
| Use of a metric | Yes (if non-standard) |
| General knowledge ("neural networks are universal approximators") | Yes (original proof) |
| Your own novel contribution in this paper | No |
| Common mathematical notation or definitions | No |
| Widely known facts ("GPUs accelerate matrix multiplication") | No |

## In-Text Citation Style

Use `natbib` commands for consistent formatting:
- Parenthetical: `\citep{Vaswani2017}` produces (Vaswani et al., 2017)
- Textual: `\citet{Vaswani2017}` produces Vaswani et al. (2017)
- Multiple: `\citep{Brown2020GPT3,Wei2022ChainOfThought}` groups them
- With note: `\citep[see][Section 3]{Vaswani2017}`

Use textual citations when the authors are the subject of the sentence. Use parenthetical citations when the work supports a claim.

Good: "Vaswani et al. (2017) introduced the Transformer architecture."
Good: "The Transformer architecture has been widely adopted (Vaswani et al., 2017)."
Bad: "(Vaswani et al., 2017) introduced the Transformer architecture."
