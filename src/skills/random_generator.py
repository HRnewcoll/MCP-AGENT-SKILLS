"""Random generator skill – generate UUIDs, passwords, random numbers and more."""

from __future__ import annotations

import random
import secrets
import string
import uuid


class RandomGeneratorSkill:
    """Generate random values: UUIDs, passwords, numbers, hex tokens, and more."""

    name = "random_generator"
    description = (
        "Generate random values. "
        "Supported actions: 'uuid' (UUID4), 'uuid1' (UUID1), "
        "'password' (secure random password), 'hex' (random hex token), "
        "'integer' (random int in range), 'float' (random float in range), "
        "'choice' (pick random item from newline-separated list), "
        "'shuffle' (shuffle newline-separated items)."
    )

    def run(
        self,
        action: str,
        length: int = 16,
        min_val: float = 0,
        max_val: float = 100,
        items: str = "",
        include_symbols: bool = True,
    ) -> str:
        """
        Generate a random value.

        Parameters
        ----------
        action:
            Generation action (see description for full list).
        length:
            Length of password or hex token (default 16).
        min_val:
            Minimum value for integer / float actions (default 0).
        max_val:
            Maximum value for integer / float actions (default 100).
        items:
            Newline-separated list of items for 'choice' and 'shuffle'.
        include_symbols:
            Include punctuation symbols in generated passwords (default True).

        Returns
        -------
        str
            Generated value or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "uuid":
            return str(uuid.uuid4())
        if action == "uuid1":
            return str(uuid.uuid1())
        if action == "hex":
            return secrets.token_hex(max(1, length // 2))
        if action == "password":
            return self._password(length, include_symbols)
        if action == "integer":
            lo, hi = int(min_val), int(max_val)
            if lo > hi:
                return "Error: min_val must be <= max_val"
            return str(secrets.randbelow(hi - lo + 1) + lo)
        if action == "float":
            if min_val > max_val:
                return "Error: min_val must be <= max_val"
            return str(random.uniform(min_val, max_val))
        if action == "choice":
            choices = [i.strip() for i in items.splitlines() if i.strip()]
            if not choices:
                return "Error: items are required for choice"
            return secrets.choice(choices)
        if action == "shuffle":
            lines = [ln for ln in items.splitlines() if ln.strip()]
            if not lines:
                return "Error: items are required for shuffle"
            random.shuffle(lines)
            return "\n".join(lines)
        return (
            f"Error: unknown action {action!r}. "
            "Use uuid, uuid1, hex, password, integer, float, choice, or shuffle."
        )

    @staticmethod
    def _password(length: int, include_symbols: bool) -> str:
        if length < 4:
            return "Error: password length must be at least 4"
        alphabet = string.ascii_letters + string.digits
        if include_symbols:
            alphabet += string.punctuation
        return "".join(secrets.choice(alphabet) for _ in range(length))
