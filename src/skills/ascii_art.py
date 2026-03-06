"""ASCII art skill – create text banners, boxes, tables, and dividers.

Covers the "Communication" and "Clawdbot Tools" categories from the
awesome-openclaw-skills directory.  Uses Python stdlib only.

Supported actions
-----------------
banner          Wrap text in a decorative box banner.
box             Draw a simple border box around text.
divider         Print a horizontal divider line.
table           Render a simple ASCII table from pipe-separated data.
progress_bar    Display a text progress bar.
bullet_list     Format a comma-separated list as bullet points.
"""

from __future__ import annotations


# Available border styles
_STYLES: dict[str, dict[str, str]] = {
    "single": {
        "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
        "h": "─", "v": "│",
    },
    "double": {
        "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
        "h": "═", "v": "║",
    },
    "rounded": {
        "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
        "h": "─", "v": "│",
    },
    "ascii": {
        "tl": "+", "tr": "+", "bl": "+", "br": "+",
        "h": "-", "v": "|",
    },
    "heavy": {
        "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛",
        "h": "━", "v": "┃",
    },
}


class AsciiArtSkill:
    """Create ASCII art banners, boxes, tables, and dividers."""

    name = "ascii_art"
    description = (
        "Create ASCII art and formatted output. "
        "Supported actions: 'banner' (text, style); 'box' (text, style); "
        "'divider' (char, width); 'table' (text, header); "
        "'progress_bar' (value, total, width); 'bullet_list' (text, bullet)."
        "\nStyles: single, double, rounded, ascii, heavy."
    )

    def run(
        self,
        action: str,
        text: str = "",
        style: str = "single",
        char: str = "─",
        width: int = 60,
        value: float = 50.0,
        total: float = 100.0,
        header: bool = True,
        bullet: str = "•",
    ) -> str:
        """
        Create ASCII art.

        Parameters
        ----------
        action:
            One of ``"banner"``, ``"box"``, ``"divider"``, ``"table"``,
            ``"progress_bar"``, ``"bullet_list"``.
        text:
            Input text (for banner / box / table / bullet_list).
        style:
            Border style for banner/box: single, double, rounded, ascii,
            heavy (default: single).
        char:
            Character to repeat for ``"divider"`` (default ``"─"``).
        width:
            Width for divider (default 60) and progress bar.
        value:
            Current value for progress bar.
        total:
            Total/max value for progress bar (default 100).
        header:
            Whether the first row of ``"table"`` data is a header
            (default ``True``).
        bullet:
            Bullet character for ``"bullet_list"`` (default ``"•"``).

        Returns
        -------
        str
            Rendered ASCII art or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "banner":
            return self._banner(text, style)
        if action == "box":
            return self._box(text, style)
        if action == "divider":
            return self._divider(char, width)
        if action == "table":
            return self._table(text, header)
        if action == "progress_bar":
            return self._progress_bar(value, total, width)
        if action == "bullet_list":
            return self._bullet_list(text, bullet)
        return (
            f"Error: unknown action {action!r}. "
            "Use banner, box, divider, table, progress_bar, or bullet_list."
        )

    # ------------------------------------------------------------------
    # Implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _get_style(style: str) -> dict[str, str]:
        return _STYLES.get(style.lower(), _STYLES["single"])

    def _banner(self, text: str, style: str) -> str:
        if not text:
            return "Error: text is required"
        s = self._get_style(style)
        lines = text.split("\n")
        max_w = max(len(ln) for ln in lines)
        border = s["h"] * (max_w + 4)
        top = s["tl"] + border + s["tr"]
        bot = s["bl"] + border + s["br"]
        blank = s["v"] + " " * (max_w + 4) + s["v"]
        rows = [top, blank]
        for ln in lines:
            rows.append(s["v"] + "  " + ln.center(max_w) + "  " + s["v"])
        rows.extend([blank, bot])
        return "\n".join(rows)

    def _box(self, text: str, style: str) -> str:
        if not text:
            return "Error: text is required"
        s = self._get_style(style)
        lines = text.split("\n")
        max_w = max(len(ln) for ln in lines)
        border = s["h"] * (max_w + 2)
        top = s["tl"] + border + s["tr"]
        bot = s["bl"] + border + s["br"]
        rows = [top]
        for ln in lines:
            rows.append(s["v"] + " " + ln.ljust(max_w) + " " + s["v"])
        rows.append(bot)
        return "\n".join(rows)

    @staticmethod
    def _divider(char: str, width: int) -> str:
        c = (char or "─")[0]
        return c * max(1, min(200, int(width)))

    @staticmethod
    def _table(text: str, header: bool) -> str:
        if not text:
            return "Error: text is required (pipe-separated rows, one per line)"
        rows = [
            [cell.strip() for cell in line.split("|")]
            for line in text.strip().split("\n")
            if line.strip()
        ]
        if not rows:
            return "(no data)"
        col_count = max(len(r) for r in rows)
        # Pad rows to same width
        rows = [r + [""] * (col_count - len(r)) for r in rows]
        widths = [max(len(r[c]) for r in rows) for c in range(col_count)]
        sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        lines = [sep]
        for i, row in enumerate(rows):
            line = "|" + "|".join(f" {row[c]:<{widths[c]}} " for c in range(col_count)) + "|"
            lines.append(line)
            if header and i == 0:
                lines.append(sep)
        lines.append(sep)
        return "\n".join(lines)

    @staticmethod
    def _progress_bar(value: float, total: float, width: int) -> str:
        if total <= 0:
            return "Error: total must be greater than 0"
        width = max(10, min(200, int(width)))
        pct = max(0.0, min(1.0, float(value) / float(total)))
        filled = int(round(pct * width))
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {pct * 100:.1f}%  ({value}/{total})"

    @staticmethod
    def _bullet_list(text: str, bullet: str) -> str:
        if not text:
            return "Error: text is required"
        items = [item.strip() for item in text.split(",") if item.strip()]
        if not items:
            return "(empty list)"
        b = (bullet or "•")[0]
        return "\n".join(f"{b} {item}" for item in items)
