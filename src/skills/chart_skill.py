"""ASCII chart skill – render bar charts, histograms, and sparklines in the terminal.

Covers the "Data & Analytics" and "CLI Utilities" categories.
Pure Python, no external libraries.

Supported actions
-----------------
bar             Horizontal bar chart from labeled values.
hbar            Alias for bar.
histogram       Frequency histogram from raw numeric data.
sparkline       Compact one-line sparkline of a numeric series.
pie_text        Text-based pie chart (percentage breakdown).
"""

from __future__ import annotations

import re


def _parse_labeled(data: str) -> list[tuple[str, float]]:
    """Parse 'label:value, label:value' or 'val1, val2' format."""
    items: list[tuple[str, float]] = []
    for part in data.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            label, _, val = part.partition(":")
            items.append((label.strip(), float(val.strip())))
        else:
            items.append((part, float(part)))
    return items


def _parse_numbers(data: str) -> list[float]:
    return [float(x.strip()) for x in data.split(",") if x.strip()]


class ChartSkill:
    """Render ASCII bar charts, histograms, sparklines, and text pie charts."""

    name = "chart"
    description = (
        "ASCII chart rendering. "
        "Supported actions: 'bar' (data – 'label:value,...' or 'v1,v2,...', width=40); "
        "'histogram' (data – comma-separated numbers, bins=10); "
        "'sparkline' (data – comma-separated numbers); "
        "'pie_text' (data – 'label:value,...')."
    )

    def run(
        self,
        action: str,
        data: str = "",
        width: int = 40,
        bins: int = 10,
    ) -> str:
        """
        Render an ASCII chart.

        Parameters
        ----------
        action:
            One of ``"bar"``, ``"hbar"``, ``"histogram"``,
            ``"sparkline"``, ``"pie_text"``.
        data:
            Input data (see description for format).
        width:
            Maximum bar width in characters for bar charts (default 40).
        bins:
            Number of bins for histogram (default 10).

        Returns
        -------
        str
            Rendered chart or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if not data:
            return "Error: data is required"

        try:
            if action in ("bar", "hbar"):
                return self._bar(data, int(width))
            if action == "histogram":
                return self._histogram(data, int(bins))
            if action == "sparkline":
                return self._sparkline(data)
            if action == "pie_text":
                return self._pie_text(data)
        except (ValueError, ZeroDivisionError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use bar, histogram, sparkline, or pie_text."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _bar(data: str, width: int) -> str:
        try:
            items = _parse_labeled(data)
        except ValueError:
            return "Error: data must be 'label:value,...' or comma-separated numbers"
        if not items:
            return "Error: no data"
        max_val = max(v for _, v in items)
        if max_val == 0:
            return "Error: all values are zero"
        label_w = max(len(lbl) for lbl, _ in items)
        lines: list[str] = []
        for label, val in items:
            bar_len = int(val / max_val * width)
            bar = "█" * bar_len
            lines.append(f"{label:>{label_w}} │{bar} {val:.2g}")
        return "\n".join(lines)

    @staticmethod
    def _histogram(data: str, bins: int) -> str:
        try:
            nums = _parse_numbers(data)
        except ValueError:
            return "Error: data must be comma-separated numbers"
        if not nums:
            return "Error: no data"
        lo, hi = min(nums), max(nums)
        if lo == hi:
            return f"All values are {lo}"
        step = (hi - lo) / bins
        counts = [0] * bins
        for v in nums:
            idx = min(int((v - lo) / step), bins - 1)
            counts[idx] += 1
        max_count = max(counts)
        bar_width = 30
        lines: list[str] = []
        for i, cnt in enumerate(counts):
            lo_edge = lo + i * step
            hi_edge = lo_edge + step
            bar = "█" * int(cnt / max_count * bar_width) if max_count else ""
            lines.append(f"[{lo_edge:>8.2f},{hi_edge:>8.2f}) │{bar} {cnt}")
        return "\n".join(lines)

    @staticmethod
    def _sparkline(data: str) -> str:
        _SPARKS = "▁▂▃▄▅▆▇█"
        try:
            nums = _parse_numbers(data)
        except ValueError:
            return "Error: data must be comma-separated numbers"
        if not nums:
            return "Error: no data"
        lo, hi = min(nums), max(nums)
        if lo == hi:
            return _SPARKS[3] * len(nums)
        spark = "".join(
            _SPARKS[int((v - lo) / (hi - lo) * (len(_SPARKS) - 1))]
            for v in nums
        )
        return spark

    @staticmethod
    def _pie_text(data: str) -> str:
        try:
            items = _parse_labeled(data)
        except ValueError:
            return "Error: data must be 'label:value,...'"
        if not items:
            return "Error: no data"
        total = sum(v for _, v in items)
        if total == 0:
            return "Error: all values are zero"
        lines: list[str] = [f"{'Label':<20} {'Value':>8} {'Pct':>6} {'Bar'}"]
        lines.append("-" * 50)
        for label, val in items:
            pct = val / total * 100
            bar = "█" * int(pct / 2)
            lines.append(f"{label:<20} {val:>8.2g} {pct:>5.1f}% {bar}")
        return "\n".join(lines)
