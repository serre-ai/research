#!/usr/bin/env python3
"""Check a .tex file against the paper style specification.

Usage:
    python3 scripts/style-checker.py projects/reasoning-gaps/paper/main.tex
    python3 scripts/style-checker.py projects/reasoning-gaps/paper/main.tex --style shared/config/paper-style.yaml
    python3 scripts/style-checker.py projects/reasoning-gaps/paper/main.tex --verbose

Outputs JSON to stdout.  With --verbose, also prints a human-readable
summary to stderr.  Uses only Python stdlib (no external dependencies).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Default banned / hedge phrases (used when no style YAML is supplied)
# ---------------------------------------------------------------------------

DEFAULT_BANNED_PHRASES: list[str] = [
    "it is important to note",
    "it should be noted",
    "it is worth mentioning",
    "needless to say",
    "it goes without saying",
    "as everyone knows",
    "obviously",
    "clearly",
    "of course",
    "basically",
    "essentially",
    "in order to",
    "due to the fact that",
    "at the end of the day",
    "paradigm shift",
    "thinking outside the box",
    "leverage",
    "utilize",
    "synergy",
    "holistic",
    "novel approach",
    "state-of-the-art",
    "groundbreaking",
    "revolutionary",
]

DEFAULT_HEDGE_PHRASES: list[str] = [
    "might",
    "perhaps",
    "possibly",
    "somewhat",
    "to some extent",
    "it seems",
    "it appears",
    "arguably",
    "could potentially",
    "may or may not",
    "it is possible that",
    "one could argue",
    "tends to",
    "in some cases",
    "rather",
    "quite",
    "fairly",
    "relatively",
    "slightly",
    "more or less",
]

DEFAULT_SECTION_TARGETS: dict[str, float] = {
    "introduction": 0.12,
    "background": 0.10,
    "framework": 0.20,
    "experiments": 0.25,
    "results": 0.15,
    "discussion": 0.10,
    "conclusion": 0.05,
    "related work": 0.10,
}

# ---------------------------------------------------------------------------
# YAML parser — try PyYAML first, fall back to recursive stdlib parser
# ---------------------------------------------------------------------------


def _parse_yaml(text: str) -> dict:
    """Parse YAML with PyYAML if available, else a recursive stdlib parser."""
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        return _parse_yaml_stdlib(text)


def _parse_yaml_stdlib(text: str) -> dict:
    """Recursive indent-based YAML parser (stdlib only).

    Handles arbitrary nesting of dicts and lists. Good enough for our
    paper-style.yaml which has 3 levels of nesting.
    """
    lines = []
    for raw in text.splitlines():
        stripped = raw.split("#")[0].rstrip()  # strip comments
        if stripped.strip():
            lines.append(stripped)

    result, _ = _parse_block(lines, 0, 0)
    return result if isinstance(result, dict) else {}


def _parse_block(lines: list[str], start: int, min_indent: int):
    """Parse a YAML block (dict or list) starting at the given line index."""
    if start >= len(lines):
        return {}, start

    first_stripped = lines[start].strip()

    # Detect if this block is a list
    if first_stripped.startswith("- "):
        return _parse_list(lines, start, min_indent)
    else:
        return _parse_dict(lines, start, min_indent)


def _parse_dict(lines: list[str], start: int, min_indent: int):
    """Parse a YAML dict block."""
    result: dict = {}
    i = start

    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip())

        if indent < min_indent:
            break

        stripped = line.strip()
        m = re.match(r"^([\w][\w\s_-]*):\s*(.*)", stripped)
        if not m:
            i += 1
            continue

        key = m.group(1).strip()
        val = m.group(2).strip()

        if val:
            result[key] = _coerce(val)
            i += 1
        else:
            # Value is on subsequent indented lines
            child_indent = indent + 2
            if i + 1 < len(lines):
                next_indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
                if next_indent > indent:
                    child_indent = next_indent

            child, i = _parse_block(lines, i + 1, child_indent)
            result[key] = child
            continue

    return result, i


def _parse_list(lines: list[str], start: int, min_indent: int):
    """Parse a YAML list block."""
    result: list = []
    i = start

    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip())

        if indent < min_indent:
            break

        stripped = line.strip()
        if stripped.startswith("- "):
            item_text = stripped[2:].strip().strip("\"'")
            result.append(_coerce(item_text))
            i += 1
        else:
            break

    return result, i


def _coerce(val: str):
    """Coerce a YAML scalar string to int/float/bool/str."""
    if not val:
        return val
    if val.lower() in ("true", "yes"):
        return True
    if val.lower() in ("false", "no"):
        return False
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val.strip("\"'")


# ---------------------------------------------------------------------------
# LaTeX helpers
# ---------------------------------------------------------------------------

_COMMENT_RE = re.compile(r"(?<!\\)%.*$")
_COMMAND_RE = re.compile(r"\\[a-zA-Z]+\*?(\{[^}]*\})*")
_ENV_TAG_RE = re.compile(r"\\(begin|end)\{[^}]*\}")


def strip_comments(lines: list[str]) -> list[str]:
    """Remove LaTeX comments from lines."""
    return [_COMMENT_RE.sub("", ln) for ln in lines]


def strip_latex_commands(text: str) -> str:
    """Remove LaTeX commands for word counting, keeping text arguments."""
    text = _ENV_TAG_RE.sub("", text)
    # Replace \command{arg} with just arg
    prev = ""
    while prev != text:
        prev = text
        text = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", text)
    # Remove remaining bare commands like \item, \par, etc.
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    # Remove braces / special chars
    text = re.sub(r"[{}\[\]~]", " ", text)
    return text


def count_words(text: str) -> int:
    """Count words in stripped text."""
    return len(strip_latex_commands(text).split())


def count_sentences(text: str) -> int:
    """Rough sentence count based on period/question/exclamation marks."""
    cleaned = strip_latex_commands(text)
    # Remove common abbreviations that have periods
    cleaned = re.sub(r"\b(e\.g|i\.e|et al|Fig|Eq|Sec|etc)\.", "", cleaned)
    return max(1, len(re.findall(r"[.?!]+", cleaned)))


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------


def check_hedges(
    lines: list[str], hedge_phrases: list[str]
) -> dict:
    """Detect hedge phrases, return count, density, and instances."""
    instances = []
    total_words = 0
    for i, line in enumerate(lines, 1):
        stripped = strip_latex_commands(line)
        total_words += len(stripped.split())
        lower = stripped.lower()
        for phrase in hedge_phrases:
            if phrase.lower() in lower:
                # Extract surrounding context (up to 80 chars around match)
                idx = lower.index(phrase.lower())
                start = max(0, idx - 30)
                end = min(len(stripped), idx + len(phrase) + 30)
                context = stripped[start:end].strip()
                instances.append(
                    {"line_number": i, "phrase": phrase, "context": context}
                )

    total_words = max(total_words, 1)
    density = round(len(instances) / (total_words / 1000), 2)
    return {"count": len(instances), "density": density, "instances": instances}


def check_passive_voice(lines: list[str]) -> dict:
    """Approximate passive voice detection.

    Catches both regular (-ed) and common irregular past participles
    used in academic writing (shown, known, found, proven, etc.).
    """
    _IRREGULAR_PP = (
        "shown|known|found|proven|proved|given|taken|seen|written|made|done|"
        "built|run|held|set|put|cut|drawn|grown|thrown|worn|torn|born|"
        "chosen|spoken|broken|frozen|stolen|driven|risen|fallen|forgotten|"
        "begun|become|come|overcome|understood|meant|thought|taught|brought|"
        "caught|fought|sought|told|sold|lost|sent|spent|left|kept|felt|met"
    )
    pattern = re.compile(
        r"\b(was|were|is|are|has been|have been|had been|being)\s+"
        r"(\w+ed|" + _IRREGULAR_PP + r")\b",
        re.IGNORECASE,
    )
    full_text = " ".join(lines)
    matches = pattern.findall(full_text)
    count = len(matches)
    total_sentences = count_sentences(full_text)
    ratio = round(count / max(total_sentences, 1), 3)
    return {"ratio": ratio, "count": count}


def check_section_ratios(
    lines: list[str], target_ratios: dict[str, float]
) -> dict:
    """Parse sections, compute word counts and compare to targets."""
    section_re = re.compile(r"\\(section|subsection)\{([^}]+)\}")
    sections: list[dict] = []
    current_name: str | None = None
    current_text_lines: list[str] = []

    def _flush():
        if current_name is not None:
            text = "\n".join(current_text_lines)
            wc = count_words(text)
            sections.append({"name": current_name, "word_count": wc, "lines": current_text_lines[:]})

    for line in lines:
        m = section_re.search(line)
        if m:
            _flush()
            current_name = m.group(2).strip()
            current_text_lines = []
        else:
            if current_name is not None:
                current_text_lines.append(line)
    _flush()

    total_words = max(sum(s["word_count"] for s in sections), 1)
    all_within = True
    result_sections = []
    for s in sections:
        actual_ratio = round(s["word_count"] / total_words, 3)
        # Match target by lowercase partial match
        name_lower = s["name"].lower()
        target = None
        for tname, tratio in target_ratios.items():
            if tname.lower() in name_lower or name_lower in tname.lower():
                target = tratio
                break
        if target is not None:
            over_under = round(actual_ratio / target, 2) if target > 0 else 0
            if over_under > 1.5:
                all_within = False
            entry = {
                "section_name": s["name"],
                "word_count": s["word_count"],
                "actual_ratio": actual_ratio,
                "target_ratio": target,
                "over_under": over_under,
            }
        else:
            entry = {
                "section_name": s["name"],
                "word_count": s["word_count"],
                "actual_ratio": actual_ratio,
                "target_ratio": None,
                "over_under": None,
            }
        result_sections.append(entry)

    return {"sections": result_sections, "all_within_target": all_within}


def check_banned_phrases(
    lines: list[str], banned_phrases: list[str]
) -> dict:
    """Scan for banned phrases."""
    instances = []
    for i, line in enumerate(lines, 1):
        stripped = strip_latex_commands(line)
        lower = stripped.lower()
        for phrase in banned_phrases:
            if phrase.lower() in lower:
                idx = lower.index(phrase.lower())
                start = max(0, idx - 30)
                end = min(len(stripped), idx + len(phrase) + 30)
                context = stripped[start:end].strip()
                instances.append(
                    {"line_number": i, "phrase": phrase, "context": context}
                )
    return {"count": len(instances), "instances": instances}


def check_captions(lines: list[str]) -> dict:
    """Check caption quality: >15 words and contains a takeaway."""
    caption_re = re.compile(r"\\caption\{", re.IGNORECASE)
    captions: list[dict] = []
    full_text = "\n".join(lines)

    # Find all \caption{...} blocks (handle nested braces)
    i = 0
    fig_counter = 0
    while i < len(full_text):
        m = caption_re.search(full_text, i)
        if not m:
            break
        fig_counter += 1
        # Extract balanced braces
        start = m.end()  # right after the opening brace
        depth = 1
        j = start
        while j < len(full_text) and depth > 0:
            if full_text[j] == "{":
                depth += 1
            elif full_text[j] == "}":
                depth -= 1
            j += 1
        caption_text = full_text[start : j - 1].strip()
        cleaned = strip_latex_commands(caption_text)
        wc = len(cleaned.split())

        # Takeaway heuristic: contains a number or comparative/superlative
        has_number = bool(re.search(r"\d+", cleaned))
        has_comparative = bool(
            re.search(
                r"\b(more|less|higher|lower|better|worse|larger|smaller|fastest|"
                r"slowest|strongest|weakest|most|least|outperform|exceed|surpass|"
                r"increase|decrease|improvement|degradation|gain|drop|rise|fall|"
                r"significant|notably)\b",
                cleaned,
                re.IGNORECASE,
            )
        )
        has_takeaway = (wc > 15) and (has_number or has_comparative)

        entry: dict = {
            "figure_id": f"fig{fig_counter}",
            "caption_text": cleaned[:120],
            "word_count": wc,
            "has_takeaway": has_takeaway,
        }
        captions.append(entry)
        i = j

    missing = [c for c in captions if not c["has_takeaway"]]
    return {
        "total": len(captions),
        "with_takeaway": len(captions) - len(missing),
        "missing": missing,
    }


def check_citations(tex_path: Path, lines: list[str]) -> dict:
    """Parse the .bib file and compute citation freshness."""
    # Find .bib file: look for \bibliography{...} or search in same/parent dir
    bib_path = None
    full_text = "\n".join(lines)
    bib_match = re.search(r"\\bibliography\{([^}]+)\}", full_text)
    if bib_match:
        bib_name = bib_match.group(1).strip()
        if not bib_name.endswith(".bib"):
            bib_name += ".bib"
        # Try relative to tex file
        candidate = tex_path.parent / bib_name
        if candidate.exists():
            bib_path = candidate

    # Also check \addbibresource{...}
    if bib_path is None:
        bib_match2 = re.search(r"\\addbibresource\{([^}]+)\}", full_text)
        if bib_match2:
            bib_name = bib_match2.group(1).strip()
            candidate = tex_path.parent / bib_name
            if candidate.exists():
                bib_path = candidate

    # Fallback: find any .bib in same dir or parent
    if bib_path is None:
        for d in [tex_path.parent, tex_path.parent.parent]:
            bibs = list(d.glob("*.bib"))
            if bibs:
                bib_path = bibs[0]
                break

    if bib_path is None or not bib_path.exists():
        return {"total": 0, "recent": 0, "ratio": 0.0}

    bib_text = bib_path.read_text(encoding="utf-8", errors="replace")
    year_re = re.compile(r"\byear\s*=\s*[{\"']?(\d{4})", re.IGNORECASE)
    years = [int(m.group(1)) for m in year_re.finditer(bib_text)]

    if not years:
        return {"total": 0, "recent": 0, "ratio": 0.0}

    # "last 2 years" relative to the most recent entry (or current year)
    import datetime

    current_year = datetime.datetime.now().year
    recent_threshold = current_year - 2
    recent = sum(1 for y in years if y >= recent_threshold)
    total = len(years)
    ratio = round(recent / max(total, 1), 3)
    return {"total": total, "recent": recent, "ratio": ratio}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def compute_score(checks: dict) -> int:
    """Compute overall score (0-100) from check results.

    Uses linear scaling instead of binary pass/fail — a paper with
    hedge density 4.9 shouldn't score 20 points higher than one at 5.1.
    """
    score = 0.0

    # Hedge density: 20 points, linear scale (0 at density=10, 20 at density=0)
    density = checks["hedges"]["density"]
    score += max(0, 20 * (1 - density / 10))

    # Passive voice: 15 points, linear scale (0 at ratio=0.40, 15 at ratio=0)
    pv_ratio = checks["passive_voice"]["ratio"]
    score += max(0, 15 * (1 - pv_ratio / 0.40))

    # Section ratios: 20 points. Lose points per section that's >150% of target
    sections = checks["section_ratios"]["sections"]
    sections_with_target = [s for s in sections if s.get("target_ratio") is not None]
    if sections_with_target:
        violations = sum(1 for s in sections_with_target if s.get("over_under", 0) and s["over_under"] > 1.5)
        score += max(0, 20 * (1 - violations / max(len(sections_with_target), 1)))
    else:
        score += 20

    # Banned phrases: 15 points, lose 3 per occurrence (0 at 5+)
    bp_count = checks["banned_phrases"]["count"]
    score += max(0, 15 - bp_count * 3)

    # Captions with takeaways: 15 points, proportional
    cap = checks["captions"]
    if cap["total"] > 0:
        score += 15 * (cap["with_takeaway"] / cap["total"])
    else:
        score += 15

    # Citation freshness: 15 points, linear (0 at 0%, 15 at 30%+)
    cit_ratio = checks["citations"]["ratio"]
    score += min(15, 15 * (cit_ratio / 0.30))

    return round(score)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def load_style(style_path: str | None) -> dict:
    """Load style config from YAML, navigating the nested structure.

    Our paper-style.yaml nests banned_phrases under voice: and
    section_ratios under structure:. This function extracts them
    into the flat config dict the checker expects.
    """
    config: dict = {
        "banned_phrases": DEFAULT_BANNED_PHRASES,
        "hedge_phrases": DEFAULT_HEDGE_PHRASES,
        "section_targets": DEFAULT_SECTION_TARGETS,
    }

    if style_path is None:
        return config

    p = Path(style_path)
    if not p.exists():
        print(f"Warning: style file {style_path} not found, using defaults", file=sys.stderr)
        return config

    raw = _parse_yaml(p.read_text(encoding="utf-8"))

    # Extract banned phrases from voice.banned_phrases (nested) or top-level
    voice = raw.get("voice", {})
    if isinstance(voice, dict):
        if "banned_phrases" in voice and isinstance(voice["banned_phrases"], list):
            config["banned_phrases"] = voice["banned_phrases"]
        # Use banned_phrases as the hedge list too — our curated list is
        # better calibrated than the generic defaults
        if "banned_phrases" in voice:
            config["hedge_phrases"] = voice["banned_phrases"]

    # Also check top-level (flat YAML format)
    if "banned_phrases" in raw and isinstance(raw["banned_phrases"], list):
        config["banned_phrases"] = raw["banned_phrases"]
    if "hedge_phrases" in raw and isinstance(raw["hedge_phrases"], list):
        config["hedge_phrases"] = raw["hedge_phrases"]

    # Extract section ratios from structure.section_ratios (nested) or top-level
    structure = raw.get("structure", {})
    if isinstance(structure, dict):
        ratios = structure.get("section_ratios", {})
        if isinstance(ratios, dict):
            config["section_targets"] = {
                k: float(v) for k, v in ratios.items() if isinstance(v, (int, float))
            }

    if "section_targets" in raw and isinstance(raw["section_targets"], dict):
        config["section_targets"] = {
            k: float(v) for k, v in raw["section_targets"].items()
        }

    return config


def run(tex_path: str, style_path: str | None = None, verbose: bool = False) -> dict:
    """Run all checks and return the result dict."""
    p = Path(tex_path)
    if not p.exists():
        print(f"Error: {tex_path} not found", file=sys.stderr)
        sys.exit(1)

    raw_lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    lines = strip_comments(raw_lines)

    style = load_style(style_path)

    full_text = "\n".join(lines)
    total_words = count_words(full_text)

    checks = {
        "hedges": check_hedges(lines, style["hedge_phrases"]),
        "passive_voice": check_passive_voice(lines),
        "section_ratios": check_section_ratios(lines, style["section_targets"]),
        "banned_phrases": check_banned_phrases(lines, style["banned_phrases"]),
        "captions": check_captions(lines),
        "citations": check_citations(p, lines),
    }

    score = compute_score(checks)

    result = {
        "file": p.name,
        "total_words": total_words,
        "score": score,
        "checks": checks,
    }

    if verbose:
        _print_summary(result, sys.stderr)

    return result


def _print_summary(result: dict, out) -> None:
    """Print a human-readable summary."""
    print(f"\n{'=' * 60}", file=out)
    print(f"  Style Check: {result['file']}", file=out)
    print(f"  Total words: {result['total_words']}", file=out)
    print(f"  Score: {result['score']} / 100", file=out)
    print(f"{'=' * 60}\n", file=out)

    c = result["checks"]

    # Hedges
    h = c["hedges"]
    print(f"  Hedges: {h['count']} found (density: {h['density']}/1000 words)", file=out)
    for inst in h["instances"][:5]:
        print(f"    L{inst['line_number']}: \"{inst['phrase']}\" — ...{inst['context']}...", file=out)
    if h["count"] > 5:
        print(f"    ... and {h['count'] - 5} more", file=out)

    # Passive voice
    pv = c["passive_voice"]
    status = "OK" if pv["ratio"] < 0.20 else "HIGH"
    print(f"\n  Passive voice: {pv['count']} instances, ratio {pv['ratio']} [{status}]", file=out)

    # Section ratios
    sr = c["section_ratios"]
    print(f"\n  Section ratios (within target: {sr['all_within_target']}):", file=out)
    for s in sr["sections"]:
        target_str = f" (target: {s['target_ratio']})" if s["target_ratio"] is not None else ""
        flag = ""
        if s["over_under"] is not None and s["over_under"] > 1.5:
            flag = " [OVER]"
        print(f"    {s['section_name']}: {s['word_count']} words ({s['actual_ratio']:.1%}){target_str}{flag}", file=out)

    # Banned phrases
    bp = c["banned_phrases"]
    print(f"\n  Banned phrases: {bp['count']}", file=out)
    for inst in bp["instances"][:5]:
        print(f"    L{inst['line_number']}: \"{inst['phrase']}\" — ...{inst['context']}...", file=out)

    # Captions
    cap = c["captions"]
    print(f"\n  Captions: {cap['with_takeaway']}/{cap['total']} with takeaway", file=out)
    for m in cap["missing"]:
        print(f"    {m['figure_id']}: \"{m['caption_text'][:60]}...\" ({m['word_count']} words)", file=out)

    # Citations
    cit = c["citations"]
    print(f"\n  Citations: {cit['recent']}/{cit['total']} recent (ratio: {cit['ratio']})", file=out)

    print("", file=out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check a .tex file against the paper style specification."
    )
    parser.add_argument("tex_file", help="Path to the .tex file to check")
    parser.add_argument(
        "--style",
        default=None,
        help="Path to paper-style.yaml (optional, uses defaults if omitted)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print human-readable summary to stderr"
    )
    args = parser.parse_args()

    result = run(args.tex_file, args.style, args.verbose)
    json.dump(result, sys.stdout, indent=2)
    print()  # trailing newline


if __name__ == "__main__":
    main()
