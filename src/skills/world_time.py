"""World time skill – get the current date/time in any IANA timezone.

Covers the "Calendar & Scheduling" and "Productivity & Tasks" categories.
Uses Python's stdlib ``zoneinfo`` module (Python ≥ 3.9) which ships with
every modern CPython installation.

Supported actions
-----------------
now             Return the current time in a given timezone.
convert         Convert a datetime string from one timezone to another.
list_zones      List all available IANA timezone identifiers.
offset          Return the UTC offset for a timezone.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones


_FMT = "%Y-%m-%d %H:%M:%S %Z%z"
_FMT_IN = "%Y-%m-%d %H:%M:%S"


class WorldTimeSkill:
    """Get the current time in any timezone or convert between timezones."""

    name = "world_time"
    description = (
        "World time and timezone utilities. "
        "Supported actions: 'now' (timezone); 'convert' (dt, from_tz, to_tz); "
        "'list_zones' (filter); 'offset' (timezone)."
    )

    def run(
        self,
        action: str,
        timezone: str = "UTC",
        dt: str = "",
        from_tz: str = "UTC",
        to_tz: str = "UTC",
        filter_str: str = "",
    ) -> str:
        """
        Perform a world-time operation.

        Parameters
        ----------
        action:
            One of ``"now"``, ``"convert"``, ``"list_zones"``,
            ``"offset"``.
        timezone:
            IANA timezone name for ``"now"`` and ``"offset"``
            (e.g. ``"America/New_York"``; default ``"UTC"``).
        dt:
            Datetime string in ``"YYYY-MM-DD HH:MM:SS"`` format for
            ``"convert"``.
        from_tz:
            Source timezone for ``"convert"`` (default ``"UTC"``).
        to_tz:
            Target timezone for ``"convert"`` (default ``"UTC"``).
        filter_str:
            Substring filter for ``"list_zones"`` (e.g. ``"Europe"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "now":
            return self._now(timezone)

        if action == "convert":
            return self._convert(dt, from_tz, to_tz)

        if action == "list_zones":
            return self._list_zones(filter_str)

        if action == "offset":
            return self._offset(timezone)

        return (
            f"Error: unknown action {action!r}. "
            "Use now, convert, list_zones, or offset."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_tz(tz_name: str) -> ZoneInfo | str:
        try:
            return ZoneInfo(tz_name)
        except (ZoneInfoNotFoundError, KeyError):
            return f"Error: unknown timezone {tz_name!r}"

    def _now(self, tz_name: str) -> str:
        tz = self._parse_tz(tz_name)
        if isinstance(tz, str):
            return tz
        now = datetime.now(tz=tz)
        return now.strftime(_FMT)

    def _convert(self, dt: str, from_tz_name: str, to_tz_name: str) -> str:
        if not dt:
            return "Error: dt is required for convert"
        from_tz = self._parse_tz(from_tz_name)
        if isinstance(from_tz, str):
            return from_tz
        to_tz = self._parse_tz(to_tz_name)
        if isinstance(to_tz, str):
            return to_tz
        try:
            parsed = datetime.strptime(dt.strip(), _FMT_IN)
        except ValueError:
            return f"Error: dt must be in 'YYYY-MM-DD HH:MM:SS' format"
        localized = parsed.replace(tzinfo=from_tz)
        converted = localized.astimezone(to_tz)
        return converted.strftime(_FMT)

    @staticmethod
    def _list_zones(filter_str: str) -> str:
        zones = sorted(available_timezones())
        if filter_str:
            zones = [z for z in zones if filter_str.lower() in z.lower()]
        if not zones:
            return f"(no timezones matching {filter_str!r})"
        return "\n".join(zones)

    def _offset(self, tz_name: str) -> str:
        tz = self._parse_tz(tz_name)
        if isinstance(tz, str):
            return tz
        now = datetime.now(tz=tz)
        offset = now.utcoffset()
        if offset is None:
            return f"{tz_name}: UTC+00:00"
        total_sec = int(offset.total_seconds())
        sign = "+" if total_sec >= 0 else "-"
        total_sec = abs(total_sec)
        hours, remainder = divmod(total_sec, 3600)
        minutes = remainder // 60
        return f"{tz_name}: UTC{sign}{hours:02d}:{minutes:02d}"
