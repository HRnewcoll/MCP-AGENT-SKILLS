"""Poll/voting skill – create simple polls and vote on options.

Covers the "Productivity & Tasks" and "Communication" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
create          Create a new poll with options.
vote            Cast a vote for an option.
results         Show current results.
list            List all polls.
close           Mark a poll as closed.
delete          Delete a poll.
clear           Delete all polls.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Poll(TypedDict):
    id: int
    question: str
    options: list[str]
    votes: dict[str, int]     # option -> count
    closed: bool
    created_at: str


class PollSkill:
    """Create and manage simple polls with vote counting."""

    name = "poll"
    description = (
        "Create and manage polls. "
        "Supported actions: 'create' (question, options – comma-separated); "
        "'vote' (poll_id, option); 'results' (poll_id); "
        "'list'; 'close' (poll_id); 'delete' (poll_id); 'clear'."
    )

    def __init__(self, store_path: str | os.PathLike = ".polls.json") -> None:
        self._path = Path(store_path)
        self._polls: list[_Poll] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        question: str = "",
        options: str = "",
        poll_id: int = 0,
        option: str = "",
    ) -> str:
        action = action.strip().lower()

        if action == "create":
            return self._create(question, options)
        if action == "vote":
            return self._vote(poll_id, option)
        if action == "results":
            return self._results(poll_id)
        if action == "list":
            return self._list()
        if action == "close":
            return self._close(poll_id)
        if action == "delete":
            return self._delete(poll_id)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use create, vote, results, list, close, delete, or clear."
        )

    # ------------------------------------------------------------------

    def _create(self, question: str, options: str) -> str:
        if not question:
            return "Error: question is required for create"
        if not options:
            return "Error: options is required for create"
        opts = [o.strip() for o in options.split(",") if o.strip()]
        if len(opts) < 2:
            return "Error: at least 2 options are required"
        poll: _Poll = {
            "id": self._next_id(),
            "question": question,
            "options": opts,
            "votes": {o: 0 for o in opts},
            "closed": False,
            "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._polls.append(poll)
        self._save()
        return (
            f"Created poll #{poll['id']}: {question!r}\n"
            + "\n".join(f"  {i+1}. {o}" for i, o in enumerate(opts))
        )

    def _vote(self, poll_id: int, option: str) -> str:
        p = self._get(poll_id)
        if isinstance(p, str):
            return p
        if p["closed"]:
            return f"Error: poll #{poll_id} is closed"
        if not option:
            return "Error: option is required for vote"
        # Allow matching by number or text (case-insensitive)
        opt_lower = option.strip().lower()
        matched = None
        for o in p["options"]:
            if o.lower() == opt_lower:
                matched = o
                break
        if matched is None:
            # Try numeric index
            if opt_lower.isdigit():
                idx = int(opt_lower) - 1
                if 0 <= idx < len(p["options"]):
                    matched = p["options"][idx]
        if matched is None:
            return f"Error: option {option!r} not found. Options: {', '.join(p['options'])}"
        p["votes"][matched] += 1
        self._save()
        return f"Voted for '{matched}' in poll #{poll_id}"

    def _results(self, poll_id: int) -> str:
        p = self._get(poll_id)
        if isinstance(p, str):
            return p
        total = sum(p["votes"].values())
        status = " [CLOSED]" if p["closed"] else ""
        lines = [f"Poll #{p['id']}{status}: {p['question']}"]
        for opt in p["options"]:
            cnt = p["votes"].get(opt, 0)
            pct = cnt / total * 100 if total else 0
            bar = "█" * int(pct / 5)
            lines.append(f"  {opt:<20} {cnt:>4} vote(s) ({pct:5.1f}%) {bar}")
        lines.append(f"  Total votes: {total}")
        return "\n".join(lines)

    def _list(self) -> str:
        if not self._polls:
            return "(no polls)"
        lines = []
        for p in self._polls:
            total = sum(p["votes"].values())
            status = " [CLOSED]" if p["closed"] else ""
            lines.append(f"#{p['id']}{status} {p['question']!r}  ({total} vote(s))")
        return "\n".join(lines)

    def _close(self, poll_id: int) -> str:
        p = self._get(poll_id)
        if isinstance(p, str):
            return p
        if p["closed"]:
            return f"Poll #{poll_id} is already closed"
        p["closed"] = True
        self._save()
        return f"Closed poll #{poll_id}"

    def _delete(self, poll_id: int) -> str:
        p = self._get(poll_id)
        if isinstance(p, str):
            return p
        self._polls.remove(p)
        self._save()
        return f"Deleted poll #{poll_id}"

    def _clear(self) -> str:
        count = len(self._polls)
        self._polls.clear()
        self._save()
        return f"Cleared {count} poll(s)"

    def _get(self, poll_id: int) -> "_Poll | str":
        if not poll_id:
            return "Error: poll_id is required"
        p = next((p for p in self._polls if p["id"] == poll_id), None)
        if p is None:
            return f"Error: poll #{poll_id} not found"
        return p

    def _next_id(self) -> int:
        return max((p["id"] for p in self._polls), default=0) + 1

    def _load(self) -> list[_Poll]:
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
            json.dumps(self._polls, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
