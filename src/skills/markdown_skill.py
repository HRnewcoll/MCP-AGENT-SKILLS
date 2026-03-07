"""Markdown skill – convert between Markdown and HTML (and plain text).

Covers the "Web & Frontend Development" category from the
awesome-openclaw-skills directory.  Uses Python stdlib only – no external
dependencies required.

Supported actions
-----------------
to_html         Convert Markdown text to basic HTML.
to_plain        Strip Markdown syntax and return plain text.
extract_links   Extract all hyperlinks from Markdown text.
extract_headers Extract all header lines (h1-h6) from Markdown.
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Markdown → HTML conversion helpers
# ---------------------------------------------------------------------------

def _md_to_html(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    in_code_block = False
    in_ul = False
    in_ol = False

    def close_list() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for line in lines:
        # Fenced code blocks
        if line.startswith("```"):
            if in_code_block:
                out.append("</code></pre>")
                in_code_block = False
            else:
                close_list()
                lang = line[3:].strip()
                attr = f' class="language-{lang}"' if lang else ""
                out.append(f"<pre><code{attr}>")
                in_code_block = True
            continue

        if in_code_block:
            out.append(_escape(line))
            continue

        # Horizontal rule
        if re.match(r"^(\-{3,}|\*{3,}|_{3,})$", line.strip()):
            close_list()
            out.append("<hr>")
            continue

        # Headers
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            close_list()
            level = len(m.group(1))
            content = _inline(m.group(2))
            out.append(f"<h{level}>{content}</h{level}>")
            continue

        # Ordered list
        m = re.match(r"^\d+\.\s+(.*)", line)
        if m:
            if in_ul:
                close_list()
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{_inline(m.group(1))}</li>")
            continue

        # Unordered list
        m = re.match(r"^[-*+]\s+(.*)", line)
        if m:
            if in_ol:
                close_list()
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_inline(m.group(1))}</li>")
            continue

        # Blockquote
        if line.startswith("> "):
            close_list()
            out.append(f"<blockquote>{_inline(line[2:])}</blockquote>")
            continue

        # Blank line
        if not line.strip():
            close_list()
            out.append("")
            continue

        # Paragraph
        close_list()
        out.append(f"<p>{_inline(line)}</p>")

    close_list()
    return "\n".join(out)


def _inline(text: str) -> str:
    """Apply inline markdown (bold, italic, code, links, images)."""
    # Inline code
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{_escape(m.group(1))}</code>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)
    # Images  (before links)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Strikethrough
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    return text


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _md_to_plain(md: str) -> str:
    """Strip Markdown syntax and return plain text."""
    text = md
    # Remove fenced code blocks (keep content)
    text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", text, flags=re.DOTALL)
    # Remove headers markup
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", text)
    text = re.sub(r"_{1,2}(.+?)_{1,2}", r"\1", text)
    # Remove inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove images
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    # Convert links to text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^(\-{3,}|\*{3,}|_{3,})$", "", text, flags=re.MULTILINE)
    # Remove blockquote markers
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # Remove list markers
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    # Collapse extra whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class MarkdownSkill:
    """Convert Markdown to HTML, plain text, or extract structured data."""

    name = "markdown"
    description = (
        "Process Markdown text. "
        "Supported actions: 'to_html' (text); 'to_plain' (text); "
        "'extract_links' (text); 'extract_headers' (text)."
    )

    def run(self, action: str, text: str = "") -> str:
        """
        Perform a Markdown operation.

        Parameters
        ----------
        action:
            One of ``"to_html"``, ``"to_plain"``, ``"extract_links"``,
            ``"extract_headers"``.
        text:
            Markdown source text.

        Returns
        -------
        str
            Processed output or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "to_html":
            if not text:
                return "Error: text is required"
            return _md_to_html(text)

        if action == "to_plain":
            if not text:
                return "Error: text is required"
            return _md_to_plain(text)

        if action == "extract_links":
            if not text:
                return "Error: text is required"
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
            if not links:
                return "(no links found)"
            return "\n".join(f"{label}: {url}" for label, url in links)

        if action == "extract_headers":
            if not text:
                return "Error: text is required"
            headers = re.findall(r"^(#{1,6})\s+(.+)", text, re.MULTILINE)
            if not headers:
                return "(no headers found)"
            return "\n".join(f"{'  ' * (len(h) - 1)}{h} {title}" for h, title in headers)

        return (
            f"Error: unknown action {action!r}. "
            "Use to_html, to_plain, extract_links, or extract_headers."
        )
