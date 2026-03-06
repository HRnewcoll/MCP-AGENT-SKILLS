"""Disclawd skill – a local Discord-like messaging interface for AI agent swarms.

Disclawd gives humans and AI agents a shared, channel-based communication
space without any external APIs.  All data is stored locally as JSON.

Concepts
--------
Server
    A top-level workspace (analogous to a Discord "server" / guild).
    Typically one server per project.
Channel
    A named topic within a server (e.g. ``#general``, ``#dev``, ``#testing``).
Message
    A timestamped post from an author (human or agent) in a channel.

Supported actions
-----------------
create_server   name=<str>
    Create a new server workspace.
list_servers
    List all servers.
create_channel  server=<str>  channel=<str>
    Create a channel inside a server.
list_channels   server=<str>
    List all channels in a server.
post_message    server=<str>  channel=<str>  author=<str>  message=<str>
    Post a message to a channel.
read_channel    server=<str>  channel=<str>  [limit=<int>]
    Read recent messages from a channel (newest last, default last 20).
list_messages   server=<str>  channel=<str>
    Alias for read_channel with no limit.
delete_server   server=<str>
    Remove a server and all its channels/messages.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

_DEFAULT_LIMIT = 20


class _Message(TypedDict):
    id: int
    author: str
    content: str
    timestamp: str


class _Channel(TypedDict):
    name: str
    created_at: str
    messages: list[_Message]


class _Server(TypedDict):
    name: str
    created_at: str
    channels: dict[str, _Channel]


class _DisclawdStore(TypedDict):
    servers: dict[str, _Server]


class DisclawdSkill:
    """Local Discord-like messaging interface for AI agents and humans."""

    name = "disclawd"
    description = (
        "Local Discord-like messaging interface for AI agents and humans. "
        "Supported actions: 'create_server' (name=<str>); "
        "'list_servers'; "
        "'create_channel' (server=<str>, channel=<str>); "
        "'list_channels' (server=<str>); "
        "'post_message' (server=<str>, channel=<str>, author=<str>, message=<str>); "
        "'read_channel' (server=<str>, channel=<str>, limit=<int>); "
        "'list_messages' (server=<str>, channel=<str>); "
        "'delete_server' (server=<str>)."
    )

    def __init__(self, store_path: str | os.PathLike = ".disclawd.json") -> None:
        self._path = Path(store_path)
        self._store: _DisclawdStore = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        name: str = "",
        server: str = "",
        channel: str = "",
        author: str = "",
        message: str = "",
        limit: int = _DEFAULT_LIMIT,
    ) -> str:
        """
        Perform a Disclawd operation.

        Parameters
        ----------
        action:
            One of ``"create_server"``, ``"list_servers"``,
            ``"create_channel"``, ``"list_channels"``,
            ``"post_message"``, ``"read_channel"``,
            ``"list_messages"``, ``"delete_server"``.
        name:
            Server name (used by *create_server*).
        server:
            Server identifier (most actions).
        channel:
            Channel name within the server.
        author:
            Message author (human name or agent role/name).
        message:
            Message content (for *post_message*).
        limit:
            Max number of messages to return (for *read_channel*).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "create_server":
            return self._create_server(name)
        if action == "list_servers":
            return self._list_servers()
        if action == "create_channel":
            return self._create_channel(server, channel)
        if action == "list_channels":
            return self._list_channels(server)
        if action == "post_message":
            return self._post_message(server, channel, author, message)
        if action in ("read_channel", "list_messages"):
            return self._read_channel(server, channel, limit)
        if action == "delete_server":
            return self._delete_server(server)
        return (
            f"Error: unknown action {action!r}. "
            "Use create_server, list_servers, create_channel, list_channels, "
            "post_message, read_channel, list_messages, or delete_server."
        )

    # ------------------------------------------------------------------
    # Action implementations
    # ------------------------------------------------------------------

    def _create_server(self, name: str) -> str:
        if not name:
            return "Error: name is required for create_server"
        name = name.strip()
        if name in self._store["servers"]:
            return f"Error: server {name!r} already exists"
        now = _now()
        self._store["servers"][name] = {
            "name": name,
            "created_at": now,
            "channels": {},
        }
        self._save()
        return f"Created server: {name!r}"

    def _list_servers(self) -> str:
        servers = self._store["servers"]
        if not servers:
            return "(no servers)"
        lines = ["Servers:"]
        for s in servers.values():
            ch_count = len(s["channels"])
            lines.append(f"  {s['name']}  ({ch_count} channel(s), created {s['created_at']})")
        return "\n".join(lines)

    def _create_channel(self, server: str, channel: str) -> str:
        srv = self._get_server(server)
        if isinstance(srv, str):
            return srv  # error string
        if not channel:
            return "Error: channel name is required"
        channel = channel.strip().lower().replace(" ", "-")
        if channel in srv["channels"]:
            return f"Error: channel #{channel} already exists in {server!r}"
        now = _now()
        srv["channels"][channel] = {
            "name": channel,
            "created_at": now,
            "messages": [],
        }
        self._save()
        return f"Created channel #{channel} in server {server!r}"

    def _list_channels(self, server: str) -> str:
        srv = self._get_server(server)
        if isinstance(srv, str):
            return srv
        channels = srv["channels"]
        if not channels:
            return f"(no channels in {server!r})"
        lines = [f"Channels in {server!r}:"]
        for ch in channels.values():
            msg_count = len(ch["messages"])
            lines.append(f"  #{ch['name']}  ({msg_count} message(s))")
        return "\n".join(lines)

    def _post_message(
        self, server: str, channel: str, author: str, message: str
    ) -> str:
        ch = self._get_channel(server, channel)
        if isinstance(ch, str):
            return ch
        if not author:
            return "Error: author is required"
        if not message:
            return "Error: message content is required"
        msg_id = (max((m["id"] for m in ch["messages"]), default=0) + 1)
        entry: _Message = {
            "id": msg_id,
            "author": author,
            "content": message,
            "timestamp": _now(),
        }
        ch["messages"].append(entry)
        self._save()
        return f"[#{channel}] {author}: {message}"

    def _read_channel(self, server: str, channel: str, limit: int) -> str:
        ch = self._get_channel(server, channel)
        if isinstance(ch, str):
            return ch
        messages = ch["messages"]
        if not messages:
            return f"(no messages in #{channel})"
        if limit and limit > 0:
            messages = messages[-limit:]
        lines = [f"#{channel} ({server}) – last {len(messages)} message(s):"]
        lines.append("-" * 60)
        for m in messages:
            lines.append(f"[{m['timestamp']}] {m['author']}: {m['content']}")
        return "\n".join(lines)

    def _delete_server(self, server: str) -> str:
        if not server:
            return "Error: server name is required"
        if server not in self._store["servers"]:
            return f"Error: server {server!r} not found"
        del self._store["servers"][server]
        self._save()
        return f"Deleted server: {server!r}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_server(self, server: str) -> _Server | str:
        if not server:
            return "Error: server name is required"
        srv = self._store["servers"].get(server)
        if srv is None:
            return f"Error: server {server!r} not found"
        return srv

    def _get_channel(self, server: str, channel: str) -> _Channel | str:
        srv = self._get_server(server)
        if isinstance(srv, str):
            return srv
        if not channel:
            return "Error: channel name is required"
        channel = channel.strip().lower().replace(" ", "-")
        ch = srv["channels"].get(channel)
        if ch is None:
            return f"Error: channel #{channel} not found in {server!r}"
        return ch

    def _load(self) -> _DisclawdStore:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "servers" in data:
                    return data  # type: ignore[return-value]
            except (json.JSONDecodeError, OSError):
                pass
        return {"servers": {}}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._store, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
