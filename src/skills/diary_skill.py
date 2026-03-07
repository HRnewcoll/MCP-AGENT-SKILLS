"""Diary skill – keep a private daily journal with mood and tags.

Covers the "Personal Development" and "Notes & PKM" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
write           Add a journal entry (for today or a given date).
read            Read the entry for a specific date.
list            List all entry dates.
search          Search entries by keyword or tag.
delete          Delete the entry for a specific date.
today           Show today's entry (or prompt to write one).
stats           Show writing statistics.
clear           Delete all entries.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Entry(TypedDict):
    date: str
    content: str
    mood: str
    tags: list[str]
    created_at: str
    updated_at: str


class DiarySkill:
    """Keep a private daily journal with mood tracking and tag search."""

    name = "diary"
    description = (
        "Private daily journal / diary. "
        "Supported actions: 'write' (content, mood, tags, date); "
        "'read' (date); 'list'; 'search' (query); 'delete' (date); "
        "'today'; 'stats'; 'clear'."
        "\nDates default to today (YYYY-MM-DD). "
        "mood: happy/sad/neutral/anxious/excited/tired/angry (optional). "
        "tags: comma-separated (optional)."
    )

    def __init__(self, store_path: str | os.PathLike = ".diary.json") -> None:
        self._path = Path(store_path)
        self._entries: dict[str, _Entry] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        content: str = "",
        mood: str = "",
        tags: str = "",
        date: str = "",
        query: str = "",
    ) -> str:
        """
        Perform a diary operation.

        Parameters
        ----------
        action:
            One of ``"write"``, ``"read"``, ``"list"``, ``"search"``,
            ``"delete"``, ``"today"``, ``"stats"``, ``"clear"``.
        content:
            Journal entry text (required for ``"write"``).
        mood:
            Optional mood tag.
        tags:
            Comma-separated tag strings.
        date:
            Entry date in ``"YYYY-MM-DD"`` format (default today).
        query:
            Keyword or tag for ``"search"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        entry_date = date.strip() if date.strip() else _today()

        if action == "write":
            return self._write(entry_date, content, mood, tags)
        if action == "read":
            return self._read(entry_date)
        if action == "list":
            return self._list()
        if action == "search":
            return self._search(query)
        if action == "delete":
            return self._delete(entry_date)
        if action == "today":
            return self._read(_today())
        if action == "stats":
            return self._stats()
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use write, read, list, search, delete, today, stats, or clear."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _write(self, entry_date: str, content: str, mood: str, tags: str) -> str:
        if not content:
            return "Error: content is required for write"
        now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        tag_list = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]
        existing = self._entries.get(entry_date)
        entry: _Entry = {
            "date": entry_date,
            "content": content,
            "mood": mood.strip().lower() if mood.strip() else "",
            "tags": tag_list,
            "created_at": existing["created_at"] if existing else now,
            "updated_at": now,
        }
        self._entries[entry_date] = entry
        self._save()
        action_word = "Updated" if existing else "Wrote"
        return f"{action_word} diary entry for {entry_date}"

    def _read(self, entry_date: str) -> str:
        entry = self._entries.get(entry_date)
        if entry is None:
            return f"No entry for {entry_date}"
        mood_str = f"  Mood: {entry['mood']}" if entry["mood"] else ""
        tags_str = "  Tags: " + ", ".join(f"#{t}" for t in entry["tags"]) if entry["tags"] else ""
        return (
            f"📔 {entry['date']}{mood_str}{tags_str}\n"
            f"{'─' * 40}\n"
            f"{entry['content']}"
        )

    def _list(self) -> str:
        if not self._entries:
            return "(no diary entries)"
        lines = []
        for d in sorted(self._entries.keys(), reverse=True):
            e = self._entries[d]
            preview = e["content"][:50].replace("\n", " ")
            mood_str = f" [{e['mood']}]" if e["mood"] else ""
            lines.append(f"{d}{mood_str}  {preview}{'…' if len(e['content']) > 50 else ''}")
        return "\n".join(lines)

    def _search(self, query: str) -> str:
        if not query:
            return "Error: query is required for search"
        q = query.lower().lstrip("#")
        results = []
        for d, e in sorted(self._entries.items(), reverse=True):
            if (q in e["content"].lower()
                    or q in e["mood"].lower()
                    or any(q in t.lower() for t in e["tags"])):
                results.append(d)
        if not results:
            return f"No entries found for {query!r}"
        return f"{len(results)} entry/entries matching {query!r}:\n" + "\n".join(results)

    def _delete(self, entry_date: str) -> str:
        if entry_date not in self._entries:
            return f"Error: no entry for {entry_date}"
        del self._entries[entry_date]
        self._save()
        return f"Deleted diary entry for {entry_date}"

    def _stats(self) -> str:
        if not self._entries:
            return "(no diary entries)"
        dates = sorted(self._entries.keys())
        moods: dict[str, int] = {}
        total_words = 0
        for e in self._entries.values():
            total_words += len(e["content"].split())
            if e["mood"]:
                moods[e["mood"]] = moods.get(e["mood"], 0) + 1
        most_common_mood = max(moods, key=lambda k: moods[k]) if moods else "N/A"
        return (
            f"Total entries : {len(self._entries)}\n"
            f"First entry   : {dates[0]}\n"
            f"Latest entry  : {dates[-1]}\n"
            f"Total words   : {total_words}\n"
            f"Avg words/day : {total_words // len(self._entries)}\n"
            f"Most used mood: {most_common_mood}"
        )

    def _clear(self) -> str:
        count = len(self._entries)
        self._entries.clear()
        self._save()
        return f"Cleared {count} diary entry/entries"

    def _load(self) -> dict[str, _Entry]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _today() -> str:
    return date.today().isoformat()
