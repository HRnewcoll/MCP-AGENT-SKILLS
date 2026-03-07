"""Typing speed skill – WPM calculation, text generation and typing tests.

Covers the "Personal Development" and "Productivity & Tasks" categories.
Pure Python, no external libraries.

Supported actions
-----------------
calculate_wpm   Calculate WPM from character count and time.
calculate_cpm   Calculate CPM (characters per minute).
accuracy        Calculate typing accuracy from typed vs original text.
analyse         Full analysis: WPM, CPM, accuracy, errors.
sample_text     Return a sample typing practice text by difficulty.
"""

from __future__ import annotations

import re

_SAMPLES: dict[str, str] = {
    "easy": (
        "The quick brown fox jumps over the lazy dog. "
        "Pack my box with five dozen liquor jugs. "
        "How vexingly quick daft zebras jump."
    ),
    "medium": (
        "Programming is the art of telling another human being what one wants "
        "the computer to do. The best programs are the ones written when the "
        "programmer is supposed to be working on something else."
    ),
    "hard": (
        "Cryptographic hash functions provide deterministic one-way transformation "
        "of arbitrary-length input data into fixed-size digest values. "
        "Collision resistance, preimage resistance, and second-preimage resistance "
        "are the primary security properties that characterise a robust hash function."
    ),
    "code": (
        "def fibonacci(n: int) -> int:\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return fibonacci(n - 1) + fibonacci(n - 2)"
    ),
}


class TypingSpeedSkill:
    """Calculate WPM/CPM, measure accuracy, and provide typing practice text."""

    name = "typing_speed"
    description = (
        "Typing speed and accuracy utilities. "
        "Supported actions: 'calculate_wpm' (text, seconds); "
        "'calculate_cpm' (text, seconds); "
        "'accuracy' (original, typed); "
        "'analyse' (original, typed, seconds); "
        "'sample_text' (difficulty=easy/medium/hard/code)."
    )

    def run(
        self,
        action: str,
        text: str = "",
        original: str = "",
        typed: str = "",
        seconds: float = 0.0,
        difficulty: str = "medium",
    ) -> str:
        """
        Perform a typing speed operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        text:
            Text that was typed (for WPM/CPM calculations).
        original:
            The reference text (for accuracy checking).
        typed:
            What the user actually typed (for accuracy checking).
        seconds:
            Time taken in seconds.
        difficulty:
            Difficulty level for ``"sample_text"``
            (easy/medium/hard/code).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "calculate_wpm":
            return self._wpm(text, seconds)
        if action == "calculate_cpm":
            return self._cpm(text, seconds)
        if action == "accuracy":
            return self._accuracy(original or text, typed)
        if action == "analyse":
            return self._analyse(original or text, typed, seconds)
        if action == "sample_text":
            return self._sample(difficulty)
        return (
            f"Error: unknown action {action!r}. "
            "Use calculate_wpm, calculate_cpm, accuracy, analyse, or sample_text."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _wpm(text: str, seconds: float) -> str:
        if not text:
            return "Error: text is required"
        if seconds <= 0:
            return "Error: seconds must be > 0"
        words = len(text.split())
        wpm = (words / seconds) * 60
        return f"Words: {words}  Time: {seconds}s  WPM: {wpm:.1f}"

    @staticmethod
    def _cpm(text: str, seconds: float) -> str:
        if not text:
            return "Error: text is required"
        if seconds <= 0:
            return "Error: seconds must be > 0"
        chars = len(text)
        cpm = (chars / seconds) * 60
        return f"Chars: {chars}  Time: {seconds}s  CPM: {cpm:.1f}"

    @staticmethod
    def _accuracy(original: str, typed: str) -> str:
        if not original:
            return "Error: original text is required"
        if not typed:
            return "Error: typed text is required"
        orig_words = original.split()
        type_words = typed.split()
        correct = sum(1 for o, t in zip(orig_words, type_words) if o == t)
        total = max(len(orig_words), len(type_words))
        acc = correct / total * 100 if total else 100.0
        errors = total - correct
        return (
            f"Accuracy  : {acc:.1f}%\n"
            f"Correct   : {correct} word(s)\n"
            f"Errors    : {errors}\n"
            f"Total     : {total} word(s)"
        )

    def _analyse(self, original: str, typed: str, seconds: float) -> str:
        if not original:
            return "Error: original text is required"
        if not typed:
            return "Error: typed text is required"
        parts = ["=== Typing Analysis ==="]
        if seconds > 0:
            parts.append(self._wpm(typed, seconds))
            parts.append(self._cpm(typed, seconds))
        parts.append(self._accuracy(original, typed))
        return "\n".join(parts)

    @staticmethod
    def _sample(difficulty: str) -> str:
        key = difficulty.lower()
        text = _SAMPLES.get(key)
        if text is None:
            return f"Error: unknown difficulty {difficulty!r}. Use easy, medium, hard, or code."
        word_count = len(text.split())
        return (
            f"Sample text ({key}, {word_count} words):\n"
            f"{'─' * 40}\n"
            f"{text}"
        )
