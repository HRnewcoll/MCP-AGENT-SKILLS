"""Contacts skill – manage a local address book.

Covers the "Communication" and "Productivity & Tasks" categories from the
awesome-openclaw-skills directory.  All data stored locally as JSON.

Supported actions
-----------------
add             Add a new contact.
get             Retrieve a contact by ID.
list            List all contacts.
update          Update a contact's fields.
delete          Remove a contact.
search          Search contacts by name, email, or phone.
clear           Remove all contacts.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypedDict


class _Contact(TypedDict, total=False):
    id: int
    name: str
    email: str
    phone: str
    company: str
    notes: str


class ContactsSkill:
    """Manage a local address book / contacts list."""

    name = "contacts"
    description = (
        "Manage a local address book. "
        "Supported actions: 'add' (name, email, phone, company, notes); "
        "'get' (contact_id); 'list'; "
        "'update' (contact_id, name, email, phone, company, notes); "
        "'delete' (contact_id); 'search' (query); 'clear'."
    )

    def __init__(self, store_path: str | os.PathLike = ".contacts.json") -> None:
        self._path = Path(store_path)
        self._contacts: list[_Contact] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        name: str = "",
        email: str = "",
        phone: str = "",
        company: str = "",
        notes: str = "",
        contact_id: int = 0,
        query: str = "",
    ) -> str:
        """
        Perform a contacts operation.

        Parameters
        ----------
        action:
            One of ``"add"``, ``"get"``, ``"list"``, ``"update"``,
            ``"delete"``, ``"search"``, ``"clear"``.
        name:
            Contact full name (required for ``"add"``).
        email:
            Email address.
        phone:
            Phone number.
        company:
            Company / organisation name.
        notes:
            Free-text notes.
        contact_id:
            Numeric contact ID (required for get / update / delete).
        query:
            Search query string (for ``"search"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "add":
            return self._add(name, email, phone, company, notes)
        if action == "get":
            return self._get(contact_id)
        if action == "list":
            return self._list()
        if action == "update":
            return self._update(contact_id, name, email, phone, company, notes)
        if action == "delete":
            return self._delete(contact_id)
        if action == "search":
            return self._search(query)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add, get, list, update, delete, search, or clear."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add(self, name: str, email: str, phone: str, company: str, notes: str) -> str:
        if not name:
            return "Error: name is required for add"
        contact: _Contact = {
            "id": self._next_id(),
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "notes": notes,
        }
        self._contacts.append(contact)
        self._save()
        return f"Added contact #{contact['id']}: {name}"

    def _get(self, contact_id: int) -> str:
        c = self._find(contact_id)
        if c is None:
            return f"Error: contact #{contact_id} not found"
        lines = [f"Contact #{c['id']}"]
        for field in ("name", "email", "phone", "company", "notes"):
            val = c.get(field, "")
            if val:
                lines.append(f"  {field:<8}: {val}")
        return "\n".join(lines)

    def _list(self) -> str:
        if not self._contacts:
            return "(no contacts)"
        lines = []
        for c in self._contacts:
            extra = ""
            if c.get("email"):
                extra += f"  📧 {c['email']}"
            if c.get("phone"):
                extra += f"  📞 {c['phone']}"
            lines.append(f"#{c['id']} {c['name']}{extra}")
        return "\n".join(lines)

    def _update(
        self,
        contact_id: int,
        name: str,
        email: str,
        phone: str,
        company: str,
        notes: str,
    ) -> str:
        if not contact_id:
            return "Error: contact_id is required for update"
        c = self._find(contact_id)
        if c is None:
            return f"Error: contact #{contact_id} not found"
        if name:
            c["name"] = name
        if email:
            c["email"] = email
        if phone:
            c["phone"] = phone
        if company:
            c["company"] = company
        if notes:
            c["notes"] = notes
        self._save()
        return f"Updated contact #{contact_id}"

    def _delete(self, contact_id: int) -> str:
        if not contact_id:
            return "Error: contact_id is required for delete"
        c = self._find(contact_id)
        if c is None:
            return f"Error: contact #{contact_id} not found"
        self._contacts.remove(c)
        self._save()
        return f"Deleted contact #{contact_id}"

    def _search(self, query: str) -> str:
        if not query:
            return "Error: query is required for search"
        q = query.lower()
        results = [
            c for c in self._contacts
            if any(
                q in str(c.get(f, "")).lower()
                for f in ("name", "email", "phone", "company", "notes")
            )
        ]
        if not results:
            return f"No contacts found for {query!r}"
        lines = [f"{len(results)} result(s):"]
        for c in results:
            lines.append(f"  #{c['id']} {c['name']} {c.get('email', '')} {c.get('phone', '')}".rstrip())
        return "\n".join(lines)

    def _clear(self) -> str:
        count = len(self._contacts)
        self._contacts.clear()
        self._save()
        return f"Cleared {count} contact(s)"

    def _find(self, contact_id: int) -> _Contact | None:
        return next((c for c in self._contacts if c["id"] == contact_id), None)

    def _next_id(self) -> int:
        return max((c["id"] for c in self._contacts), default=0) + 1

    def _load(self) -> list[_Contact]:
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
            json.dumps(self._contacts, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
