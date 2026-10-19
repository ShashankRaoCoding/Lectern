"""Render Markdown (with ```mermaid fences) to safe HTML."""
import html
import re

import markdown as md
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

MERMAID_RE = re.compile(r"```mermaid[ \t]*\n(.*?)\n```", re.DOTALL)


@register.filter
def render_markdown(text: str):
    blocks = []

    def stash(match):
        blocks.append(match.group(1))
        return f"\n\nMERMAIDBLOCK{len(blocks) - 1}END\n\n"

    text = MERMAID_RE.sub(stash, text or "")
    rendered = md.markdown(text, extensions=["fenced_code", "tables", "toc", "sane_lists"])
    clean = nh3.clean(rendered)
    for i, code in enumerate(blocks):
        clean = clean.replace(
            f"<p>MERMAIDBLOCK{i}END</p>",
            f'<pre class="mermaid">{html.escape(code)}</pre>',
        )
    return mark_safe(clean)
