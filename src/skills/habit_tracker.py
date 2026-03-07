"""Habit tracker skill – track daily habits with streaks and completion stats.

Covers the "Personal Development" and "Health & Fitness" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
add_habit       Create a new habit to track.
list_habits     Show all habits.
check_in        Mark a habit as done for today (or a given date).
uncheck         Remove today's check-in for a habit.
streak          Show current and longest streak for a habit.
stats           Show completion statistics for a habit.
delete_habit    Remove a habit and all its history.
clear           Remove all habits.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Habit(TypedDict):
    id: int
    name: str
    description: str
    created_at: str
    check_ins: list[str]   # ISO date strings "YYYY-MM-DD"


class HabitTrackerSkill:
    """Track daily habits with streaks and completion statistics."""

    name = "habit_tracker"
    description = (
        "Track daily habits. "
        "Supported actions: 'add_habit' (name, description); "
        "'list_habits'; 'check_in' (habit_id, date); "
        "'uncheck' (habit_id, date); 'streak' (habit_id); "
        "'stats' (habit_id); 'delete_habit' (habit_id); 'clear'."
        "\nDates default to today (YYYY-MM-DD format)."
    )

    def __init__(self, store_path: str | os.PathLike = ".habits.json") -> None:
        self._path = Path(store_path)
        self._habits: list[_Habit] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        name: str = "",
        description: str = "",
        habit_id: int = 0,
        date: str = "",
    ) -> str:
        """
        Perform a habit tracking operation.

        Parameters
        ----------
        action:
            One of ``"add_habit"``, ``"list_habits"``, ``"check_in"``,
            ``"uncheck"``, ``"streak"``, ``"stats"``,
            ``"delete_habit"``, ``"clear"``.
        name:
            Habit name (required for ``"add_habit"``).
        description:
            Optional description for the habit.
        habit_id:
            Numeric habit ID.
        date:
            Date string in ``"YYYY-MM-DD"`` format (defaults to today).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        today = _today()
        check_date = date.strip() if date.strip() else today

        if action == "add_habit":
            return self._add(name, description)
        if action == "list_habits":
            return self._list()
        if action == "check_in":
            return self._check_in(habit_id, check_date)
        if action == "uncheck":
            return self._uncheck(habit_id, check_date)
        if action == "streak":
            return self._streak(habit_id)
        if action == "stats":
            return self._stats(habit_id)
        if action == "delete_habit":
            return self._delete(habit_id)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add_habit, list_habits, check_in, uncheck, streak, "
            "stats, delete_habit, or clear."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add(self, name: str, description: str) -> str:
        if not name:
            return "Error: name is required for add_habit"
        habit: _Habit = {
            "id": self._next_id(),
            "name": name,
            "description": description,
            "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "check_ins": [],
        }
        self._habits.append(habit)
        self._save()
        return f"Added habit #{habit['id']}: {name!r}"

    def _list(self) -> str:
        if not self._habits:
            return "(no habits)"
        today = _today()
        lines = []
        for h in self._habits:
            done_today = "✓" if today in h["check_ins"] else "○"
            streak = self._calc_streak(h)
            lines.append(
                f"#{h['id']} {done_today} {h['name']}  "
                f"(streak: {streak['current']}d  best: {streak['longest']}d)"
            )
        return "\n".join(lines)

    def _check_in(self, habit_id: int, check_date: str) -> str:
        h = self._get(habit_id)
        if isinstance(h, str):
            return h
        if check_date in h["check_ins"]:
            return f"Already checked in for {check_date}"
        h["check_ins"].append(check_date)
        h["check_ins"].sort()
        self._save()
        return f"Checked in habit #{habit_id} ({h['name']!r}) for {check_date}"

    def _uncheck(self, habit_id: int, check_date: str) -> str:
        h = self._get(habit_id)
        if isinstance(h, str):
            return h
        if check_date not in h["check_ins"]:
            return f"No check-in found for {check_date}"
        h["check_ins"].remove(check_date)
        self._save()
        return f"Removed check-in for {check_date} from habit #{habit_id}"

    def _streak(self, habit_id: int) -> str:
        h = self._get(habit_id)
        if isinstance(h, str):
            return h
        s = self._calc_streak(h)
        return (
            f"Habit #{habit_id}: {h['name']!r}\n"
            f"Current streak : {s['current']} day(s)\n"
            f"Longest streak : {s['longest']} day(s)\n"
            f"Total check-ins: {len(h['check_ins'])}"
        )

    def _stats(self, habit_id: int) -> str:
        h = self._get(habit_id)
        if isinstance(h, str):
            return h
        if not h["check_ins"]:
            return f"Habit #{habit_id}: {h['name']!r}  — no check-ins yet"
        first = h["check_ins"][0]
        last  = h["check_ins"][-1]
        from datetime import timedelta
        first_d = date.fromisoformat(first)
        last_d  = date.fromisoformat(last)
        total_days = (last_d - first_d).days + 1
        completion = len(h["check_ins"]) / total_days * 100 if total_days > 0 else 100
        s = self._calc_streak(h)
        return (
            f"Habit #{habit_id}: {h['name']!r}\n"
            f"First check-in : {first}\n"
            f"Last check-in  : {last}\n"
            f"Total check-ins: {len(h['check_ins'])}\n"
            f"Days tracked   : {total_days}\n"
            f"Completion rate: {completion:.1f}%\n"
            f"Current streak : {s['current']} day(s)\n"
            f"Longest streak : {s['longest']} day(s)"
        )

    def _delete(self, habit_id: int) -> str:
        h = self._get(habit_id)
        if isinstance(h, str):
            return h
        self._habits.remove(h)
        self._save()
        return f"Deleted habit #{habit_id}"

    def _clear(self) -> str:
        count = len(self._habits)
        self._habits.clear()
        self._save()
        return f"Cleared {count} habit(s)"

    def _get(self, habit_id: int) -> "_Habit | str":
        if not habit_id:
            return "Error: habit_id is required"
        h = next((h for h in self._habits if h["id"] == habit_id), None)
        if h is None:
            return f"Error: habit #{habit_id} not found"
        return h

    @staticmethod
    def _calc_streak(h: _Habit) -> dict[str, int]:
        if not h["check_ins"]:
            return {"current": 0, "longest": 0}
        from datetime import timedelta
        dates = sorted(date.fromisoformat(d) for d in h["check_ins"])
        today = date.fromisoformat(_today())
        current = 0
        check = today
        while check in set(dates):
            current += 1
            check -= timedelta(days=1)
        # Longest streak
        longest = 0
        run = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                run += 1
                longest = max(longest, run)
            else:
                run = 1
        longest = max(longest, run, current)
        return {"current": current, "longest": longest}

    def _next_id(self) -> int:
        return max((h["id"] for h in self._habits), default=0) + 1

    def _load(self) -> list[_Habit]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._habits, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _today() -> str:
    return date.today().isoformat()
