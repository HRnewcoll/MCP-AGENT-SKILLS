"""Mind map skill – build and visualise simple text-based mind maps.

Covers the "Notes & PKM" and "Personal Development" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
create_map      Create a new mind map with a central idea.
list_maps       List all mind maps.
add_node        Add a child node to a parent node in a map.
view            View a mind map as a text tree.
delete_node     Remove a node (and all its children) from a map.
delete_map      Delete an entire mind map.
search          Search for a node across all maps.
clear           Delete all mind maps.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Node(TypedDict):
    id: str
    text: str
    children: list["_Node"]


class _Map(TypedDict):
    name: str
    root: _Node
    created_at: str


class MindMapSkill:
    """Build and visualise simple text-based mind maps."""

    name = "mind_map"
    description = (
        "Create and manage text-based mind maps. "
        "Supported actions: 'create_map' (map_name, central_idea); "
        "'list_maps'; 'add_node' (map_name, parent_text, node_text); "
        "'view' (map_name); 'delete_node' (map_name, node_text); "
        "'delete_map' (map_name); 'search' (query); 'clear'."
    )

    def __init__(self, store_path: str | os.PathLike = ".mindmaps.json") -> None:
        self._path = Path(store_path)
        self._maps: dict[str, _Map] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        map_name: str = "",
        central_idea: str = "",
        parent_text: str = "",
        node_text: str = "",
        query: str = "",
    ) -> str:
        """
        Perform a mind map operation.

        Parameters
        ----------
        action:
            One of ``"create_map"``, ``"list_maps"``, ``"add_node"``,
            ``"view"``, ``"delete_node"``, ``"delete_map"``,
            ``"search"``, ``"clear"``.
        map_name:
            Name of the mind map.
        central_idea:
            Text for the root node (for ``"create_map"``).
        parent_text:
            Text of the parent node to add a child to (for ``"add_node"``).
        node_text:
            Text of the new node (for ``"add_node"``/``"delete_node"``).
        query:
            Text to search for across all maps (for ``"search"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "create_map":
            return self._create_map(map_name, central_idea)
        if action == "list_maps":
            return self._list_maps()
        if action == "add_node":
            return self._add_node(map_name, parent_text, node_text)
        if action == "view":
            return self._view(map_name)
        if action == "delete_node":
            return self._delete_node(map_name, node_text)
        if action == "delete_map":
            return self._delete_map(map_name)
        if action == "search":
            return self._search(query)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use create_map, list_maps, add_node, view, delete_node, "
            "delete_map, search, or clear."
        )

    # ------------------------------------------------------------------

    def _create_map(self, map_name: str, central_idea: str) -> str:
        if not map_name:
            return "Error: map_name is required for create_map"
        if not central_idea:
            return "Error: central_idea is required for create_map"
        if map_name in self._maps:
            return f"Error: mind map '{map_name}' already exists"
        root: _Node = {"id": "root", "text": central_idea, "children": []}
        mind_map: _Map = {
            "name": map_name,
            "root": root,
            "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._maps[map_name] = mind_map
        self._save()
        return f"Created mind map '{map_name}' with central idea: {central_idea!r}"

    def _list_maps(self) -> str:
        if not self._maps:
            return "(no mind maps)"
        lines = []
        for name, m in self._maps.items():
            count = self._count_nodes(m["root"])
            lines.append(f"  '{name}'  ({count} node(s))  root: {m['root']['text']!r}")
        return "Mind maps:\n" + "\n".join(lines)

    def _add_node(self, map_name: str, parent_text: str, node_text: str) -> str:
        if not map_name:
            return "Error: map_name is required"
        if not node_text:
            return "Error: node_text is required for add_node"
        m = self._maps.get(map_name)
        if m is None:
            return f"Error: mind map '{map_name}' not found"
        parent = parent_text.strip() if parent_text.strip() else m["root"]["text"]
        parent_node = self._find_node(m["root"], parent)
        if parent_node is None:
            return f"Error: parent node {parent!r} not found in '{map_name}'"
        new_node: _Node = {
            "id": f"n{self._count_nodes(m['root'])}",
            "text": node_text,
            "children": [],
        }
        parent_node["children"].append(new_node)
        self._save()
        return f"Added node {node_text!r} under {parent_node['text']!r} in '{map_name}'"

    def _view(self, map_name: str) -> str:
        if not map_name:
            return "Error: map_name is required for view"
        m = self._maps.get(map_name)
        if m is None:
            return f"Error: mind map '{map_name}' not found"
        lines = [f"Mind Map: {map_name}"]
        self._render_node(m["root"], lines, "", True)
        return "\n".join(lines)

    def _delete_node(self, map_name: str, node_text: str) -> str:
        if not map_name or not node_text:
            return "Error: map_name and node_text are required for delete_node"
        m = self._maps.get(map_name)
        if m is None:
            return f"Error: mind map '{map_name}' not found"
        if m["root"]["text"] == node_text:
            return "Error: cannot delete the root node; use delete_map instead"
        removed = self._remove_node(m["root"], node_text)
        if not removed:
            return f"Error: node {node_text!r} not found in '{map_name}'"
        self._save()
        return f"Deleted node {node_text!r} (and its children) from '{map_name}'"

    def _delete_map(self, map_name: str) -> str:
        if not map_name:
            return "Error: map_name is required for delete_map"
        if map_name not in self._maps:
            return f"Error: mind map '{map_name}' not found"
        del self._maps[map_name]
        self._save()
        return f"Deleted mind map '{map_name}'"

    def _search(self, query: str) -> str:
        if not query:
            return "Error: query is required for search"
        q = query.lower()
        results: list[str] = []
        for map_name, m in self._maps.items():
            hits = self._search_nodes(m["root"], q)
            for hit in hits:
                results.append(f"  '{map_name}' → {hit}")
        if not results:
            return f"No nodes matching {query!r}"
        return f"{len(results)} result(s) for {query!r}:\n" + "\n".join(results)

    def _clear(self) -> str:
        count = len(self._maps)
        self._maps.clear()
        self._save()
        return f"Cleared {count} mind map(s)"

    # ------------------------------------------------------------------
    # Tree helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _count_nodes(node: _Node) -> int:
        return 1 + sum(MindMapSkill._count_nodes(c) for c in node["children"])

    @staticmethod
    def _find_node(node: _Node, text: str) -> _Node | None:
        if node["text"] == text:
            return node
        for child in node["children"]:
            found = MindMapSkill._find_node(child, text)
            if found:
                return found
        return None

    @staticmethod
    def _remove_node(node: _Node, text: str) -> bool:
        for i, child in enumerate(node["children"]):
            if child["text"] == text:
                node["children"].pop(i)
                return True
            if MindMapSkill._remove_node(child, text):
                return True
        return False

    @staticmethod
    def _render_node(node: _Node, lines: list[str], prefix: str, is_last: bool) -> None:
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + node["text"])
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node["children"]):
            MindMapSkill._render_node(child, lines, child_prefix, i == len(node["children"]) - 1)

    @staticmethod
    def _search_nodes(node: _Node, query: str) -> list[str]:
        results = []
        if query in node["text"].lower():
            results.append(node["text"])
        for child in node["children"]:
            results.extend(MindMapSkill._search_nodes(child, query))
        return results

    def _load(self) -> dict[str, _Map]:
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
            json.dumps(self._maps, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
