"""Task list skill – manage a persistent to-do list backed by JSON."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Task(TypedDict):
    id: int
    title: str
    done: bool
    created_at: str


class TaskListSkill:
    """Manage a persistent to-do / task list."""

    name = "task_list"
    description = (
        "Manage a to-do task list. "
        "Supported actions: 'add' (add a task), 'complete' (mark done), "
        "'uncomplete' (mark undone), 'delete' (remove task), "
        "'list' (show all tasks), 'clear' (remove all tasks)."
    )

    def __init__(self, store_path: str | os.PathLike = ".tasks.json") -> None:
        self._path = Path(store_path)
        self._tasks: list[_Task] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, action: str, title: str = "", task_id: int = 0) -> str:
        """
        Perform a task list operation.

        Parameters
        ----------
        action:
            One of ``"add"``, ``"complete"``, ``"uncomplete"``,
            ``"delete"``, ``"list"``, ``"clear"``.
        title:
            Task description (required for 'add').
        task_id:
            Numeric task ID (required for complete / uncomplete / delete).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "add":
            return self._add(title)
        if action == "complete":
            return self._set_done(task_id, done=True)
        if action == "uncomplete":
            return self._set_done(task_id, done=False)
        if action == "delete":
            return self._delete(task_id)
        if action == "list":
            return self._list()
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add, complete, uncomplete, delete, list, or clear."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> list[_Task]:
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
            json.dumps(self._tasks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _next_id(self) -> int:
        return max((t["id"] for t in self._tasks), default=0) + 1

    def _find(self, task_id: int) -> _Task | None:
        for t in self._tasks:
            if t["id"] == task_id:
                return t
        return None

    def _add(self, title: str) -> str:
        if not title:
            return "Error: title is required for add"
        task: _Task = {
            "id": self._next_id(),
            "title": title,
            "done": False,
            "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._tasks.append(task)
        self._save()
        return f"Added task #{task['id']}: {title!r}"

    def _set_done(self, task_id: int, done: bool) -> str:
        if not task_id:
            return "Error: task_id is required"
        task = self._find(task_id)
        if task is None:
            return f"Error: task #{task_id} not found"
        task["done"] = done
        self._save()
        return f"Task #{task_id} marked as {'completed' if done else 'uncompleted'}"

    def _delete(self, task_id: int) -> str:
        if not task_id:
            return "Error: task_id is required"
        task = self._find(task_id)
        if task is None:
            return f"Error: task #{task_id} not found"
        self._tasks.remove(task)
        self._save()
        return f"Deleted task #{task_id}"

    def _list(self) -> str:
        if not self._tasks:
            return "(no tasks)"
        lines = []
        for t in self._tasks:
            status = "[x]" if t["done"] else "[ ]"
            lines.append(f"#{t['id']} {status} {t['title']}")
        return "\n".join(lines)

    def _clear(self) -> str:
        count = len(self._tasks)
        self._tasks.clear()
        self._save()
        return f"Cleared {count} tasks"
