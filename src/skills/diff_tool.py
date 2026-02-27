"""Diff tool skill – compare two texts and show their differences."""

from __future__ import annotations

import difflib


class DiffToolSkill:
    """Compare two text strings and return a human-readable diff."""

    name = "diff_tool"
    description = (
        "Compare two texts and show their differences. "
        "Supported actions: 'unified' (unified diff), "
        "'side_by_side' (Differ-style), "
        "'ratio' (similarity ratio 0.0–1.0)."
    )

    def run(
        self,
        action: str = "unified",
        text_a: str = "",
        text_b: str = "",
        label_a: str = "text_a",
        label_b: str = "text_b",
        context_lines: int = 3,
    ) -> str:
        """
        Compare *text_a* and *text_b*.

        Parameters
        ----------
        action:
            One of ``"unified"``, ``"side_by_side"``, ``"ratio"``.
        text_a:
            First (original) text.
        text_b:
            Second (modified) text.
        label_a / label_b:
            Labels used in diff headers (default ``"text_a"`` / ``"text_b"``).
        context_lines:
            Number of context lines around each change (default 3).

        Returns
        -------
        str
            Diff output or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "unified":
            return self._unified(text_a, text_b, label_a, label_b, context_lines)
        if action == "side_by_side":
            return self._side_by_side(text_a, text_b, label_a, label_b)
        if action == "ratio":
            return self._ratio(text_a, text_b)
        return f"Error: unknown action {action!r}. Use unified, side_by_side, or ratio."

    # ------------------------------------------------------------------

    @staticmethod
    def _unified(
        text_a: str,
        text_b: str,
        label_a: str,
        label_b: str,
        context: int,
    ) -> str:
        lines_a = text_a.splitlines(keepends=True)
        lines_b = text_b.splitlines(keepends=True)
        diff = list(
            difflib.unified_diff(
                lines_a, lines_b, fromfile=label_a, tofile=label_b, n=context
            )
        )
        return "".join(diff) if diff else "(no differences)"

    @staticmethod
    def _side_by_side(
        text_a: str, text_b: str, label_a: str, label_b: str
    ) -> str:
        lines_a = text_a.splitlines()
        lines_b = text_b.splitlines()
        lines = list(difflib.Differ().compare(lines_a, lines_b))
        if not lines:
            return "(no differences)"
        header = f"{'--- ' + label_a:<40} {'=== ' + label_b}"
        return header + "\n" + "\n".join(lines)

    @staticmethod
    def _ratio(text_a: str, text_b: str) -> str:
        ratio = difflib.SequenceMatcher(None, text_a, text_b).ratio()
        return f"Similarity: {ratio:.4f} ({ratio * 100:.1f}%)"
