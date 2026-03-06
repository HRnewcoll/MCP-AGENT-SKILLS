"""Workout tracker skill – log and review exercise sessions.

Covers the "Health & Fitness" category from the awesome-openclaw-skills
directory.  All data persisted to a local JSON file.

Supported actions
-----------------
log             Log a workout session.
list            List all sessions (most recent first).
stats           Show overall fitness stats.
personal_best   Find the personal best for a specific exercise.
by_type         List sessions of a specific workout type.
delete          Delete a session by ID.
clear           Delete all sessions.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Session(TypedDict):
    id: int
    workout_type: str
    exercise: str
    sets: int
    reps: int
    weight: float
    duration_minutes: float
    notes: str
    date: str


class WorkoutTrackerSkill:
    """Log and review exercise / workout sessions."""

    name = "workout_tracker"
    description = (
        "Track workout and exercise sessions. "
        "Supported actions: 'log' (workout_type, exercise, sets, reps, weight, "
        "duration_minutes, notes, date); 'list'; "
        "'stats'; 'personal_best' (exercise); "
        "'by_type' (workout_type); 'delete' (session_id); 'clear'."
        "\ndate defaults to today (YYYY-MM-DD)."
    )

    def __init__(self, store_path: str | os.PathLike = ".workouts.json") -> None:
        self._path = Path(store_path)
        self._sessions: list[_Session] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        workout_type: str = "",
        exercise: str = "",
        sets: int = 0,
        reps: int = 0,
        weight: float = 0.0,
        duration_minutes: float = 0.0,
        notes: str = "",
        date: str = "",
        session_id: int = 0,
    ) -> str:
        """
        Perform a workout tracking operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        workout_type:
            Type of workout (e.g. ``"strength"``, ``"cardio"``,
            ``"yoga"``).
        exercise:
            Specific exercise name (e.g. ``"bench press"``).
        sets / reps / weight:
            Exercise metrics (0 if not applicable).
        duration_minutes:
            Session duration in minutes.
        notes:
            Optional free-text notes.
        date:
            Date in ``"YYYY-MM-DD"`` format (default today).
        session_id:
            Numeric session ID for ``"delete"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        session_date = date.strip() if date.strip() else _today()

        if action == "log":
            return self._log(
                workout_type, exercise, sets, reps,
                weight, duration_minutes, notes, session_date
            )
        if action == "list":
            return self._list()
        if action == "stats":
            return self._stats()
        if action == "personal_best":
            return self._personal_best(exercise)
        if action == "by_type":
            return self._by_type(workout_type)
        if action == "delete":
            return self._delete(session_id)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use log, list, stats, personal_best, by_type, delete, or clear."
        )

    # ------------------------------------------------------------------

    def _log(
        self,
        workout_type: str,
        exercise: str,
        sets: int,
        reps: int,
        weight: float,
        duration_minutes: float,
        notes: str,
        session_date: str,
    ) -> str:
        if not workout_type and not exercise:
            return "Error: workout_type or exercise is required for log"
        session: _Session = {
            "id": self._next_id(),
            "workout_type": workout_type or "general",
            "exercise": exercise,
            "sets": int(sets),
            "reps": int(reps),
            "weight": float(weight),
            "duration_minutes": float(duration_minutes),
            "notes": notes,
            "date": session_date,
        }
        self._sessions.append(session)
        self._save()
        parts = [f"#{session['id']} {session['workout_type']}"]
        if exercise:
            parts.append(exercise)
        if sets and reps:
            parts.append(f"{sets}×{reps}")
        if weight:
            parts.append(f"@ {weight}kg")
        if duration_minutes:
            parts.append(f"{duration_minutes}min")
        return "Logged: " + "  ".join(parts) + f"  [{session_date}]"

    def _list(self) -> str:
        if not self._sessions:
            return "(no workout sessions)"
        lines = []
        for s in sorted(self._sessions, key=lambda x: x["date"], reverse=True):
            detail = ""
            if s["sets"] and s["reps"]:
                detail += f"  {s['sets']}×{s['reps']}"
            if s["weight"]:
                detail += f" @{s['weight']}kg"
            if s["duration_minutes"]:
                detail += f"  {s['duration_minutes']}min"
            ex = f" – {s['exercise']}" if s["exercise"] else ""
            lines.append(f"#{s['id']} [{s['date']}] {s['workout_type']}{ex}{detail}")
        return "\n".join(lines)

    def _stats(self) -> str:
        if not self._sessions:
            return "(no workout sessions)"
        total = len(self._sessions)
        total_min = sum(s["duration_minutes"] for s in self._sessions)
        types: dict[str, int] = {}
        for s in self._sessions:
            types[s["workout_type"]] = types.get(s["workout_type"], 0) + 1
        most_common = max(types, key=lambda k: types[k]) if types else "N/A"
        return (
            f"Total sessions    : {total}\n"
            f"Total time        : {total_min:.0f} minutes\n"
            f"Most common type  : {most_common} ({types.get(most_common, 0)}x)"
        )

    def _personal_best(self, exercise: str) -> str:
        if not exercise:
            return "Error: exercise is required for personal_best"
        ex_lower = exercise.lower()
        matching = [s for s in self._sessions if s["exercise"].lower() == ex_lower]
        if not matching:
            return f"No sessions found for exercise {exercise!r}"
        best_weight = max((s["weight"] for s in matching), default=0)
        best_reps = max((s["reps"] for s in matching), default=0)
        return (
            f"Personal best for '{exercise}':\n"
            f"  Max weight: {best_weight} kg\n"
            f"  Max reps  : {best_reps}"
        )

    def _by_type(self, workout_type: str) -> str:
        if not workout_type:
            return "Error: workout_type is required for by_type"
        matching = [
            s for s in self._sessions
            if s["workout_type"].lower() == workout_type.lower()
        ]
        if not matching:
            return f"No sessions of type {workout_type!r}"
        lines = [f"{len(matching)} session(s) of type '{workout_type}':"]
        for s in sorted(matching, key=lambda x: x["date"], reverse=True):
            ex = f" – {s['exercise']}" if s["exercise"] else ""
            lines.append(f"  #{s['id']} [{s['date']}]{ex}")
        return "\n".join(lines)

    def _delete(self, session_id: int) -> str:
        if not session_id:
            return "Error: session_id is required for delete"
        s = next((x for x in self._sessions if x["id"] == session_id), None)
        if s is None:
            return f"Error: session #{session_id} not found"
        self._sessions.remove(s)
        self._save()
        return f"Deleted session #{session_id}"

    def _clear(self) -> str:
        count = len(self._sessions)
        self._sessions.clear()
        self._save()
        return f"Cleared {count} session(s)"

    def _next_id(self) -> int:
        return max((s["id"] for s in self._sessions), default=0) + 1

    def _load(self) -> list[_Session]:
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
            json.dumps(self._sessions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _today() -> str:
    from datetime import date
    return date.today().isoformat()
