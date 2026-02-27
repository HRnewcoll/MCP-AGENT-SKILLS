"""Memory skill – persistent key-value store backed by a JSON file."""

import json
import os
from pathlib import Path


class MemorySkill:
    """Store and retrieve information across agent turns."""

    name = "memory"
    description = (
        "Persist and retrieve named pieces of information (key-value). "
        "Supported actions: 'set', 'get', 'delete', 'list', 'clear'."
    )

    def __init__(self, store_path: str | os.PathLike = ".memory.json") -> None:
        self._path = Path(store_path)
        self._data: dict[str, str] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, action: str, key: str = "", value: str = "") -> str:
        """
        Perform a memory operation.

        Parameters
        ----------
        action:
            One of ``"set"``, ``"get"``, ``"delete"``, ``"list"``, ``"clear"``.
        key:
            Memory key (required for set / get / delete).
        value:
            Value to store (required for set).

        Returns
        -------
        str
            Result string or an error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "set":
            return self._set(key, value)
        if action == "get":
            return self._get(key)
        if action == "delete":
            return self._delete(key)
        if action == "list":
            return self._list()
        if action == "clear":
            return self._clear()
        return f"Error: unknown action {action!r}. Use set, get, delete, list, or clear."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict[str, str]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return {str(k): str(v) for k, v in data.items()}
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _set(self, key: str, value: str) -> str:
        if not key:
            return "Error: key is required for set"
        self._data[key] = value
        self._save()
        return f"Stored {key!r}"

    def _get(self, key: str) -> str:
        if not key:
            return "Error: key is required for get"
        if key not in self._data:
            return f"Error: key {key!r} not found"
        return self._data[key]

    def _delete(self, key: str) -> str:
        if not key:
            return "Error: key is required for delete"
        if key not in self._data:
            return f"Error: key {key!r} not found"
        del self._data[key]
        self._save()
        return f"Deleted {key!r}"

    def _list(self) -> str:
        if not self._data:
            return "(no memories stored)"
        return "\n".join(sorted(self._data.keys()))

    def _clear(self) -> str:
        count = len(self._data)
        self._data.clear()
        self._save()
        return f"Cleared {count} entries"
