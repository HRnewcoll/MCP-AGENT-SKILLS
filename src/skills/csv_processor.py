"""CSV processor skill – read, write, filter, and convert CSV data.

Covers the "Data & Analytics" category from the awesome-openclaw-skills
directory.  Uses Python stdlib only (``csv``, ``json``).

Supported actions
-----------------
load            Read a CSV file into memory and return a summary.
read_file       Alias for load.
get_rows        Return all rows (optionally filtered by column=value).
get_row         Return a single row by index (0-based).
add_row         Append a new row (values as comma-separated string).
delete_row      Remove a row by index.
list_columns    Return the header column names.
sort            Sort rows by a column name (ascending).
to_json         Convert loaded CSV to JSON array string.
from_csv_string Parse a raw CSV string and return JSON.
write           Write current data back to a file.
"""

from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path


class CsvProcessorSkill:
    """Read, write, filter, and convert CSV data."""

    name = "csv_processor"
    description = (
        "Process CSV files and data. "
        "Supported actions: 'load' (path=<file>); 'get_rows' (column, value); "
        "'get_row' (row_index); 'add_row' (values=<csv string>); "
        "'delete_row' (row_index); 'list_columns'; 'sort' (column); "
        "'to_json'; 'from_csv_string' (text); 'write' (path=<file>)."
    )

    def __init__(self) -> None:
        self._headers: list[str] = []
        self._rows: list[dict[str, str]] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        path: str = "",
        column: str = "",
        value: str = "",
        row_index: int = 0,
        values: str = "",
        text: str = "",
    ) -> str:
        """
        Perform a CSV operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        path:
            File path for ``"load"`` and ``"write"``.
        column:
            Column name for ``"get_rows"`` and ``"sort"``.
        value:
            Filter value for ``"get_rows"``.
        row_index:
            Zero-based row index for ``"get_row"`` and ``"delete_row"``.
        values:
            Comma-separated field values for ``"add_row"``.
        text:
            Raw CSV text for ``"from_csv_string"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action in ("load", "read_file"):
            return self._load(path)
        if action == "get_rows":
            return self._get_rows(column, value)
        if action == "get_row":
            return self._get_row(row_index)
        if action == "add_row":
            return self._add_row(values)
        if action == "delete_row":
            return self._delete_row(row_index)
        if action == "list_columns":
            return self._list_columns()
        if action == "sort":
            return self._sort(column)
        if action == "to_json":
            return self._to_json()
        if action == "from_csv_string":
            return self._from_csv_string(text)
        if action == "write":
            return self._write(path)
        return (
            f"Error: unknown action {action!r}. "
            "Use load, get_rows, get_row, add_row, delete_row, "
            "list_columns, sort, to_json, from_csv_string, or write."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self, path: str) -> str:
        if not path:
            return "Error: path is required for load"
        p = Path(path)
        if not p.exists():
            return f"Error: file {path!r} not found"
        try:
            text = p.read_text(encoding="utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            self._headers = list(reader.fieldnames or [])
            self._rows = [dict(row) for row in reader]
            return (
                f"Loaded {len(self._rows)} row(s) with "
                f"{len(self._headers)} column(s): {', '.join(self._headers)}"
            )
        except Exception as exc:
            return f"Error: {exc}"

    def _get_rows(self, column: str, value: str) -> str:
        if not self._headers:
            return "Error: no data loaded – use load first"
        if column and column not in self._headers:
            return f"Error: column {column!r} not found"
        rows = (
            [r for r in self._rows if r.get(column, "") == value]
            if column
            else self._rows
        )
        if not rows:
            return "(no matching rows)"
        return _format_rows(self._headers, rows)

    def _get_row(self, row_index: int) -> str:
        if not self._rows:
            return "Error: no data loaded – use load first"
        if row_index < 0 or row_index >= len(self._rows):
            return f"Error: row index {row_index} out of range (0-{len(self._rows)-1})"
        row = self._rows[row_index]
        lines = [f"Row {row_index}:"]
        for k, v in row.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    def _add_row(self, values: str) -> str:
        if not self._headers:
            return "Error: no data loaded – use load first"
        parts = list(csv.reader([values]))[0] if values else []
        if len(parts) != len(self._headers):
            return (
                f"Error: expected {len(self._headers)} value(s) "
                f"({', '.join(self._headers)}), got {len(parts)}"
            )
        row = dict(zip(self._headers, parts))
        self._rows.append(row)
        return f"Added row {len(self._rows) - 1}"

    def _delete_row(self, row_index: int) -> str:
        if not self._rows:
            return "Error: no data loaded"
        if row_index < 0 or row_index >= len(self._rows):
            return f"Error: row index {row_index} out of range"
        self._rows.pop(row_index)
        return f"Deleted row {row_index}"

    def _list_columns(self) -> str:
        if not self._headers:
            return "Error: no data loaded"
        return "Columns: " + ", ".join(self._headers)

    def _sort(self, column: str) -> str:
        if not self._rows:
            return "Error: no data loaded"
        if not column:
            return "Error: column is required for sort"
        if column not in self._headers:
            return f"Error: column {column!r} not found"
        self._rows.sort(key=lambda r: r.get(column, ""))
        return f"Sorted {len(self._rows)} row(s) by {column!r}"

    def _to_json(self) -> str:
        if not self._rows:
            return "[]"
        return json.dumps(self._rows, ensure_ascii=False, indent=2)

    def _from_csv_string(self, text: str) -> str:
        if not text:
            return "Error: text is required"
        try:
            reader = csv.DictReader(io.StringIO(text))
            self._headers = list(reader.fieldnames or [])
            self._rows = [dict(row) for row in reader]
            result = json.dumps(self._rows, ensure_ascii=False, indent=2)
            return result
        except Exception as exc:
            return f"Error: {exc}"

    def _write(self, path: str) -> str:
        if not path:
            return "Error: path is required for write"
        if not self._headers:
            return "Error: no data loaded"
        try:
            p = Path(path)
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=self._headers)
            writer.writeheader()
            writer.writerows(self._rows)
            p.write_text(buf.getvalue(), encoding="utf-8")
            return f"Wrote {len(self._rows)} row(s) to {path!r}"
        except Exception as exc:
            return f"Error: {exc}"


def _format_rows(headers: list[str], rows: list[dict[str, str]]) -> str:
    widths = {h: max(len(h), max((len(r.get(h, "")) for r in rows), default=0)) for h in headers}
    sep = "+" + "+".join("-" * (w + 2) for w in widths.values()) + "+"
    header_row = "|" + "|".join(f" {h:<{widths[h]}} " for h in headers) + "|"
    lines = [sep, header_row, sep]
    for row in rows:
        lines.append("|" + "|".join(f" {row.get(h, ''):<{widths[h]}} " for h in headers) + "|")
    lines.append(sep)
    return "\n".join(lines)
