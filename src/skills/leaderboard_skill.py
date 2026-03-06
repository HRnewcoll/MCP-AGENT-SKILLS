"""Leaderboard skill – manage ranked scoreboards for games and competitions.

Covers the "Gaming" and "Productivity & Tasks" categories.
All data persisted to a local JSON file.

Supported actions
-----------------
add_score       Record a score for a player.
list            Show the current leaderboard (sorted by score).
top             Show the top-N players.
get             Get all scores for a specific player.
delete_player   Remove a player and all their scores.
reset           Reset all scores for a board.
list_boards     List all leaderboards.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Score(TypedDict):
    player: str
    score: float
    timestamp: str
    note: str


class LeaderboardSkill:
    """Manage ranked scoreboards for games and competitions."""

    name = "leaderboard"
    description = (
        "Manage leaderboards and score tracking. "
        "Supported actions: 'add_score' (board, player, score, note); "
        "'list' (board); 'top' (board, n=10); "
        "'get' (board, player); 'delete_player' (board, player); "
        "'reset' (board); 'list_boards'."
    )

    def __init__(self, store_path: str | os.PathLike = ".leaderboards.json") -> None:
        self._path = Path(store_path)
        # Dict: board_name -> list of _Score
        self._data: dict[str, list[_Score]] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        board: str = "default",
        player: str = "",
        score: float = 0.0,
        note: str = "",
        n: int = 10,
    ) -> str:
        """
        Perform a leaderboard operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        board:
            Leaderboard name (default ``"default"``).
        player:
            Player name.
        score:
            Numeric score.
        note:
            Optional note (e.g. game mode, level).
        n:
            Number of top players to show for ``"top"`` (default 10).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "add_score":
            return self._add_score(board, player, score, note)
        if action == "list":
            return self._list(board)
        if action == "top":
            return self._top(board, n)
        if action == "get":
            return self._get(board, player)
        if action == "delete_player":
            return self._delete_player(board, player)
        if action == "reset":
            return self._reset(board)
        if action == "list_boards":
            return self._list_boards()
        return (
            f"Error: unknown action {action!r}. "
            "Use add_score, list, top, get, delete_player, reset, or list_boards."
        )

    # ------------------------------------------------------------------

    def _add_score(self, board: str, player: str, score: float, note: str) -> str:
        if not player:
            return "Error: player is required for add_score"
        entry: _Score = {
            "player": player,
            "score": float(score),
            "timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "note": note,
        }
        if board not in self._data:
            self._data[board] = []
        self._data[board].append(entry)
        self._save()
        return f"Recorded score {score} for '{player}' on board '{board}'"

    def _list(self, board: str) -> str:
        entries = self._get_board(board)
        if isinstance(entries, str):
            return entries
        ranked = self._rank(entries)
        lines = [f"Leaderboard: {board}"]
        for rank, entry in enumerate(ranked, 1):
            note = f"  ({entry['note']})" if entry["note"] else ""
            lines.append(f"  {rank}. {entry['player']}: {entry['score']}{note}")
        return "\n".join(lines)

    def _top(self, board: str, n: int) -> str:
        entries = self._get_board(board)
        if isinstance(entries, str):
            return entries
        n = max(1, min(int(n), len(entries)))
        ranked = self._rank(entries)[:n]
        lines = [f"Top {n} on leaderboard '{board}':"]
        for rank, entry in enumerate(ranked, 1):
            lines.append(f"  {rank}. {entry['player']}: {entry['score']}")
        return "\n".join(lines)

    def _get(self, board: str, player: str) -> str:
        if not player:
            return "Error: player is required for get"
        entries = self._get_board(board)
        if isinstance(entries, str):
            return entries
        player_scores = [e for e in entries if e["player"].lower() == player.lower()]
        if not player_scores:
            return f"No scores found for '{player}' on board '{board}'"
        best = max(player_scores, key=lambda e: e["score"])
        lines = [f"Scores for '{player}' on '{board}':"]
        for e in sorted(player_scores, key=lambda x: x["score"], reverse=True):
            note = f"  ({e['note']})" if e["note"] else ""
            lines.append(f"  {e['score']}{note} @ {e['timestamp']}")
        lines.append(f"Best score: {best['score']}")
        return "\n".join(lines)

    def _delete_player(self, board: str, player: str) -> str:
        if not player:
            return "Error: player is required for delete_player"
        entries = self._get_board(board)
        if isinstance(entries, str):
            return entries
        before = len(entries)
        self._data[board] = [
            e for e in entries if e["player"].lower() != player.lower()
        ]
        removed = before - len(self._data[board])
        if removed == 0:
            return f"No entries for '{player}' on board '{board}'"
        self._save()
        return f"Removed {removed} entry/entries for '{player}' from '{board}'"

    def _reset(self, board: str) -> str:
        if board not in self._data:
            return f"Board '{board}' not found"
        count = len(self._data[board])
        self._data[board] = []
        self._save()
        return f"Reset board '{board}' ({count} entries removed)"

    def _list_boards(self) -> str:
        if not self._data:
            return "(no leaderboards)"
        lines = []
        for name, entries in sorted(self._data.items()):
            lines.append(f"  {name}: {len(entries)} score(s)")
        return "Leaderboards:\n" + "\n".join(lines)

    def _get_board(self, board: str) -> "list[_Score] | str":
        if board not in self._data or not self._data[board]:
            return f"(leaderboard '{board}' is empty)"
        return self._data[board]

    @staticmethod
    def _rank(entries: list[_Score]) -> list[_Score]:
        """Return best score per player, sorted descending."""
        best: dict[str, _Score] = {}
        for e in entries:
            key = e["player"].lower()
            if key not in best or e["score"] > best[key]["score"]:
                best[key] = e
        return sorted(best.values(), key=lambda x: x["score"], reverse=True)

    def _load(self) -> dict[str, list[_Score]]:
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
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
