"""Quote skill – store and retrieve inspirational quotes.

Covers the "Notes & PKM" and "Personal Development" categories.
Includes a built-in collection of famous quotes plus user-added ones.
All custom data persisted to a local JSON file.

Supported actions
-----------------
random          Return a random quote (built-in + custom).
by_author       Return quotes by a specific author.
search          Search quotes by keyword.
add             Add a custom quote.
list_authors    List all authors.
list_custom     List user-added quotes.
delete          Delete a custom quote by ID.
daily           Return a deterministic "quote of the day" (by date).
"""

from __future__ import annotations

import json
import os
import secrets
from datetime import date
from pathlib import Path
from typing import TypedDict


class _Quote(TypedDict):
    id: int
    text: str
    author: str
    source: str


_BUILTIN: list[dict[str, str]] = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "source": ""},
    {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein", "source": ""},
    {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius", "source": ""},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt", "source": ""},
    {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon", "source": ""},
    {"text": "Get busy living or get busy dying.", "author": "Stephen King", "source": "The Shawshank Redemption"},
    {"text": "You only live once, but if you do it right, once is enough.", "author": "Mae West", "source": ""},
    {"text": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde", "source": ""},
    {"text": "Two things are infinite: the universe and human stupidity.", "author": "Albert Einstein", "source": ""},
    {"text": "Be the change you wish to see in the world.", "author": "Mahatma Gandhi", "source": ""},
    {"text": "In the beginning was the Word.", "author": "John", "source": "Bible"},
    {"text": "To be, or not to be, that is the question.", "author": "William Shakespeare", "source": "Hamlet"},
    {"text": "Ask not what your country can do for you.", "author": "John F. Kennedy", "source": "Inaugural Address"},
    {"text": "The only thing we have to fear is fear itself.", "author": "Franklin D. Roosevelt", "source": ""},
    {"text": "An unexamined life is not worth living.", "author": "Socrates", "source": ""},
    {"text": "The greatest glory in living lies not in never falling, but in rising every time we fall.", "author": "Nelson Mandela", "source": ""},
    {"text": "Spread love everywhere you go. Let no one ever come to you without leaving happier.", "author": "Mother Teresa", "source": ""},
    {"text": "When you reach the end of your rope, tie a knot in it and hang on.", "author": "Franklin D. Roosevelt", "source": ""},
    {"text": "Always remember that you are absolutely unique. Just like everyone else.", "author": "Margaret Mead", "source": ""},
    {"text": "Don't judge each day by the harvest you reap but by the seeds that you plant.", "author": "Robert Louis Stevenson", "source": ""},
]


class QuoteSkill:
    """Store and retrieve inspirational quotes."""

    name = "quote"
    description = (
        "Inspirational quotes manager. "
        "Supported actions: 'random'; 'by_author' (author); 'search' (query); "
        "'add' (text, author, source); 'list_authors'; "
        "'list_custom'; 'delete' (quote_id); 'daily'."
    )

    def __init__(self, store_path: str | os.PathLike = ".quotes.json") -> None:
        self._path = Path(store_path)
        self._custom: list[_Quote] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        text: str = "",
        author: str = "",
        source: str = "",
        query: str = "",
        quote_id: int = 0,
    ) -> str:
        action = action.strip().lower()

        all_quotes = self._all()

        if action == "random":
            return self._fmt(secrets.choice(all_quotes))
        if action == "by_author":
            return self._by_author(all_quotes, author)
        if action == "search":
            return self._search(all_quotes, query)
        if action == "add":
            return self._add(text, author, source)
        if action == "list_authors":
            return self._list_authors(all_quotes)
        if action == "list_custom":
            return self._list_custom()
        if action == "delete":
            return self._delete(quote_id)
        if action == "daily":
            return self._daily(all_quotes)
        return (
            f"Error: unknown action {action!r}. "
            "Use random, by_author, search, add, list_authors, list_custom, delete, or daily."
        )

    # ------------------------------------------------------------------

    def _all(self) -> list[dict]:
        return list(_BUILTIN) + [dict(q) for q in self._custom]

    @staticmethod
    def _fmt(q: dict) -> str:
        source = f" ({q['source']})" if q.get("source") else ""
        return f'"{q["text"]}"\n— {q["author"]}{source}'

    @staticmethod
    def _by_author(quotes: list, author: str) -> str:
        if not author:
            return "Error: author is required for by_author"
        matches = [q for q in quotes if author.lower() in q["author"].lower()]
        if not matches:
            return f"No quotes found for author {author!r}"
        return QuoteSkill._fmt(secrets.choice(matches))

    @staticmethod
    def _search(quotes: list, query: str) -> str:
        if not query:
            return "Error: query is required for search"
        q = query.lower()
        matches = [qt for qt in quotes if q in qt["text"].lower() or q in qt["author"].lower()]
        if not matches:
            return f"No quotes found for {query!r}"
        return f"{len(matches)} quote(s) found:\n" + "\n\n".join(
            QuoteSkill._fmt(m) for m in matches[:5]
        )

    def _add(self, text: str, author: str, source: str) -> str:
        if not text:
            return "Error: text is required for add"
        if not author:
            return "Error: author is required for add"
        q: _Quote = {
            "id": self._next_id(),
            "text": text,
            "author": author,
            "source": source,
        }
        self._custom.append(q)
        self._save()
        return f"Added custom quote #{q['id']}"

    @staticmethod
    def _list_authors(quotes: list) -> str:
        authors = sorted(set(q["author"] for q in quotes))
        return f"{len(authors)} author(s): " + ", ".join(authors)

    def _list_custom(self) -> str:
        if not self._custom:
            return "(no custom quotes)"
        return "\n\n".join(f"#{q['id']} " + self._fmt(q) for q in self._custom)

    def _delete(self, quote_id: int) -> str:
        if not quote_id:
            return "Error: quote_id is required for delete"
        q = next((q for q in self._custom if q["id"] == quote_id), None)
        if q is None:
            return f"Error: custom quote #{quote_id} not found"
        self._custom.remove(q)
        self._save()
        return f"Deleted custom quote #{quote_id}"

    @staticmethod
    def _daily(quotes: list) -> str:
        """Deterministic daily quote based on the current date."""
        idx = hash(str(date.today())) % len(quotes)
        return QuoteSkill._fmt(quotes[abs(idx)])

    def _next_id(self) -> int:
        return max((q["id"] for q in self._custom), default=0) + 1

    def _load(self) -> list[_Quote]:
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
            json.dumps(self._custom, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
