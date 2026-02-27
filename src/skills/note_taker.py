"""Note taker skill – manage structured notes with titles, content, tags and search."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Note(TypedDict):
    id: int
    title: str
    content: str
    tags: list[str]
    created_at: str
    updated_at: str


class NoteTakerSkill:
    """Create, search, and manage rich structured notes."""

    name = "note_taker"
    description = (
        "Create and manage structured notes with titles, content, and tags. "
        "Supported actions: 'add' (create note), 'get' (retrieve by id), "
        "'update' (edit title/content/tags), 'delete' (remove note), "
        "'list' (show all notes), 'search' (find notes by keyword or #tag), "
        "'clear' (delete all notes)."
    )

    def __init__(self, store_path: str | os.PathLike = ".notes.json") -> None:
        self._path = Path(store_path)
        self._notes: list[_Note] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        title: str = "",
        content: str = "",
        note_id: int = 0,
        tags: str = "",
        query: str = "",
    ) -> str:
        """
        Perform a note operation.

        Parameters
        ----------
        action:
            One of ``"add"``, ``"get"``, ``"update"``, ``"delete"``,
            ``"list"``, ``"search"``, ``"clear"``.
        title:
            Note title (required for add).
        content:
            Note body text (required for add; optional for update).
        note_id:
            Numeric note ID (required for get / update / delete).
        tags:
            Comma-separated list of tags (optional for add / update).
        query:
            Keyword or ``#tag`` string for search.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "add":
            return self._add(title, content, tags)
        if action == "get":
            return self._get(note_id)
        if action == "update":
            return self._update(note_id, title, content, tags)
        if action == "delete":
            return self._delete(note_id)
        if action == "list":
            return self._list()
        if action == "search":
            return self._search(query)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add, get, update, delete, list, search, or clear."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> list[_Note]:
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
            json.dumps(self._notes, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _next_id(self) -> int:
        return max((n["id"] for n in self._notes), default=0) + 1

    def _find(self, note_id: int) -> _Note | None:
        for n in self._notes:
            if n["id"] == note_id:
                return n
        return None

    @staticmethod
    def _now() -> str:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _parse_tags(tags_str: str) -> list[str]:
        return [t.strip().lstrip("#") for t in tags_str.split(",") if t.strip()]

    def _add(self, title: str, content: str, tags: str) -> str:
        if not title:
            return "Error: title is required for add"
        now = self._now()
        note: _Note = {
            "id": self._next_id(),
            "title": title,
            "content": content,
            "tags": self._parse_tags(tags),
            "created_at": now,
            "updated_at": now,
        }
        self._notes.append(note)
        self._save()
        return f"Note #{note['id']} created: {title!r}"

    def _get(self, note_id: int) -> str:
        if not note_id:
            return "Error: note_id is required for get"
        note = self._find(note_id)
        if note is None:
            return f"Error: note #{note_id} not found"
        tags_str = ", ".join(f"#{t}" for t in note["tags"]) if note["tags"] else "(none)"
        return (
            f"#{note['id']} – {note['title']}\n"
            f"Tags: {tags_str}\n"
            f"Created: {note['created_at']}  Updated: {note['updated_at']}\n"
            f"\n{note['content']}"
        )

    def _update(self, note_id: int, title: str, content: str, tags: str) -> str:
        if not note_id:
            return "Error: note_id is required for update"
        note = self._find(note_id)
        if note is None:
            return f"Error: note #{note_id} not found"
        if title:
            note["title"] = title
        if content:
            note["content"] = content
        if tags:
            note["tags"] = self._parse_tags(tags)
        note["updated_at"] = self._now()
        self._save()
        return f"Note #{note_id} updated"

    def _delete(self, note_id: int) -> str:
        if not note_id:
            return "Error: note_id is required for delete"
        note = self._find(note_id)
        if note is None:
            return f"Error: note #{note_id} not found"
        self._notes.remove(note)
        self._save()
        return f"Deleted note #{note_id}"

    def _list(self) -> str:
        if not self._notes:
            return "(no notes)"
        lines = []
        for n in self._notes:
            tags_str = " " + " ".join(f"#{t}" for t in n["tags"]) if n["tags"] else ""
            lines.append(f"#{n['id']} [{n['updated_at']}] {n['title']}{tags_str}")
        return "\n".join(lines)

    def _search(self, query: str) -> str:
        if not query:
            return "Error: query is required for search"
        q_lower = query.lower()
        is_tag = q_lower.startswith("#")
        tag_query = q_lower.lstrip("#") if is_tag else ""
        results = []
        for note in self._notes:
            if is_tag:
                if any(t.lower() == tag_query for t in note["tags"]):
                    results.append(note)
            else:
                if (
                    q_lower in note["title"].lower()
                    or q_lower in note["content"].lower()
                    or any(q_lower in t.lower() for t in note["tags"])
                ):
                    results.append(note)
        if not results:
            return f"No notes found for {query!r}"
        lines = []
        for n in results:
            tags_str = " " + " ".join(f"#{t}" for t in n["tags"]) if n["tags"] else ""
            lines.append(f"#{n['id']} {n['title']}{tags_str}")
        return f"{len(results)} result(s):\n" + "\n".join(lines)

    def _clear(self) -> str:
        count = len(self._notes)
        self._notes.clear()
        self._save()
        return f"Cleared {count} notes"
