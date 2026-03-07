"""Calendar skill – date arithmetic, calendar views, and scheduling helpers.

Covers the "Calendar & Scheduling" and "Productivity & Tasks" categories
from the awesome-openclaw-skills directory.  Uses Python stdlib only
(``calendar``, ``datetime``).

Supported actions
-----------------
days_between    Count calendar days between two dates.
add_days        Add/subtract days from a date.
month_calendar  Print a text calendar for a month.
day_of_week     Get the weekday name for a date.
is_leap_year    Check whether a year is a leap year.
next_weekday    Find the next occurrence of a given weekday.
weeks_in_year   Return the number of ISO weeks in a year.
quarter         Return the calendar quarter (1-4) for a date.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta

_DATE_FMT = "%Y-%m-%d"

_WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def _parse_date(s: str) -> "date | str":
    try:
        return datetime.strptime(s.strip(), _DATE_FMT).date()
    except ValueError:
        return f"Error: date {s!r} must be in YYYY-MM-DD format"


class CalendarSkill:
    """Date arithmetic, calendar views, and scheduling utilities."""

    name = "calendar_skill"
    description = (
        "Date arithmetic and calendar utilities. "
        "Supported actions: 'days_between' (date1, date2); "
        "'add_days' (date, days); 'month_calendar' (year, month); "
        "'day_of_week' (date); 'is_leap_year' (year); "
        "'next_weekday' (date, weekday); 'weeks_in_year' (year); "
        "'quarter' (date)."
        "\nDates must be in YYYY-MM-DD format."
    )

    def run(
        self,
        action: str,
        date: str = "",
        date1: str = "",
        date2: str = "",
        days: int = 0,
        year: int = 0,
        month: int = 0,
        weekday: str = "Monday",
    ) -> str:
        """
        Perform a calendar / date operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        date:
            A date string in ``"YYYY-MM-DD"`` format.
        date1 / date2:
            Two date strings for ``"days_between"``.
        days:
            Number of days to add (can be negative) for ``"add_days"``.
        year:
            4-digit year integer (for month_calendar / is_leap_year /
            weeks_in_year).
        month:
            Month integer 1-12 (for ``"month_calendar"``).
        weekday:
            Weekday name (Monday-Sunday) for ``"next_weekday"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "days_between":
            return self._days_between(date1, date2)
        if action == "add_days":
            return self._add_days(date, days)
        if action == "month_calendar":
            return self._month_calendar(year, month)
        if action == "day_of_week":
            return self._day_of_week(date)
        if action == "is_leap_year":
            return self._is_leap_year(year or (int(date[:4]) if date else 0))
        if action == "next_weekday":
            return self._next_weekday(date, weekday)
        if action == "weeks_in_year":
            return self._weeks_in_year(year or (int(date[:4]) if date else 0))
        if action == "quarter":
            return self._quarter(date)
        return (
            f"Error: unknown action {action!r}. "
            "Use days_between, add_days, month_calendar, day_of_week, "
            "is_leap_year, next_weekday, weeks_in_year, or quarter."
        )

    # ------------------------------------------------------------------
    # Implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _days_between(d1: str, d2: str) -> str:
        if not d1 or not d2:
            return "Error: date1 and date2 are required for days_between"
        a = _parse_date(d1)
        if isinstance(a, str):
            return a
        b = _parse_date(d2)
        if isinstance(b, str):
            return b
        delta = (b - a).days
        direction = "ahead" if delta > 0 else ("behind" if delta < 0 else "same day")
        return f"{abs(delta)} day(s) – {d2} is {direction} of {d1}"

    @staticmethod
    def _add_days(d: str, days: int) -> str:
        if not d:
            return "Error: date is required for add_days"
        parsed = _parse_date(d)
        if isinstance(parsed, str):
            return parsed
        result = parsed + timedelta(days=int(days))
        return result.strftime(_DATE_FMT)

    @staticmethod
    def _month_calendar(year: int, month: int) -> str:
        if not year or not month:
            return "Error: year and month are required for month_calendar"
        try:
            return calendar.month(int(year), int(month))
        except (ValueError, calendar.IllegalWeekdayError) as exc:
            return f"Error: {exc}"

    @staticmethod
    def _day_of_week(d: str) -> str:
        if not d:
            return "Error: date is required for day_of_week"
        parsed = _parse_date(d)
        if isinstance(parsed, str):
            return parsed
        return _WEEKDAY_NAMES[parsed.weekday()]

    @staticmethod
    def _is_leap_year(year: int) -> str:
        if not year:
            return "Error: year is required for is_leap_year"
        return f"{year} {'is' if calendar.isleap(int(year)) else 'is not'} a leap year"

    @staticmethod
    def _next_weekday(d: str, weekday: str) -> str:
        if not d:
            return "Error: date is required for next_weekday"
        parsed = _parse_date(d)
        if isinstance(parsed, str):
            return parsed
        try:
            target_wd = _WEEKDAY_NAMES.index(weekday.title())
        except ValueError:
            return f"Error: unknown weekday {weekday!r}. Use Monday-Sunday."
        days_ahead = target_wd - parsed.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        result = parsed + timedelta(days=days_ahead)
        return f"Next {weekday.title()} after {d}: {result.strftime(_DATE_FMT)}"

    @staticmethod
    def _weeks_in_year(year: int) -> str:
        if not year:
            return "Error: year is required for weeks_in_year"
        # ISO week: week 53 exists if Dec 31 is Thursday (or leap year and Thu/Fri)
        last_day = date(int(year), 12, 28)
        weeks = last_day.isocalendar()[1]
        return f"{year} has {weeks} ISO week(s)"

    @staticmethod
    def _quarter(d: str) -> str:
        if not d:
            return "Error: date is required for quarter"
        parsed = _parse_date(d)
        if isinstance(parsed, str):
            return parsed
        q = (parsed.month - 1) // 3 + 1
        return f"{d} is in Q{q} of {parsed.year}"
