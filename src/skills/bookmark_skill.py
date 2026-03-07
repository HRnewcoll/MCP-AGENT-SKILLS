"""Bookmark skill – save, organise, and search web bookmarks locally.

Covers the "Browser & Automation" and "Notes & PKM" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
add             Save a new bookmark (url, title, tags).
get             Retrieve a bookmark by ID.
list            List all bookmarks.
search          Search bookmarks by URL, title, or tag.
delete          Remove a bookmark by ID.
tag_search      Find all bookmarks with a specific tag.
list_tags       List all tags used.
clear           Delete all bookmarks.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Bookmark(TypedDict):
    id: int
    url: str
    title: str
    tags: list[str]
    created_at: str


class BookmarkSkill:
    """Save, organise, and search web bookmarks locally."""

    name = "bookmark"
    description = (
        "Manage web bookmarks locally. "
        "Supported actions: 'add' (url, title, tags); 'get' (bookmark_id); "
        "'list'; 'search' (query); 'delete' (bookmark_id); "
        "'tag_search' (tag); 'list_tags'; 'clear'."
        "\ntags: comma-separated list (optional)."
    )

    def __init__(self, store_path: str | os.PathLike = ".bookmarks.json") -> None:
        self._path = Path(store_path)
        self._bookmarks: list[_Bookmark] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        url: str = "",
        title: str = "",
        tags: str = "",
        bookmark_id: int = 0,
        query: str = "",
        tag: str = "",
    ) -> str:
        """
        Perform a bookmark operation.

        Parameters
        ----------
        action:
            One of ``"add"``, ``"get"``, ``"list"``, ``"search"``,
            ``"delete"``, ``"tag_search"``, ``"list_tags"``, ``"clear"``.
        url:
            URL to bookmark (required for ``"add"``).
        title:
            Human-readable title for the bookmark.
        tags:
            Comma-separated tags.
        bookmark_id:
            Numeric bookmark ID.
        query:
            Search query for ``"search"``.
        tag:
            Tag to filter by for ``"tag_search"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "add":
            return self._add(url, title, tags)
        if action == "get":
            return self._get(bookmark_id)
        if action == "list":
            return self._list()
        if action == "search":
            return self._search(query)
        if action == "delete":
            return self._delete(bookmark_id)
        if action == "tag_search":
            return self._tag_search(tag)
        if action == "list_tags":
            return self._list_tags()
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add, get, list, search, delete, tag_search, list_tags, or clear."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add(self, url: str, title: str, tags: str) -> str:
        if not url:
            return "Error: url is required for add"
        tag_list = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]
        bm: _Bookmark = {
            "id": self._next_id(),
            "url": url,
            "title": title or url,
            "tags": tag_list,
            "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._bookmarks.append(bm)
        self._save()
        return f"Saved bookmark #{bm['id']}: {bm['title']}"

    def _get(self, bm_id: int) -> str:
        bm = self._find(bm_id)
        if bm is None:
            return f"Error: bookmark #{bm_id} not found"
        tags_str = ", ".join(f"#{t}" for t in bm["tags"]) if bm["tags"] else "(none)"
        return (
            f"#{bm['id']} {bm['title']}\n"
            f"URL    : {bm['url']}\n"
            f"Tags   : {tags_str}\n"
            f"Saved  : {bm['created_at']}"
        )

    def _list(self) -> str:
        if not self._bookmarks:
            return "(no bookmarks)"
        lines = []
        for bm in self._bookmarks:
            tags_str = " " + " ".join(f"#{t}" for t in bm["tags"]) if bm["tags"] else ""
            lines.append(f"#{bm['id']} {bm['title']}{tags_str}\n   {bm['url']}")
        return "\n".join(lines)

    def _search(self, query: str) -> str:
        if not query:
            return "Error: query is required for search"
        q = query.lower()
        results = [
            bm for bm in self._bookmarks
            if q in bm["url"].lower()
            or q in bm["title"].lower()
            or any(q in t.lower() for t in bm["tags"])
        ]
        if not results:
            return f"No bookmarks found for {query!r}"
        lines = [f"{len(results)} result(s):"]
        for bm in results:
            lines.append(f"  #{bm['id']} {bm['title']}  {bm['url']}")
        return "\n".join(lines)

    def _delete(self, bm_id: int) -> str:
        if not bm_id:
            return "Error: bookmark_id is required for delete"
        bm = self._find(bm_id)
        if bm is None:
            return f"Error: bookmark #{bm_id} not found"
        self._bookmarks.remove(bm)
        self._save()
        return f"Deleted bookmark #{bm_id}"

    def _tag_search(self, tag: str) -> str:
        if not tag:
            return "Error: tag is required for tag_search"
        tag_clean = tag.lstrip("#").lower()
        results = [
            bm for bm in self._bookmarks
            if any(t.lower() == tag_clean for t in bm["tags"])
        ]
        if not results:
            return f"No bookmarks with tag #{tag_clean}"
        lines = [f"{len(results)} bookmark(s) tagged #{tag_clean}:"]
        for bm in results:
            lines.append(f"  #{bm['id']} {bm['title']}  {bm['url']}")
        return "\n".join(lines)

    def _list_tags(self) -> str:
        all_tags: dict[str, int] = {}
        for bm in self._bookmarks:
            for t in bm["tags"]:
                all_tags[t] = all_tags.get(t, 0) + 1
        if not all_tags:
            return "(no tags)"
        return "\n".join(
            f"#{tag} ({count})"
            for tag, count in sorted(all_tags.items(), key=lambda x: -x[1])
        )

    def _clear(self) -> str:
        count = len(self._bookmarks)
        self._bookmarks.clear()
        self._save()
        return f"Cleared {count} bookmark(s)"

    def _find(self, bm_id: int) -> _Bookmark | None:
        return next((bm for bm in self._bookmarks if bm["id"] == bm_id), None)

    def _next_id(self) -> int:
        return max((bm["id"] for bm in self._bookmarks), default=0) + 1

    def _load(self) -> list[_Bookmark]:
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
            json.dumps(self._bookmarks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
