"""Time tracker skill – track time spent on tasks and projects.

Covers the "Productivity & Tasks" and "DevOps" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
start           Start a timer for a task.
stop            Stop the running timer for a task.
log             Manually log time for a task (without real-time tracking).
list            List all time entries.
summary         Show total time per task/project.
delete          Delete a specific time entry.
clear           Delete all entries.
running         Show currently running timers.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Entry(TypedDict):
    id: int
    task: str
    project: str
    start: str
    end: str          # empty string if still running
    minutes: float    # 0 if still running


class TimeTrackerSkill:
    """Track time spent on tasks and projects."""

    name = "time_tracker"
    description = (
        "Track time on tasks. "
        "Supported actions: 'start' (task, project); 'stop' (task); "
        "'log' (task, minutes, project); 'list'; 'summary'; "
        "'delete' (entry_id); 'clear'; 'running'."
    )

    def __init__(self, store_path: str | os.PathLike = ".time_tracker.json") -> None:
        self._path = Path(store_path)
        self._entries: list[_Entry] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        task: str = "",
        project: str = "",
        minutes: float = 0.0,
        entry_id: int = 0,
    ) -> str:
        """
        Perform a time tracking operation.

        Parameters
        ----------
        action:
            One of ``"start"``, ``"stop"``, ``"log"``, ``"list"``,
            ``"summary"``, ``"delete"``, ``"clear"``, ``"running"``.
        task:
            Task name.
        project:
            Optional project name.
        minutes:
            Duration in minutes for ``"log"``.
        entry_id:
            Entry ID for ``"delete"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "start":
            return self._start(task, project)
        if action == "stop":
            return self._stop(task)
        if action == "log":
            return self._log(task, project, minutes)
        if action == "list":
            return self._list()
        if action == "summary":
            return self._summary()
        if action == "delete":
            return self._delete(entry_id)
        if action == "clear":
            return self._clear()
        if action == "running":
            return self._running()
        return (
            f"Error: unknown action {action!r}. "
            "Use start, stop, log, list, summary, delete, clear, or running."
        )

    # ------------------------------------------------------------------

    def _start(self, task: str, project: str) -> str:
        if not task:
            return "Error: task is required for start"
        # Check if already running
        for e in self._entries:
            if e["task"].lower() == task.lower() and not e["end"]:
                return f"Timer for '{task}' is already running"
        entry: _Entry = {
            "id": self._next_id(),
            "task": task,
            "project": project,
            "start": _now(),
            "end": "",
            "minutes": 0.0,
        }
        self._entries.append(entry)
        self._save()
        return f"⏱ Started timer for '{task}'" + (f" [{project}]" if project else "")

    def _stop(self, task: str) -> str:
        if not task:
            return "Error: task is required for stop"
        running = [e for e in self._entries if e["task"].lower() == task.lower() and not e["end"]]
        if not running:
            return f"Error: no running timer for '{task}'"
        entry = running[-1]
        now = _now()
        entry["end"] = now
        start_dt = datetime.fromisoformat(entry["start"])
        end_dt = datetime.fromisoformat(now)
        entry["minutes"] = (end_dt - start_dt).total_seconds() / 60
        self._save()
        return (
            f"⏹ Stopped '{task}'  "
            f"Duration: {_fmt_minutes(entry['minutes'])}"
        )

    def _log(self, task: str, project: str, minutes: float) -> str:
        if not task:
            return "Error: task is required for log"
        if minutes <= 0:
            return "Error: minutes must be > 0"
        entry: _Entry = {
            "id": self._next_id(),
            "task": task,
            "project": project,
            "start": _now(),
            "end": _now(),
            "minutes": float(minutes),
        }
        self._entries.append(entry)
        self._save()
        return f"Logged {_fmt_minutes(minutes)} for '{task}'" + (f" [{project}]" if project else "")

    def _list(self) -> str:
        if not self._entries:
            return "(no time entries)"
        lines = []
        for e in sorted(self._entries, key=lambda x: x["start"], reverse=True):
            status = "▶ RUNNING" if not e["end"] else _fmt_minutes(e["minutes"])
            proj = f" [{e['project']}]" if e["project"] else ""
            lines.append(f"#{e['id']} {e['task']}{proj}  {status}  started: {e['start'][:16]}")
        return "\n".join(lines)

    def _summary(self) -> str:
        if not self._entries:
            return "(no time entries)"
        totals: dict[str, float] = {}
        for e in self._entries:
            if e["end"]:
                key = e["task"]
                totals[key] = totals.get(key, 0.0) + e["minutes"]
        if not totals:
            return "(no completed entries)"
        lines = ["Time summary:"]
        for task, mins in sorted(totals.items(), key=lambda x: -x[1]):
            lines.append(f"  {task:<30} {_fmt_minutes(mins)}")
        total_all = sum(totals.values())
        lines.append(f"  {'TOTAL':<30} {_fmt_minutes(total_all)}")
        return "\n".join(lines)

    def _delete(self, entry_id: int) -> str:
        if not entry_id:
            return "Error: entry_id is required for delete"
        entry = next((e for e in self._entries if e["id"] == entry_id), None)
        if entry is None:
            return f"Error: entry #{entry_id} not found"
        self._entries.remove(entry)
        self._save()
        return f"Deleted entry #{entry_id}"

    def _clear(self) -> str:
        count = len(self._entries)
        self._entries.clear()
        self._save()
        return f"Cleared {count} entry/entries"

    def _running(self) -> str:
        running = [e for e in self._entries if not e["end"]]
        if not running:
            return "(no timers running)"
        lines = []
        for e in running:
            start_dt = datetime.fromisoformat(e["start"])
            now_dt = datetime.now(tz=timezone.utc)
            elapsed = (now_dt - start_dt).total_seconds() / 60
            proj = f" [{e['project']}]" if e["project"] else ""
            lines.append(f"▶ #{e['id']} {e['task']}{proj}  elapsed: {_fmt_minutes(elapsed)}")
        return "\n".join(lines)

    def _next_id(self) -> int:
        return max((e["id"] for e in self._entries), default=0) + 1

    def _load(self) -> list[_Entry]:
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
            json.dumps(self._entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_minutes(mins: float) -> str:
    h = int(mins // 60)
    m = int(mins % 60)
    s = int((mins * 60) % 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"
