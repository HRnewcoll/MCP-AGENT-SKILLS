"""Flashcard skill – create and study flashcard decks locally.

Covers the "Personal Development" and "Notes & PKM" categories from the
awesome-openclaw-skills directory.  All data stored locally as JSON.

Supported actions
-----------------
create_deck     Create a new flashcard deck.
list_decks      List all decks.
add_card        Add a card (front/back) to a deck.
list_cards      List all cards in a deck.
get_card        Get a specific card by ID.
remove_card     Remove a card from a deck.
quiz            Get a random card from a deck for quizzing.
delete_deck     Delete an entire deck.
"""

from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from typing import TypedDict


class _Card(TypedDict):
    id: int
    front: str
    back: str


class _Deck(TypedDict):
    name: str
    cards: list[_Card]


class _Store(TypedDict):
    decks: dict[str, _Deck]


class FlashcardSkill:
    """Create and study flashcard decks locally."""

    name = "flashcard"
    description = (
        "Manage and study flashcard decks. "
        "Supported actions: 'create_deck' (deck); 'list_decks'; "
        "'add_card' (deck, front, back); 'list_cards' (deck); "
        "'get_card' (deck, card_id); 'remove_card' (deck, card_id); "
        "'quiz' (deck); 'delete_deck' (deck)."
    )

    def __init__(self, store_path: str | os.PathLike = ".flashcards.json") -> None:
        self._path = Path(store_path)
        self._store: _Store = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        deck: str = "",
        front: str = "",
        back: str = "",
        card_id: int = 0,
    ) -> str:
        """
        Perform a flashcard operation.

        Parameters
        ----------
        action:
            One of ``"create_deck"``, ``"list_decks"``, ``"add_card"``,
            ``"list_cards"``, ``"get_card"``, ``"remove_card"``,
            ``"quiz"``, ``"delete_deck"``.
        deck:
            Name of the deck.
        front:
            Front (question) side of the card (for ``"add_card"``).
        back:
            Back (answer) side of the card (for ``"add_card"``).
        card_id:
            Card ID (for ``"get_card"`` and ``"remove_card"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "create_deck":
            return self._create_deck(deck)
        if action == "list_decks":
            return self._list_decks()
        if action == "add_card":
            return self._add_card(deck, front, back)
        if action == "list_cards":
            return self._list_cards(deck)
        if action == "get_card":
            return self._get_card(deck, card_id)
        if action == "remove_card":
            return self._remove_card(deck, card_id)
        if action == "quiz":
            return self._quiz(deck)
        if action == "delete_deck":
            return self._delete_deck(deck)
        return (
            f"Error: unknown action {action!r}. "
            "Use create_deck, list_decks, add_card, list_cards, "
            "get_card, remove_card, quiz, or delete_deck."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_deck(self, name: str) -> str:
        if not name:
            return "Error: deck name is required"
        if name in self._store["decks"]:
            return f"Error: deck {name!r} already exists"
        self._store["decks"][name] = {"name": name, "cards": []}
        self._save()
        return f"Created deck {name!r}"

    def _list_decks(self) -> str:
        if not self._store["decks"]:
            return "(no decks)"
        lines = ["Decks:"]
        for d in self._store["decks"].values():
            lines.append(f"  {d['name']}  ({len(d['cards'])} card(s))")
        return "\n".join(lines)

    def _add_card(self, deck: str, front: str, back: str) -> str:
        d = self._get_deck(deck)
        if isinstance(d, str):
            return d
        if not front:
            return "Error: front is required for add_card"
        if not back:
            return "Error: back is required for add_card"
        next_id = max((c["id"] for c in d["cards"]), default=0) + 1
        d["cards"].append({"id": next_id, "front": front, "back": back})
        self._save()
        return f"Added card #{next_id} to {deck!r}: {front!r}"

    def _list_cards(self, deck: str) -> str:
        d = self._get_deck(deck)
        if isinstance(d, str):
            return d
        if not d["cards"]:
            return f"(no cards in {deck!r})"
        lines = [f"Cards in {deck!r}:"]
        for c in d["cards"]:
            lines.append(f"  #{c['id']}  Q: {c['front']}")
        return "\n".join(lines)

    def _get_card(self, deck: str, card_id: int) -> str:
        d = self._get_deck(deck)
        if isinstance(d, str):
            return d
        card = next((c for c in d["cards"] if c["id"] == card_id), None)
        if card is None:
            return f"Error: card #{card_id} not found in {deck!r}"
        return f"#{card['id']}\nFront: {card['front']}\nBack:  {card['back']}"

    def _remove_card(self, deck: str, card_id: int) -> str:
        d = self._get_deck(deck)
        if isinstance(d, str):
            return d
        card = next((c for c in d["cards"] if c["id"] == card_id), None)
        if card is None:
            return f"Error: card #{card_id} not found in {deck!r}"
        d["cards"].remove(card)
        self._save()
        return f"Removed card #{card_id} from {deck!r}"

    def _quiz(self, deck: str) -> str:
        d = self._get_deck(deck)
        if isinstance(d, str):
            return d
        if not d["cards"]:
            return f"Error: deck {deck!r} has no cards"
        card = secrets.choice(d["cards"])
        return (
            f"[Quiz card #{card['id']} from {deck!r}]\n"
            f"Front: {card['front']}\n"
            f"(Use get_card with card_id={card['id']} to see the answer)"
        )

    def _delete_deck(self, deck: str) -> str:
        if not deck:
            return "Error: deck name is required"
        if deck not in self._store["decks"]:
            return f"Error: deck {deck!r} not found"
        count = len(self._store["decks"][deck]["cards"])
        del self._store["decks"][deck]
        self._save()
        return f"Deleted deck {deck!r} ({count} card(s) removed)"

    def _get_deck(self, name: str) -> "_Deck | str":
        if not name:
            return "Error: deck name is required"
        d = self._store["decks"].get(name)
        if d is None:
            return f"Error: deck {name!r} not found"
        return d

    def _load(self) -> _Store:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "decks" in data:
                    return data  # type: ignore[return-value]
            except (json.JSONDecodeError, OSError):
                pass
        return {"decks": {}}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._store, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
