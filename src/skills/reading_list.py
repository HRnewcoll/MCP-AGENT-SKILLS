"""Reading list skill – manage a list of books to read with ratings and notes.

Covers the "Notes & PKM" and "Personal Development" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
add             Add a book to the list.
list            List all books (optionally filtered by status).
update_status   Update a book's reading status.
rate            Rate a book (1–5 stars).
note            Add/update a note for a book.
search          Search books by title, author, or tag.
stats           Show reading statistics.
delete          Remove a book from the list.
clear           Remove all books.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

_STATUSES = {"want_to_read", "reading", "read", "abandoned"}


class _Book(TypedDict):
    id: int
    title: str
    author: str
    genre: str
    status: str
    rating: int          # 0 = not rated
    notes: str
    added_at: str
    finished_at: str


class ReadingListSkill:
    """Manage a reading list with status tracking and ratings."""

    name = "reading_list"
    description = (
        "Manage a book reading list. "
        "Supported actions: 'add' (title, author, genre, status=want_to_read); "
        "'list' (status=all); 'update_status' (book_id, status); "
        "'rate' (book_id, rating 1-5); 'note' (book_id, text); "
        "'search' (query); 'stats'; 'delete' (book_id); 'clear'."
        "\nStatus options: want_to_read, reading, read, abandoned."
    )

    def __init__(self, store_path: str | os.PathLike = ".reading_list.json") -> None:
        self._path = Path(store_path)
        self._books: list[_Book] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        title: str = "",
        author: str = "",
        genre: str = "",
        status: str = "",
        book_id: int = 0,
        rating: int = 0,
        text: str = "",
        query: str = "",
    ) -> str:
        action = action.strip().lower()

        if action == "add":
            return self._add(title, author, genre, status or "want_to_read")
        if action == "list":
            return self._list(status or "all")
        if action == "update_status":
            return self._update_status(book_id, status)
        if action == "rate":
            return self._rate(book_id, rating)
        if action == "note":
            return self._note(book_id, text)
        if action == "search":
            return self._search(query)
        if action == "stats":
            return self._stats()
        if action == "delete":
            return self._delete(book_id)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add, list, update_status, rate, note, search, stats, delete, or clear."
        )

    # ------------------------------------------------------------------

    def _add(self, title: str, author: str, genre: str, status: str) -> str:
        if not title:
            return "Error: title is required for add"
        stat = status.strip().lower()
        if stat not in _STATUSES:
            stat = "want_to_read"
        book: _Book = {
            "id": self._next_id(),
            "title": title,
            "author": author,
            "genre": genre,
            "status": stat,
            "rating": 0,
            "notes": "",
            "added_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "finished_at": "",
        }
        self._books.append(book)
        self._save()
        return f"Added #{book['id']}: {title!r}" + (f" by {author}" if author else "")

    def _list(self, status: str) -> str:
        books = self._books
        if status.lower() not in ("all", ""):
            books = [b for b in self._books if b["status"] == status.lower()]
        if not books:
            return "(no books)" if status in ("all", "") else f"(no books with status '{status}')"
        lines = []
        for b in books:
            stars = "★" * b["rating"] + "☆" * (5 - b["rating"]) if b["rating"] else "☆☆☆☆☆"
            author = f" – {b['author']}" if b["author"] else ""
            lines.append(f"#{b['id']} [{b['status']:>12}] {stars} {b['title']!r}{author}")
        return "\n".join(lines)

    def _update_status(self, book_id: int, status: str) -> str:
        b = self._get(book_id)
        if isinstance(b, str):
            return b
        stat = status.strip().lower()
        if stat not in _STATUSES:
            return f"Error: status must be one of: {', '.join(sorted(_STATUSES))}"
        b["status"] = stat
        if stat == "read" and not b["finished_at"]:
            b["finished_at"] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._save()
        return f"Updated #{book_id} to status '{stat}'"

    def _rate(self, book_id: int, rating: int) -> str:
        b = self._get(book_id)
        if isinstance(b, str):
            return b
        if not 1 <= int(rating) <= 5:
            return "Error: rating must be between 1 and 5"
        b["rating"] = int(rating)
        self._save()
        return f"Rated #{book_id} {b['title']!r}: {'★' * b['rating']}"

    def _note(self, book_id: int, text: str) -> str:
        b = self._get(book_id)
        if isinstance(b, str):
            return b
        if not text:
            return "Error: text is required for note"
        b["notes"] = text
        self._save()
        return f"Note saved for #{book_id} {b['title']!r}"

    def _search(self, query: str) -> str:
        if not query:
            return "Error: query is required for search"
        q = query.lower()
        results = [
            b for b in self._books
            if q in b["title"].lower()
            or q in b["author"].lower()
            or q in b["genre"].lower()
            or q in b["notes"].lower()
        ]
        if not results:
            return f"No books found for {query!r}"
        return f"{len(results)} result(s):\n" + "\n".join(
            f"  #{b['id']} {b['title']!r}" for b in results
        )

    def _stats(self) -> str:
        if not self._books:
            return "(no books)"
        status_counts: dict[str, int] = {}
        rated = [b for b in self._books if b["rating"]]
        avg_rating = sum(b["rating"] for b in rated) / len(rated) if rated else 0
        for b in self._books:
            status_counts[b["status"]] = status_counts.get(b["status"], 0) + 1
        lines = [f"Total books: {len(self._books)}"]
        for s in sorted(_STATUSES):
            lines.append(f"  {s:<15}: {status_counts.get(s, 0)}")
        lines.append(f"Avg rating  : {avg_rating:.1f} ★ ({len(rated)} rated)")
        return "\n".join(lines)

    def _delete(self, book_id: int) -> str:
        b = self._get(book_id)
        if isinstance(b, str):
            return b
        self._books.remove(b)
        self._save()
        return f"Deleted #{book_id}"

    def _clear(self) -> str:
        count = len(self._books)
        self._books.clear()
        self._save()
        return f"Cleared {count} book(s)"

    def _get(self, book_id: int) -> "_Book | str":
        if not book_id:
            return "Error: book_id is required"
        b = next((b for b in self._books if b["id"] == book_id), None)
        if b is None:
            return f"Error: book #{book_id} not found"
        return b

    def _next_id(self) -> int:
        return max((b["id"] for b in self._books), default=0) + 1

    def _load(self) -> list[_Book]:
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
            json.dumps(self._books, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
