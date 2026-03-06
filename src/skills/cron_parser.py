"""Cron parser skill – parse and explain cron job expressions.

Covers the "DevOps & Cloud" category from the awesome-openclaw-skills
directory.  Pure Python, no external libraries.

A cron expression has 5 fields: minute hour day-of-month month day-of-week.

Supported actions
-----------------
describe        Explain a cron expression in plain English.
next_times      List the next N matching times from now (or a given start).
validate        Check if a cron expression is syntactically valid.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

_MINUTE  = (0, 59)
_HOUR    = (0, 23)
_DOM     = (1, 31)
_MONTH   = (1, 12)
_DOW     = (0, 6)

_MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_DOW_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}
_MONTH_LABELS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
_DOW_LABELS = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
]


def _normalize_word(field: str, mapping: dict[str, int]) -> str:
    for name, num in mapping.items():
        field = re.sub(r"(?i)\b" + name + r"\b", str(num), field)
    return field


def _parse_field(field: str, lo: int, hi: int) -> list[int]:
    """Return a sorted list of matching integers for a cron field."""
    if field == "*":
        return list(range(lo, hi + 1))
    result: set[int] = set()
    for part in field.split(","):
        if part == "*":
            result.update(range(lo, hi + 1))
        elif re.match(r"^\*/(\d+)$", part):
            step = int(part.split("/")[1])
            if step == 0:
                raise ValueError(f"Step of 0 is invalid in {part!r}")
            result.update(range(lo, hi + 1, step))
        elif re.match(r"^(\d+)-(\d+)(/(\d+))?$", part):
            m = re.match(r"^(\d+)-(\d+)(/(\d+))?$", part)
            start, end = int(m.group(1)), int(m.group(2))
            step = int(m.group(4)) if m.group(4) else 1
            result.update(range(start, end + 1, step))
        elif re.match(r"^\d+$", part):
            result.add(int(part))
        else:
            raise ValueError(f"Invalid cron field segment: {part!r}")
    return sorted(v for v in result if lo <= v <= hi)


def _parse_cron(expr: str) -> tuple[list[int], list[int], list[int], list[int], list[int]]:
    parts = expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Cron expression must have exactly 5 fields, got {len(parts)}")
    minute_f, hour_f, dom_f, month_f, dow_f = parts
    month_f = _normalize_word(month_f, _MONTH_NAMES)
    dow_f   = _normalize_word(dow_f, _DOW_NAMES)
    minutes = _parse_field(minute_f, *_MINUTE)
    hours   = _parse_field(hour_f,   *_HOUR)
    doms    = _parse_field(dom_f,    *_DOM)
    months  = _parse_field(month_f,  *_MONTH)
    dows    = _parse_field(dow_f,    *_DOW)
    return minutes, hours, doms, months, dows


def _describe_field(field: str, lo: int, hi: int, labels: list[str] | None = None) -> str:
    if field.strip() == "*":
        return "every value"
    values = _parse_field(field, lo, hi)
    if labels:
        named = [labels[v] for v in values if 0 <= v < len(labels)]
        return ", ".join(named) if named else ", ".join(str(v) for v in values)
    return ", ".join(str(v) for v in values)


class CronParserSkill:
    """Parse, validate, and explain cron job expressions."""

    name = "cron_parser"
    description = (
        "Parse and explain 5-field cron expressions (min hour dom month dow). "
        "Supported actions: 'describe' (expression); "
        "'validate' (expression); 'next_times' (expression, count=5)."
    )

    def run(
        self,
        action: str,
        expression: str = "",
        count: int = 5,
    ) -> str:
        """
        Perform a cron operation.

        Parameters
        ----------
        action:
            One of ``"describe"``, ``"validate"``, ``"next_times"``.
        expression:
            A 5-field cron expression, e.g. ``"0 9 * * 1-5"``.
        count:
            Number of upcoming times to show for ``"next_times"``
            (default 5, max 20).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if not expression:
            return "Error: expression is required"

        if action == "validate":
            return self._validate(expression)
        if action == "describe":
            return self._describe(expression)
        if action == "next_times":
            return self._next_times(expression, count)
        return (
            f"Error: unknown action {action!r}. "
            "Use describe, validate, or next_times."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _validate(expression: str) -> str:
        try:
            _parse_cron(expression)
            return f"{expression!r} is a valid cron expression"
        except ValueError as exc:
            return f"Error: {exc}"

    @staticmethod
    def _describe(expression: str) -> str:
        try:
            parts = expression.strip().split()
            if len(parts) != 5:
                return f"Error: expected 5 fields, got {len(parts)}"
            minute_f, hour_f, dom_f, month_f, dow_f = parts
            month_f_n = _normalize_word(month_f, _MONTH_NAMES)
            dow_f_n   = _normalize_word(dow_f,   _DOW_NAMES)

            minute_desc = _describe_field(minute_f, *_MINUTE)
            hour_desc   = _describe_field(hour_f,   *_HOUR)
            dom_desc    = _describe_field(dom_f,    *_DOM)
            month_desc  = _describe_field(month_f_n,*_MONTH, _MONTH_LABELS)
            dow_desc    = _describe_field(dow_f_n,  *_DOW,   _DOW_LABELS)

            return (
                f"Expression : {expression}\n"
                f"Minute     : {minute_desc}\n"
                f"Hour       : {hour_desc}\n"
                f"Day/month  : {dom_desc}\n"
                f"Month      : {month_desc}\n"
                f"Day/week   : {dow_desc}"
            )
        except ValueError as exc:
            return f"Error: {exc}"

    @staticmethod
    def _next_times(expression: str, count: int) -> str:
        try:
            minutes, hours, doms, months, dows = _parse_cron(expression)
        except ValueError as exc:
            return f"Error: {exc}"

        count = max(1, min(20, int(count)))
        now = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
        # Advance by one minute so we find *next* times
        from datetime import timedelta
        current = now + timedelta(minutes=1)
        results: list[str] = []
        limit = 0
        while len(results) < count and limit < 527040:  # max ~1 year
            limit += 1
            if (current.month in months
                    and current.day in doms
                    and current.hour in hours
                    and current.minute in minutes
                    and current.weekday() in [d if d != 0 else 0 for d in dows]
                    or (current.month in months
                        and current.day in doms
                        and current.hour in hours
                        and current.minute in minutes
                        and (current.isoweekday() % 7) in dows)):
                results.append(current.strftime("%Y-%m-%d %H:%M UTC"))
            current += timedelta(minutes=1)

        if not results:
            return "(no upcoming matches found within 1 year)"
        return "\n".join(results)
