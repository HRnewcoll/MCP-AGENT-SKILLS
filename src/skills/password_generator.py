"""Password generator skill – create strong passwords and passphrases.

Covers the "Security & Passwords" category from the
awesome-openclaw-skills directory.  Uses Python stdlib only
(``secrets``, ``string``).

Supported actions
-----------------
generate            Generate a random password.
generate_passphrase Generate a random word-based passphrase.
check_strength      Analyse the strength of an existing password.
"""

from __future__ import annotations

import re
import secrets
import string


# ---------------------------------------------------------------------------
# Built-in word list for passphrases (curated common English words)
# ---------------------------------------------------------------------------

_WORDS = [
    "apple", "bridge", "castle", "dragon", "eagle", "forest", "garden",
    "harbor", "island", "jungle", "kitten", "lemon", "mango", "needle",
    "ocean", "piano", "quartz", "river", "shield", "tiger", "umbrella",
    "violet", "walnut", "xenon", "yellow", "zebra", "amber", "breeze",
    "candle", "diamond", "ember", "flute", "goblin", "hollow", "ivory",
    "jewel", "kernel", "lantern", "marble", "nimble", "onyx", "pebble",
    "quarry", "ripple", "silver", "tunnel", "umber", "velvet", "warden",
    "xyster", "yarrow", "zenith", "acorn", "blaze", "copper", "dagger",
    "eclipse", "fern", "glacier", "hammer", "iron", "jasper", "kite",
    "lunar", "mosaic", "north", "opaque", "prism", "raven", "storm",
    "topaz", "uplift", "vision", "whisk", "xenolith", "yonder", "zephyr",
]


class PasswordGeneratorSkill:
    """Generate strong passwords and passphrases, and check password strength."""

    name = "password_generator"
    description = (
        "Generate secure passwords and check password strength. "
        "Supported actions: 'generate' (length, symbols, digits, uppercase, lowercase); "
        "'generate_passphrase' (words, separator); "
        "'check_strength' (password)."
    )

    def run(
        self,
        action: str,
        length: int = 16,
        symbols: bool = True,
        digits: bool = True,
        uppercase: bool = True,
        lowercase: bool = True,
        words: int = 4,
        separator: str = "-",
        password: str = "",
    ) -> str:
        """
        Perform a password operation.

        Parameters
        ----------
        action:
            One of ``"generate"``, ``"generate_passphrase"``,
            ``"check_strength"``.
        length:
            Password length for ``"generate"`` (default 16, min 4).
        symbols:
            Include symbols (``!@#$...``) in generated password
            (default ``True``).
        digits:
            Include digits 0-9 (default ``True``).
        uppercase:
            Include uppercase letters (default ``True``).
        lowercase:
            Include lowercase letters (default ``True``).
        words:
            Number of words in passphrase (default 4, max 12).
        separator:
            Word separator for passphrase (default ``"-"``).
        password:
            Password to analyse for ``"check_strength"``.

        Returns
        -------
        str
            Generated password / passphrase / strength report or
            error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "generate":
            return self._generate(length, symbols, digits, uppercase, lowercase)

        if action == "generate_passphrase":
            return self._generate_passphrase(words, separator)

        if action == "check_strength":
            return self._check_strength(password)

        return (
            f"Error: unknown action {action!r}. "
            "Use generate, generate_passphrase, or check_strength."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate(
        length: int,
        use_symbols: bool,
        use_digits: bool,
        use_upper: bool,
        use_lower: bool,
    ) -> str:
        length = max(4, min(256, int(length)))
        pool = ""
        required: list[str] = []

        if use_lower:
            pool += string.ascii_lowercase
            required.append(secrets.choice(string.ascii_lowercase))
        if use_upper:
            pool += string.ascii_uppercase
            required.append(secrets.choice(string.ascii_uppercase))
        if use_digits:
            pool += string.digits
            required.append(secrets.choice(string.digits))
        if use_symbols:
            sym = "!@#$%^&*()-_=+[]{}|;:,.<>?"
            pool += sym
            required.append(secrets.choice(sym))

        if not pool:
            return "Error: at least one character class must be enabled"

        remaining = length - len(required)
        chars = [secrets.choice(pool) for _ in range(max(0, remaining))]
        all_chars = required + chars
        # Fisher-Yates shuffle via secrets
        for i in range(len(all_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            all_chars[i], all_chars[j] = all_chars[j], all_chars[i]
        return "".join(all_chars)

    @staticmethod
    def _generate_passphrase(num_words: int, separator: str) -> str:
        num_words = max(2, min(12, int(num_words)))
        chosen = [secrets.choice(_WORDS) for _ in range(num_words)]
        return separator.join(chosen)

    @staticmethod
    def _check_strength(password: str) -> str:
        if not password:
            return "Error: password is required for check_strength"
        score = 0
        feedback: list[str] = []

        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Too short (< 8 chars)")

        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1

        if re.search(r"[a-z]", password):
            score += 1
        else:
            feedback.append("Add lowercase letters")

        if re.search(r"[A-Z]", password):
            score += 1
        else:
            feedback.append("Add uppercase letters")

        if re.search(r"\d", password):
            score += 1
        else:
            feedback.append("Add digits")

        if re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]", password):
            score += 1
        else:
            feedback.append("Add symbols")

        levels = {0: "Very weak", 1: "Very weak", 2: "Weak", 3: "Fair",
                  4: "Good", 5: "Strong", 6: "Very strong", 7: "Excellent"}
        rating = levels.get(min(score, 7), "Excellent")
        tips = "\n  ".join(feedback) if feedback else "No suggestions"
        return (
            f"Strength: {rating} (score {score}/7)\n"
            f"Length: {len(password)}\n"
            f"Suggestions:\n  {tips}"
        )
