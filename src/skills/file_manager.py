"""File manager skill – read, write and list files within a sandbox directory."""

import os
from pathlib import Path


class FileManagerSkill:
    """Read, write, and list files within a sandboxed root directory."""

    name = "file_manager"
    description = (
        "Manage files within a sandboxed directory. "
        "Supported actions: 'read', 'write', 'list', 'delete'."
    )

    def __init__(self, root: str | os.PathLike = ".") -> None:
        self._root = Path(root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def run(self, action: str, path: str = "", content: str = "") -> str:
        """
        Perform a file operation.

        Parameters
        ----------
        action:
            One of ``"read"``, ``"write"``, ``"list"``, ``"delete"``.
        path:
            Relative path within the sandbox (required for read/write/delete).
        content:
            File content when *action* is ``"write"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "list":
            return self._list(path)
        if action == "read":
            return self._read(path)
        if action == "write":
            return self._write(path, content)
        if action == "delete":
            return self._delete(path)
        return f"Error: unknown action {action!r}. Use read, write, list, or delete."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _safe_path(self, relative: str) -> Path | None:
        """Resolve *relative* inside the sandbox; return None if escaping."""
        resolved = (self._root / relative).resolve()
        try:
            resolved.relative_to(self._root)
        except ValueError:
            return None
        return resolved

    def _list(self, sub: str = "") -> str:
        base = self._safe_path(sub) if sub else self._root
        if base is None:
            return "Error: path escapes sandbox"
        if not base.exists():
            return f"Error: directory {sub!r} does not exist"
        entries = sorted(
            ("[dir] " + p.name if p.is_dir() else p.name)
            for p in base.iterdir()
        )
        return "\n".join(entries) if entries else "(empty)"

    def _read(self, relative: str) -> str:
        if not relative:
            return "Error: path is required for read"
        target = self._safe_path(relative)
        if target is None:
            return "Error: path escapes sandbox"
        if not target.exists():
            return f"Error: file {relative!r} does not exist"
        if not target.is_file():
            return f"Error: {relative!r} is not a file"
        return target.read_text(encoding="utf-8")

    def _write(self, relative: str, content: str) -> str:
        if not relative:
            return "Error: path is required for write"
        target = self._safe_path(relative)
        if target is None:
            return "Error: path escapes sandbox"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Written {len(content)} bytes to {relative!r}"

    def _delete(self, relative: str) -> str:
        if not relative:
            return "Error: path is required for delete"
        target = self._safe_path(relative)
        if target is None:
            return "Error: path escapes sandbox"
        if not target.exists():
            return f"Error: {relative!r} does not exist"
        if target.is_dir():
            return "Error: delete only supports files, not directories"
        target.unlink()
        return f"Deleted {relative!r}"
