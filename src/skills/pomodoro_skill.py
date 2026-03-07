"""Pomodoro skill – track Pomodoro focus sessions locally.

Covers the "Productivity & Tasks" category from the
awesome-openclaw-skills directory.  All session data stored locally
as JSON – no external APIs or timers required (humans/agents report
session start/end manually).

Supported actions
-----------------
start_session   Record the start of a Pomodoro session.
end_session     Record the end of a session and compute duration.
list_sessions   List recorded sessions.
stats           Show productivity statistics.
clear           Remove all session records.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

_FMT = "%Y-%m-%dT%H:%M:%SZ"


class _Session(TypedDict, total=False):
    id: int
    task: str
    started_at: str
    ended_at: str
    duration_minutes: float
    completed: bool


class PomodoroSkill:
    """Track Pomodoro focus sessions (25-min blocks) locally."""

    name = "pomodoro"
    description = (
        "Track Pomodoro productivity sessions. "
        "Supported actions: 'start_session' (task); "
        "'end_session' (session_id); 'list_sessions'; "
        "'stats'; 'clear'."
    )

    def __init__(self, store_path: str | os.PathLike = ".pomodoro.json") -> None:
        self._path = Path(store_path)
        self._sessions: list[_Session] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        task: str = "",
        session_id: int = 0,
    ) -> str:
        """
        Perform a Pomodoro operation.

        Parameters
        ----------
        action:
            One of ``"start_session"``, ``"end_session"``,
            ``"list_sessions"``, ``"stats"``, ``"clear"``.
        task:
            Task description for ``"start_session"``.
        session_id:
            Numeric session ID for ``"end_session"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "start_session":
            return self._start(task)
        if action == "end_session":
            return self._end(session_id)
        if action == "list_sessions":
            return self._list()
        if action == "stats":
            return self._stats()
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use start_session, end_session, list_sessions, stats, or clear."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _start(self, task: str) -> str:
        if not task:
            return "Error: task is required for start_session"
        # Warn if there is already an open session
        open_sessions = [s for s in self._sessions if not s.get("completed")]
        session: _Session = {
            "id": self._next_id(),
            "task": task,
            "started_at": _now(),
            "ended_at": "",
            "duration_minutes": 0.0,
            "completed": False,
        }
        self._sessions.append(session)
        self._save()
        msg = f"Session #{session['id']} started: {task!r}"
        if open_sessions:
            msg += f"\n(Note: {len(open_sessions)} other open session(s) already active)"
        return msg

    def _end(self, session_id: int) -> str:
        if not session_id:
            return "Error: session_id is required for end_session"
        session = next((s for s in self._sessions if s["id"] == session_id), None)
        if session is None:
            return f"Error: session #{session_id} not found"
        if session.get("completed"):
            return f"Error: session #{session_id} is already completed"
        now = _now()
        session["ended_at"] = now
        start = datetime.strptime(session["started_at"], _FMT)
        end = datetime.strptime(now, _FMT)
        duration = (end - start).total_seconds() / 60.0
        session["duration_minutes"] = round(duration, 1)
        session["completed"] = True
        self._save()
        return (
            f"Session #{session_id} completed: {session['task']!r}\n"
            f"Duration: {duration:.1f} minute(s)"
        )

    def _list(self) -> str:
        if not self._sessions:
            return "(no sessions recorded)"
        lines = ["ID  Task                       Started              Duration   Done"]
        lines.append("-" * 75)
        for s in self._sessions:
            done = "✓" if s.get("completed") else "…"
            dur = f"{s.get('duration_minutes', 0):.1f}m" if s.get("completed") else "-"
            lines.append(
                f"#{s['id']:<2} {s['task']:<27} {s.get('started_at',''):<21} "
                f"{dur:<10} {done}"
            )
        return "\n".join(lines)

    def _stats(self) -> str:
        completed = [s for s in self._sessions if s.get("completed")]
        total_min = sum(s.get("duration_minutes", 0) for s in completed)
        open_count = len(self._sessions) - len(completed)
        return (
            f"Sessions completed : {len(completed)}\n"
            f"Sessions open      : {open_count}\n"
            f"Total time         : {total_min:.1f} minute(s) "
            f"({total_min / 25:.1f} Pomodoros)"
        )

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


def _now() -> str:
    return datetime.now(tz=timezone.utc).strftime(_FMT)
