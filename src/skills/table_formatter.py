"""Table formatter skill – format data as ASCII/markdown/CSV tables.

Covers the "Data & Analytics" and "CLI Utilities" categories.
Pure Python, no external libraries.

Supported actions
-----------------
ascii           Render data as a bordered ASCII table.
markdown        Render data as a Markdown table.
csv_to_table    Convert CSV text to an ASCII table.
json_to_table   Convert a JSON array-of-objects to a table.
transpose       Transpose rows and columns of a table.
"""

from __future__ import annotations

import csv
import io
import json


def _parse_rows(data: str) -> tuple[list[str], list[list[str]]]:
    """
    Parse 'header1,header2;row1col1,row1col2;...' format.
    First row is treated as headers.
    """
    rows = []
    for row_str in data.split(";"):
        row_str = row_str.strip()
        if row_str:
            rows.append([c.strip() for c in row_str.split(",")])
    if not rows:
        return [], []
    return rows[0], rows[1:]


class TableFormatterSkill:
    """Format tabular data as ASCII, Markdown, or convert from CSV/JSON."""

    name = "table_formatter"
    description = (
        "Format data as tables. "
        "Supported actions: 'ascii' (data – 'h1,h2;r1c1,r1c2;r2c1,r2c2'); "
        "'markdown' (data – same format); "
        "'csv_to_table' (data – CSV text); "
        "'json_to_table' (data – JSON array of objects); "
        "'transpose' (data – same format as ascii)."
    )

    def run(self, action: str, data: str = "") -> str:
        """
        Format a table.

        Parameters
        ----------
        action:
            One of ``"ascii"``, ``"markdown"``, ``"csv_to_table"``,
            ``"json_to_table"``, ``"transpose"``.
        data:
            Input data (format depends on action; see description).

        Returns
        -------
        str
            Formatted table or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if not data:
            return "Error: data is required"

        try:
            if action == "ascii":
                return self._ascii(data)
            if action == "markdown":
                return self._markdown(data)
            if action == "csv_to_table":
                return self._csv_to_table(data)
            if action == "json_to_table":
                return self._json_to_table(data)
            if action == "transpose":
                return self._transpose(data)
        except (ValueError, json.JSONDecodeError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use ascii, markdown, csv_to_table, json_to_table, or transpose."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _render_ascii(headers: list[str], rows: list[list[str]]) -> str:
        all_rows = [headers] + rows
        n_cols = max(len(r) for r in all_rows)
        # Pad rows
        padded = [r + [""] * (n_cols - len(r)) for r in all_rows]
        widths = [max(len(str(row[c])) for row in padded) for c in range(n_cols)]
        sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        def fmt_row(row: list[str]) -> str:
            return "|" + "|".join(f" {str(row[c]):<{widths[c]}} " for c in range(n_cols)) + "|"
        lines = [sep, fmt_row(padded[0]), sep]
        for row in padded[1:]:
            lines.append(fmt_row(row))
        lines.append(sep)
        return "\n".join(lines)

    def _ascii(self, data: str) -> str:
        headers, rows = _parse_rows(data)
        if not headers:
            return "Error: no data"
        return self._render_ascii(headers, rows)

    @staticmethod
    def _render_markdown(headers: list[str], rows: list[list[str]]) -> str:
        n_cols = max(len(headers), max((len(r) for r in rows), default=0))
        padded_headers = headers + [""] * (n_cols - len(headers))
        widths = [max(len(str(h)), max((len(str(r[c])) if c < len(r) else 0 for r in rows), default=0))
                  for c, h in enumerate(padded_headers)]
        def fmt_row(row: list[str]) -> str:
            padded = row + [""] * (n_cols - len(row))
            return "| " + " | ".join(f"{str(padded[c]):<{widths[c]}}" for c in range(n_cols)) + " |"
        sep = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
        lines = [fmt_row(padded_headers), sep]
        for row in rows:
            lines.append(fmt_row(row))
        return "\n".join(lines)

    def _markdown(self, data: str) -> str:
        headers, rows = _parse_rows(data)
        if not headers:
            return "Error: no data"
        return self._render_markdown(headers, rows)

    def _csv_to_table(self, data: str) -> str:
        reader = csv.reader(io.StringIO(data))
        all_rows = [row for row in reader if row]
        if not all_rows:
            return "Error: no CSV data"
        return self._render_ascii(all_rows[0], all_rows[1:])

    @staticmethod
    def _json_to_table(data: str) -> str:
        parsed = json.loads(data)
        if not isinstance(parsed, list) or not parsed:
            return "Error: expected a non-empty JSON array of objects"
        if not isinstance(parsed[0], dict):
            return "Error: each item must be a JSON object"
        headers = list(parsed[0].keys())
        rows = [[str(item.get(h, "")) for h in headers] for item in parsed]
        widths = [max(len(h), max(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
        sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        def fmt(row: list[str]) -> str:
            return "|" + "|".join(f" {row[i]:<{widths[i]}} " for i in range(len(headers))) + "|"
        lines = [sep, fmt(headers), sep]
        for row in rows:
            lines.append(fmt(row))
        lines.append(sep)
        return "\n".join(lines)

    def _transpose(self, data: str) -> str:
        headers, rows = _parse_rows(data)
        if not headers:
            return "Error: no data"
        all_rows = [headers] + rows
        n_cols = max(len(r) for r in all_rows)
        padded = [r + [""] * (n_cols - len(r)) for r in all_rows]
        transposed = [[padded[r][c] for r in range(len(padded))] for c in range(n_cols)]
        return self._render_ascii(transposed[0], transposed[1:])
