"""Datetime skill – work with dates, times and durations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


class DatetimeSkill:
    """Perform date and time operations."""

    name = "datetime"
    description = (
        "Work with dates and times. "
        "Supported actions: 'now' (current UTC time), 'format' (reformat a date string), "
        "'diff' (difference between two dates), 'add' (add duration to a date), "
        "'parse' (parse a date string to ISO-8601)."
    )

    _ISO_FMT = "%Y-%m-%dT%H:%M:%S"

    def run(
        self,
        action: str,
        date: str = "",
        date2: str = "",
        fmt: str = "%Y-%m-%d %H:%M:%S",
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
    ) -> str:
        """
        Perform a datetime operation.

        Parameters
        ----------
        action:
            One of ``"now"``, ``"format"``, ``"diff"``, ``"add"``, ``"parse"``.
        date:
            ISO-8601 date/datetime string (required for format, diff, add, parse).
        date2:
            Second ISO-8601 date string (required for diff).
        fmt:
            strftime format string used by 'now' and 'format' (default: ``"%Y-%m-%d %H:%M:%S"``).
        days, hours, minutes:
            Duration offsets for the 'add' action.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "now":
            return self._now(fmt)
        if action == "format":
            return self._format_date(date, fmt)
        if action == "diff":
            return self._diff(date, date2)
        if action == "add":
            return self._add(date, days, hours, minutes, fmt)
        if action == "parse":
            return self._parse(date)
        return f"Error: unknown action {action!r}. Use now, format, diff, add, or parse."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now(fmt: str) -> str:
        try:
            return datetime.now(tz=timezone.utc).strftime(fmt) + " UTC"
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _parse_dt(s: str) -> datetime | None:
        """Try to parse a date string in several common formats."""
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ):
            try:
                return datetime.strptime(s.strip(), fmt)
            except ValueError:
                continue
        return None

    def _format_date(self, date: str, fmt: str) -> str:
        if not date:
            return "Error: date is required for format"
        dt = self._parse_dt(date)
        if dt is None:
            return f"Error: could not parse date {date!r}"
        try:
            return dt.strftime(fmt)
        except Exception as exc:
            return f"Error: {exc}"

    def _diff(self, date: str, date2: str) -> str:
        if not date or not date2:
            return "Error: both date and date2 are required for diff"
        dt1 = self._parse_dt(date)
        dt2 = self._parse_dt(date2)
        if dt1 is None:
            return f"Error: could not parse date {date!r}"
        if dt2 is None:
            return f"Error: could not parse date2 {date2!r}"
        delta = abs(dt2 - dt1)
        total_seconds = int(delta.total_seconds())
        days = delta.days
        hours, rem = divmod(total_seconds % 86400, 3600)
        mins, secs = divmod(rem, 60)
        return f"{days} days, {hours} hours, {mins} minutes, {secs} seconds"

    def _add(self, date: str, days: int, hours: int, minutes: int, fmt: str) -> str:
        if not date:
            return "Error: date is required for add"
        dt = self._parse_dt(date)
        if dt is None:
            return f"Error: could not parse date {date!r}"
        try:
            result = dt + timedelta(days=days, hours=hours, minutes=minutes)
            return result.strftime(fmt)
        except Exception as exc:
            return f"Error: {exc}"

    def _parse(self, date: str) -> str:
        if not date:
            return "Error: date is required for parse"
        dt = self._parse_dt(date)
        if dt is None:
            return f"Error: could not parse date {date!r}"
        return dt.strftime(self._ISO_FMT)
