"""Render Markdown (with ```mermaid fences and LaTeX math) to safe HTML.

Math is pulled out before Markdown runs (so `_`, `*`, `\\` aren't mangled),
HTML-escaped, and put back as <span class="math-inline"> / <div class="math-display">
elements that KaTeX typesets in the browser (see _katex.html).

Supported: $$...$$, \\[...\\], \\(...\\), $...$, and bare commands such as
\\text{PrP}^\\text{C} (wrapped as inline math automatically).
"""
import html
import re

import markdown as md
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

MERMAID_RE = re.compile(r"```mermaid[ \t]*\n(.*?)\n```", re.DOTALL)
FENCE_RE = re.compile(r"(```.*?```|~~~.*?~~~)", re.DOTALL)
CODE_SPAN_RE = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)", re.DOTALL)

DISPLAY_RES = [
    re.compile(r"\$\$(.+?)\$\$", re.DOTALL),
    re.compile(r"\\\[(.+?)\\\]", re.DOTALL),
]
INLINE_RES = [
    re.compile(r"\\\((.+?)\\\)", re.DOTALL),
    # $...$ — not currency ("$5 and $10"): no space inside the edges, no digit/word after the closer
    re.compile(r"(?<![\\$\w])\$(?![\s$])([^$\n]+?)(?<![\s\\])\$(?![\w$])"),
]
# A bare LaTeX command with a braced argument, plus any chained ^/_ scripts or further commands:
#   \text{PrP}^\text{C}   \text{PrP}^{Sc}   \alpha_{i}   \mathrm{H}_2\mathrm{O}
_ARG = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
_CMD = rf"\\[A-Za-z]+(?:{_ARG})+"
BARE_RE = re.compile(rf"{_CMD}(?:(?:[\^_](?:{_CMD}|{_ARG}|[A-Za-z0-9+\-]))|{_CMD})*")


def _stash(pattern, text, store, kind):
    def repl(m):
        store.append((kind, m.group(1) if m.groups() else m.group(0)))
        return f"MATHTOKEN{len(store) - 1}END"

    return pattern.sub(repl, text)


@register.filter
def render_markdown(text: str):
    text = text or ""

    # 1. mermaid
    diagrams = []

    def stash_mermaid(match):
        diagrams.append(match.group(1))
        return f"\n\nMERMAIDBLOCK{len(diagrams) - 1}END\n\n"

    text = MERMAID_RE.sub(stash_mermaid, text)

    # 2. code (math inside code must stay literal)
    code = []

    def stash_code(match):
        code.append(match.group(0))
        return f"CODETOKEN{len(code) - 1}END"

    text = FENCE_RE.sub(stash_code, text)
    text = CODE_SPAN_RE.sub(stash_code, text)

    # 3. math
    math = []
    for pat in DISPLAY_RES:
        text = _stash(pat, text, math, "display")
    for pat in INLINE_RES:
        text = _stash(pat, text, math, "inline")
    text = _stash(BARE_RE, text, math, "inline")

    # 4. restore code, run Markdown, sanitise
    for i, chunk in enumerate(code):
        text = text.replace(f"CODETOKEN{i}END", chunk)
    rendered = md.markdown(text, extensions=["fenced_code", "tables", "toc", "sane_lists"])
    clean = nh3.clean(rendered)

    # 5. put math and diagrams back (after sanitising, with everything escaped)
    for i, (kind, tex) in enumerate(math):
        tex = html.escape(tex.strip())
        token = f"MATHTOKEN{i}END"
        if kind == "display":
            block = f'<div class="math-display">\\[{tex}\\]</div>'
            clean = clean.replace(f"<p>{token}</p>", block)
            clean = clean.replace(token, block)
        else:
            clean = clean.replace(token, f'<span class="math-inline">\\({tex}\\)</span>')
    for i, src in enumerate(diagrams):
        clean = clean.replace(
            f"<p>MERMAIDBLOCK{i}END</p>",
            f'<pre class="mermaid">{html.escape(src)}</pre>',
        )
    return mark_safe(clean)
