"""Dice roller skill – roll dice with various configurations and modifiers.

Covers the "Gaming" category.
Uses Python stdlib ``secrets`` module for cryptographically random rolls.

Supported actions
-----------------
roll            Roll dice using standard notation (e.g. '2d6', '1d20+5').
stats           Show statistical properties of a dice expression.
roll_multiple   Roll the same expression multiple times.
fate            Roll four Fate/Fudge dice (−, blank, +).
custom          Roll a custom die with specified faces.
"""

from __future__ import annotations

import re
import secrets


_DICE_RE = re.compile(
    r"^(\d+)?d(\d+)([+-]\d+)?$",
    re.IGNORECASE,
)


def _parse_dice(expr: str) -> tuple[int, int, int]:
    """Return (count, sides, modifier) from a dice expression like '2d6+3'."""
    m = _DICE_RE.match(expr.strip().replace(" ", ""))
    if not m:
        raise ValueError(f"Invalid dice expression: {expr!r}")
    count = int(m.group(1)) if m.group(1) else 1
    sides = int(m.group(2))
    modifier = int(m.group(3)) if m.group(3) else 0
    if count < 1 or count > 1000:
        raise ValueError(f"Dice count must be 1–1000 (got {count})")
    if sides < 2 or sides > 10000:
        raise ValueError(f"Sides must be 2–10000 (got {sides})")
    return count, sides, modifier


class DiceRollerSkill:
    """Roll polyhedral dice with standard notation."""

    name = "dice_roller"
    description = (
        "Roll dice using standard notation. "
        "Supported actions: 'roll' (expression – e.g. '2d6+3', '1d20', '4d10-2'); "
        "'stats' (expression); "
        "'roll_multiple' (expression, times=5); "
        "'fate' (description='Fate dice roll'); "
        "'custom' (faces – comma-separated face values, count=1)."
    )

    def run(
        self,
        action: str,
        expression: str = "1d6",
        times: int = 5,
        faces: str = "",
        count: int = 1,
    ) -> str:
        """
        Perform a dice roll.

        Parameters
        ----------
        action:
            One of ``"roll"``, ``"stats"``, ``"roll_multiple"``,
            ``"fate"``, ``"custom"``.
        expression:
            Dice notation, e.g. ``"2d6+3"`` (default ``"1d6"``).
        times:
            How many times to roll for ``"roll_multiple"`` (default 5).
        faces:
            Comma-separated face values for ``"custom"`` (e.g. ``"1,2,3,6,6,6"``).
        count:
            Number of custom dice to roll (default 1).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "roll":
                return self._roll(expression)
            if action == "stats":
                return self._stats(expression)
            if action == "roll_multiple":
                return self._roll_multiple(expression, int(times))
            if action == "fate":
                return self._fate()
            if action == "custom":
                return self._custom(faces, int(count))
        except (ValueError, TypeError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use roll, stats, roll_multiple, fate, or custom."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _roll(expr: str) -> str:
        n, sides, mod = _parse_dice(expr)
        rolls = [secrets.randbelow(sides) + 1 for _ in range(n)]
        total = sum(rolls) + mod
        rolls_str = ", ".join(str(r) for r in rolls)
        expr_clean = expr.replace(" ", "")
        mod_str = f" + {mod}" if mod > 0 else (f" − {abs(mod)}" if mod < 0 else "")
        return (
            f"🎲 {expr_clean}: [{rolls_str}]{mod_str} = {total}"
        )

    @staticmethod
    def _stats(expr: str) -> str:
        n, sides, mod = _parse_dice(expr)
        minimum = n * 1 + mod
        maximum = n * sides + mod
        avg = n * (sides + 1) / 2 + mod
        return (
            f"Expression: {expr}\n"
            f"Dice      : {n}d{sides}\n"
            f"Modifier  : {mod:+d}\n"
            f"Min       : {minimum}\n"
            f"Max       : {maximum}\n"
            f"Average   : {avg:.1f}"
        )

    @staticmethod
    def _roll_multiple(expr: str, times: int) -> str:
        times = max(1, min(int(times), 100))
        n, sides, mod = _parse_dice(expr)
        results: list[int] = []
        for _ in range(times):
            rolls = [secrets.randbelow(sides) + 1 for _ in range(n)]
            results.append(sum(rolls) + mod)
        avg = sum(results) / len(results)
        return (
            f"{times} rolls of {expr}:\n"
            f"Results : {', '.join(str(r) for r in results)}\n"
            f"Min     : {min(results)}  Max: {max(results)}  Avg: {avg:.1f}"
        )

    @staticmethod
    def _fate() -> str:
        _FATE_FACES = ["-", "-", " ", " ", "+", "+"]
        rolls = [secrets.choice(_FATE_FACES) for _ in range(4)]
        plus = rolls.count("+")
        minus = rolls.count("-")
        total = plus - minus
        return f"Fate dice: [{' '.join(rolls)}]  Total: {total:+d}"

    @staticmethod
    def _custom(faces: str, count: int) -> str:
        if not faces:
            return "Error: faces is required for custom"
        face_list = [f.strip() for f in faces.split(",") if f.strip()]
        if len(face_list) < 2:
            return "Error: at least 2 faces required"
        count = max(1, min(int(count), 100))
        results = [secrets.choice(face_list) for _ in range(count)]
        return f"Custom die ({len(face_list)} faces) ×{count}: {', '.join(results)}"
