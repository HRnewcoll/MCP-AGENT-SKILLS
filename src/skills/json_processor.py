"""JSON processor skill – parse, query and manipulate JSON data."""

from __future__ import annotations

import json


class JsonProcessorSkill:
    """Parse, query, and manipulate JSON data using dot-notation paths."""

    name = "json_processor"
    description = (
        "Parse, query and manipulate JSON data. "
        "Supported actions: 'parse' (validate + pretty-print), "
        "'get' (get value by dot-notation path), "
        "'set' (set value at dot-notation path), "
        "'delete' (remove a key at path), "
        "'keys' (list keys at path), "
        "'type' (get JSON type at path), "
        "'flatten' (flatten nested object to dot-notation pairs)."
    )

    def run(
        self,
        action: str,
        data: str = "",
        path: str = "",
        value: str = "",
    ) -> str:
        """
        Perform a JSON operation.

        Parameters
        ----------
        action:
            One of ``"parse"``, ``"get"``, ``"set"``, ``"delete"``,
            ``"keys"``, ``"type"``, ``"flatten"``.
        data:
            JSON string to operate on.
        path:
            Dot-notation key path (e.g. ``"user.address.city"``).
        value:
            JSON-encoded value to write (for 'set' action).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if not data:
            return "Error: data is required"

        try:
            obj = json.loads(data)
        except json.JSONDecodeError as exc:
            return f"Error: invalid JSON – {exc}"

        if action == "parse":
            return json.dumps(obj, indent=2, ensure_ascii=False)
        if action == "get":
            return self._get(obj, path)
        if action == "set":
            return self._set(obj, path, value)
        if action == "delete":
            return self._delete(obj, path)
        if action == "keys":
            return self._keys(obj, path)
        if action == "type":
            return self._type(obj, path)
        if action == "flatten":
            return self._flatten(obj)
        return (
            f"Error: unknown action {action!r}. "
            "Use parse, get, set, delete, keys, type, or flatten."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _navigate(obj: object, path: str) -> tuple[object, str]:
        """Navigate to the parent of the last path segment.

        Returns ``(parent_container, last_key)``.
        Raises ``KeyError`` or ``IndexError`` when a segment is missing.
        """
        keys = path.split(".")
        current: object = obj
        for key in keys[:-1]:
            if isinstance(current, dict):
                if key not in current:
                    raise KeyError(key)
                current = current[key]
            elif isinstance(current, list):
                try:
                    current = current[int(key)]
                except (ValueError, IndexError):
                    raise KeyError(key)
            else:
                raise KeyError(key)
        return current, keys[-1]

    def _get(self, obj: object, path: str) -> str:
        if not path:
            return json.dumps(obj, ensure_ascii=False)
        try:
            parent, last_key = self._navigate(obj, path)
            if isinstance(parent, dict):
                if last_key not in parent:
                    return f"Error: key {path!r} not found"
                val = parent[last_key]
            elif isinstance(parent, list):
                try:
                    val = parent[int(last_key)]
                except (ValueError, IndexError):
                    return f"Error: index {last_key!r} out of range"
            else:
                return f"Error: cannot index into {type(parent).__name__}"
            return json.dumps(val, ensure_ascii=False)
        except KeyError as exc:
            return f"Error: key {exc} not found"

    def _set(self, obj: object, path: str, value: str) -> str:
        if not path:
            return "Error: path is required for set"
        try:
            new_val = json.loads(value) if value else None
        except json.JSONDecodeError as exc:
            return f"Error: invalid value JSON – {exc}"
        try:
            parent, last_key = self._navigate(obj, path)
            if isinstance(parent, dict):
                parent[last_key] = new_val  # type: ignore[index]
            elif isinstance(parent, list):
                parent[int(last_key)] = new_val  # type: ignore[index]
            else:
                return f"Error: cannot set on {type(parent).__name__}"
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except KeyError as exc:
            return f"Error: key {exc} not found"
        except (ValueError, IndexError) as exc:
            return f"Error: {exc}"

    def _delete(self, obj: object, path: str) -> str:
        if not path:
            return "Error: path is required for delete"
        try:
            parent, last_key = self._navigate(obj, path)
            if isinstance(parent, dict):
                if last_key not in parent:
                    return f"Error: key {path!r} not found"
                del parent[last_key]  # type: ignore[arg-type]
            elif isinstance(parent, list):
                try:
                    del parent[int(last_key)]  # type: ignore[arg-type]
                except (ValueError, IndexError) as exc:
                    return f"Error: {exc}"
            else:
                return f"Error: cannot delete from {type(parent).__name__}"
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except KeyError as exc:
            return f"Error: key {exc} not found"

    def _keys(self, obj: object, path: str) -> str:
        target: object = obj
        if path:
            result = self._get(obj, path)
            try:
                target = json.loads(result)
            except (json.JSONDecodeError, Exception):
                return result  # propagate error string
        if isinstance(target, dict):
            return "\n".join(sorted(target.keys()))
        if isinstance(target, list):
            return f"Array of {len(target)} item(s)"
        return f"Error: target at {path!r} is not an object or array"

    def _type(self, obj: object, path: str) -> str:
        target: object = obj
        if path:
            result = self._get(obj, path)
            if result.startswith("Error:"):
                return result
            try:
                target = json.loads(result)
            except json.JSONDecodeError:
                target = result
        type_map: dict = {
            dict: "object",
            list: "array",
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            type(None): "null",
        }
        return type_map.get(type(target), type(target).__name__)

    @staticmethod
    def _flatten(obj: object) -> str:
        results: list[str] = []

        def _recurse(current: object, key: str) -> None:
            if isinstance(current, dict):
                for k, v in current.items():
                    _recurse(v, f"{key}.{k}" if key else k)
            elif isinstance(current, list):
                for i, v in enumerate(current):
                    _recurse(v, f"{key}.{i}" if key else str(i))
            else:
                results.append(f"{key}: {json.dumps(current, ensure_ascii=False)}")

        _recurse(obj, "")
        return "\n".join(results) if results else "(empty)"
