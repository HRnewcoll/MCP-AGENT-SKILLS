"""Countdown skill – track countdowns to upcoming events.

Covers the "Calendar & Scheduling" and "Productivity & Tasks" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
add             Add a countdown event.
list            List all countdown events (sorted by proximity).
check           Get the time remaining for a specific event.
delete          Remove a countdown event.
next            Show the nearest upcoming event.
clear           Remove all events.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import TypedDict

_DATE_FMT = "%Y-%m-%d"


class _Event(TypedDict):
    id: int
    name: str
    target_date: str   # YYYY-MM-DD
    notes: str


class CountdownSkill:
    """Track countdowns to upcoming events and important dates."""

    name = "countdown"
    description = (
        "Track countdown timers to future events. "
        "Supported actions: 'add' (name, target_date, notes); "
        "'list'; 'check' (event_id); 'delete' (event_id); "
        "'next'; 'clear'."
        "\ntarget_date must be in YYYY-MM-DD format."
    )

    def __init__(self, store_path: str | os.PathLike = ".countdowns.json") -> None:
        self._path = Path(store_path)
        self._events: list[_Event] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        name: str = "",
        target_date: str = "",
        notes: str = "",
        event_id: int = 0,
    ) -> str:
        """
        Perform a countdown operation.

        Parameters
        ----------
        action:
            One of ``"add"``, ``"list"``, ``"check"``, ``"delete"``,
            ``"next"``, ``"clear"``.
        name:
            Event name (required for ``"add"``).
        target_date:
            Target date in ``"YYYY-MM-DD"`` format (required for ``"add"``).
        notes:
            Optional notes for the event.
        event_id:
            Numeric event ID (required for ``"check"`` and ``"delete"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "add":
            return self._add(name, target_date, notes)
        if action == "list":
            return self._list()
        if action == "check":
            return self._check(event_id)
        if action == "delete":
            return self._delete(event_id)
        if action == "next":
            return self._next()
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add, list, check, delete, next, or clear."
        )

    # ------------------------------------------------------------------

    def _add(self, name: str, target_date: str, notes: str) -> str:
        if not name:
            return "Error: name is required for add"
        if not target_date:
            return "Error: target_date is required for add"
        try:
            datetime.strptime(target_date, _DATE_FMT)
        except ValueError:
            return f"Error: target_date must be in YYYY-MM-DD format"
        event: _Event = {
            "id": self._next_id(),
            "name": name,
            "target_date": target_date,
            "notes": notes,
        }
        self._events.append(event)
        self._save()
        days = _days_remaining(target_date)
        return f"Added event #{event['id']}: {name!r} on {target_date} ({_format_days(days)})"

    def _list(self) -> str:
        if not self._events:
            return "(no countdown events)"
        today = date.today()
        sorted_events = sorted(
            self._events,
            key=lambda e: date.fromisoformat(e["target_date"])
        )
        lines = []
        for e in sorted_events:
            days = _days_remaining(e["target_date"])
            lines.append(f"#{e['id']} {e['name']}  [{e['target_date']}]  {_format_days(days)}")
        return "\n".join(lines)

    def _check(self, event_id: int) -> str:
        e = self._find(event_id)
        if e is None:
            return f"Error: event #{event_id} not found"
        days = _days_remaining(e["target_date"])
        notes_str = f"\nNotes: {e['notes']}" if e["notes"] else ""
        return (
            f"#{e['id']} {e['name']}\n"
            f"Date : {e['target_date']}\n"
            f"Time remaining: {_format_days(days)}"
            f"{notes_str}"
        )

    def _delete(self, event_id: int) -> str:
        if not event_id:
            return "Error: event_id is required for delete"
        e = self._find(event_id)
        if e is None:
            return f"Error: event #{event_id} not found"
        self._events.remove(e)
        self._save()
        return f"Deleted event #{event_id}"

    def _next(self) -> str:
        today = date.today()
        upcoming = [
            e for e in self._events
            if date.fromisoformat(e["target_date"]) >= today
        ]
        if not upcoming:
            return "(no upcoming events)"
        nearest = min(upcoming, key=lambda e: date.fromisoformat(e["target_date"]))
        days = _days_remaining(nearest["target_date"])
        return f"Next event: {nearest['name']}  [{nearest['target_date']}]  {_format_days(days)}"

    def _clear(self) -> str:
        count = len(self._events)
        self._events.clear()
        self._save()
        return f"Cleared {count} event(s)"

    def _find(self, event_id: int) -> _Event | None:
        return next((e for e in self._events if e["id"] == event_id), None)

    def _next_id(self) -> int:
        return max((e["id"] for e in self._events), default=0) + 1

    def _load(self) -> list[_Event]:
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
            json.dumps(self._events, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _days_remaining(target: str) -> int:
    return (date.fromisoformat(target) - date.today()).days


def _format_days(days: int) -> str:
    if days > 0:
        return f"in {days} day(s)"
    if days == 0:
        return "TODAY!"
    return f"{abs(days)} day(s) ago"
