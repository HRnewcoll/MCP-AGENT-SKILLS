"""INI/config file skill – read, write, and manipulate INI-style config files.

Covers the "DevOps & Cloud" and "CLI Utilities" categories.
Uses Python stdlib ``configparser`` module only.

Supported actions
-----------------
read            Read a value from a config file.
write           Write a value to a config file (creates it if needed).
list_sections   List all sections in the config.
list_keys       List all keys in a section.
delete_key      Delete a key from a section.
delete_section  Delete an entire section.
get_all         Return all sections and key-value pairs.
to_json         Convert the entire config to JSON.
"""

from __future__ import annotations

import configparser
import io
import json
import os
from pathlib import Path


class IniConfigSkill:
    """Read, write, and manipulate INI/config files."""

    name = "ini_config"
    description = (
        "Manage INI-style configuration files. "
        "Supported actions: 'read' (path, section, key); "
        "'write' (path, section, key, value); "
        "'list_sections' (path); 'list_keys' (path, section); "
        "'delete_key' (path, section, key); "
        "'delete_section' (path, section); "
        "'get_all' (path); 'to_json' (path)."
    )

    def run(
        self,
        action: str,
        path: str = "",
        section: str = "",
        key: str = "",
        value: str = "",
    ) -> str:
        """
        Perform a config file operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        path:
            Path to the INI config file.
        section:
            Config section name (e.g. ``"database"``).
        key:
            Config key name.
        value:
            Value to write (for ``"write"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "read":
            return self._read(path, section, key)
        if action == "write":
            return self._write(path, section, key, value)
        if action == "list_sections":
            return self._list_sections(path)
        if action == "list_keys":
            return self._list_keys(path, section)
        if action == "delete_key":
            return self._delete_key(path, section, key)
        if action == "delete_section":
            return self._delete_section(path, section)
        if action == "get_all":
            return self._get_all(path)
        if action == "to_json":
            return self._to_json(path)
        return (
            f"Error: unknown action {action!r}. "
            "Use read, write, list_sections, list_keys, "
            "delete_key, delete_section, get_all, or to_json."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load(path: str) -> "configparser.ConfigParser | str":
        if not path:
            return "Error: path is required"
        cfg = configparser.ConfigParser()
        p = Path(path)
        if p.exists():
            try:
                cfg.read(path, encoding="utf-8")
            except configparser.Error as exc:
                return f"Error: {exc}"
        return cfg

    def _read(self, path: str, section: str, key: str) -> str:
        if not section:
            return "Error: section is required for read"
        if not key:
            return "Error: key is required for read"
        result = self._load(path)
        if isinstance(result, str):
            return result
        cfg = result
        if not cfg.has_section(section):
            return f"Error: section [{section}] not found"
        if not cfg.has_option(section, key):
            return f"Error: key '{key}' not found in [{section}]"
        return cfg.get(section, key)

    def _write(self, path: str, section: str, key: str, value: str) -> str:
        if not path:
            return "Error: path is required for write"
        if not section:
            return "Error: section is required for write"
        if not key:
            return "Error: key is required for write"
        result = self._load(path)
        if isinstance(result, str):
            return result
        cfg = result
        if not cfg.has_section(section):
            cfg.add_section(section)
        cfg.set(section, key, value)
        try:
            with open(path, "w", encoding="utf-8") as f:
                cfg.write(f)
        except OSError as exc:
            return f"Error: {exc}"
        return f"Set [{section}] {key} = {value!r}"

    def _list_sections(self, path: str) -> str:
        result = self._load(path)
        if isinstance(result, str):
            return result
        sections = result.sections()
        if not sections:
            return "(no sections)"
        return "Sections: " + ", ".join(sections)

    def _list_keys(self, path: str, section: str) -> str:
        if not section:
            return "Error: section is required for list_keys"
        result = self._load(path)
        if isinstance(result, str):
            return result
        cfg = result
        if not cfg.has_section(section):
            return f"Error: section [{section}] not found"
        items = cfg.items(section)
        if not items:
            return f"(no keys in [{section}])"
        return "\n".join(f"  {k} = {v}" for k, v in items)

    def _delete_key(self, path: str, section: str, key: str) -> str:
        if not path or not section or not key:
            return "Error: path, section, and key are required for delete_key"
        result = self._load(path)
        if isinstance(result, str):
            return result
        cfg = result
        if not cfg.has_section(section):
            return f"Error: section [{section}] not found"
        if not cfg.remove_option(section, key):
            return f"Error: key '{key}' not found in [{section}]"
        with open(path, "w", encoding="utf-8") as f:
            cfg.write(f)
        return f"Deleted [{section}] {key}"

    def _delete_section(self, path: str, section: str) -> str:
        if not path or not section:
            return "Error: path and section are required for delete_section"
        result = self._load(path)
        if isinstance(result, str):
            return result
        cfg = result
        if not cfg.remove_section(section):
            return f"Error: section [{section}] not found"
        with open(path, "w", encoding="utf-8") as f:
            cfg.write(f)
        return f"Deleted section [{section}]"

    def _get_all(self, path: str) -> str:
        result = self._load(path)
        if isinstance(result, str):
            return result
        cfg = result
        if not cfg.sections():
            return "(empty config)"
        lines = []
        for section in cfg.sections():
            lines.append(f"[{section}]")
            for k, v in cfg.items(section):
                lines.append(f"  {k} = {v}")
        return "\n".join(lines)

    def _to_json(self, path: str) -> str:
        result = self._load(path)
        if isinstance(result, str):
            return result
        cfg = result
        data = {section: dict(cfg.items(section)) for section in cfg.sections()}
        return json.dumps(data, ensure_ascii=False, indent=2)
