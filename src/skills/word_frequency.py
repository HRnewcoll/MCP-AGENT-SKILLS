"""Word frequency skill – analyse word frequencies in text.

Covers the "Data & Analytics" and "Search & Research" categories.
Uses Python stdlib only.

Supported actions
-----------------
count           Return word frequencies for all words (sorted by frequency).
top             Return the top-N most frequent words.
frequency       Return the frequency (count and %) of a specific word.
unique_count    Return the number of unique words.
common_words    Remove common stop-words and return top-N content words.
compare         Compare word frequencies between two texts.
"""

from __future__ import annotations

import re
from collections import Counter

_STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "must", "ought", "it", "its", "this", "that", "these", "those",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "they",
    "them", "his", "her", "their", "not", "no", "nor", "so", "yet",
    "both", "either", "neither", "as", "than", "then", "when", "where",
    "who", "which", "what", "how", "all", "each", "every", "some",
    "any", "few", "more", "most", "other", "such", "same", "just",
    "also", "very", "too", "now", "up", "out", "about", "into", "over",
})


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z']+\b", text.lower())


class WordFrequencySkill:
    """Analyse word frequencies in text."""

    name = "word_frequency"
    description = (
        "Analyse word frequencies in text. "
        "Supported actions: 'count' (text); 'top' (text, n=10); "
        "'frequency' (text, word); 'unique_count' (text); "
        "'common_words' (text, n=10); 'compare' (text, text2, n=10)."
    )

    def run(
        self,
        action: str,
        text: str = "",
        text2: str = "",
        word: str = "",
        n: int = 10,
    ) -> str:
        """
        Analyse word frequencies.

        Parameters
        ----------
        action:
            The analysis to perform (see description).
        text:
            Input text.
        text2:
            Second text for ``"compare"``.
        word:
            Specific word for ``"frequency"``.
        n:
            Number of top words to return (default 10).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "count":
            return self._count(text)
        if action == "top":
            return self._top(text, n)
        if action == "frequency":
            return self._frequency(text, word)
        if action == "unique_count":
            return self._unique_count(text)
        if action == "common_words":
            return self._common_words(text, n)
        if action == "compare":
            return self._compare(text, text2, n)
        return (
            f"Error: unknown action {action!r}. "
            "Use count, top, frequency, unique_count, common_words, or compare."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _count(text: str) -> str:
        if not text:
            return "Error: text is required"
        words = _tokenize(text)
        if not words:
            return "(no words found)"
        counts = Counter(words)
        lines = [f"{word}: {cnt}" for word, cnt in counts.most_common()]
        return "\n".join(lines)

    @staticmethod
    def _top(text: str, n: int) -> str:
        if not text:
            return "Error: text is required"
        words = _tokenize(text)
        if not words:
            return "(no words found)"
        n = max(1, min(int(n), len(words)))
        counts = Counter(words)
        total = len(words)
        lines = [f"Top {n} words (total: {total})"]
        for word, cnt in counts.most_common(n):
            pct = cnt / total * 100
            lines.append(f"  {word}: {cnt} ({pct:.1f}%)")
        return "\n".join(lines)

    @staticmethod
    def _frequency(text: str, word: str) -> str:
        if not text:
            return "Error: text is required"
        if not word:
            return "Error: word is required for frequency"
        words = _tokenize(text)
        w = word.lower().strip()
        cnt = sum(1 for t in words if t == w)
        total = len(words)
        if total == 0:
            return "(no words found)"
        pct = cnt / total * 100
        return f"'{w}': {cnt} occurrence(s) / {total} total words ({pct:.2f}%)"

    @staticmethod
    def _unique_count(text: str) -> str:
        if not text:
            return "Error: text is required"
        words = _tokenize(text)
        unique = len(set(words))
        total = len(words)
        return (
            f"Unique words : {unique}\n"
            f"Total words  : {total}\n"
            f"Lexical density: {unique / total * 100:.1f}%" if total else "(no words)"
        )

    @staticmethod
    def _common_words(text: str, n: int) -> str:
        if not text:
            return "Error: text is required"
        words = [w for w in _tokenize(text) if w not in _STOP_WORDS and len(w) > 1]
        if not words:
            return "(no content words found after removing stop-words)"
        n = max(1, min(int(n), len(words)))
        counts = Counter(words)
        total = sum(counts.values())
        lines = [f"Top {n} content words (stop-words excluded):"]
        for word, cnt in counts.most_common(n):
            lines.append(f"  {word}: {cnt} ({cnt / total * 100:.1f}%)")
        return "\n".join(lines)

    @staticmethod
    def _compare(text: str, text2: str, n: int) -> str:
        if not text:
            return "Error: text is required"
        if not text2:
            return "Error: text2 is required for compare"
        c1 = Counter(_tokenize(text))
        c2 = Counter(_tokenize(text2))
        all_words = (set(c1.keys()) | set(c2.keys()))
        n = max(1, min(int(n), len(all_words)))
        # Sort by combined count
        ranked = sorted(all_words, key=lambda w: c1[w] + c2[w], reverse=True)[:n]
        lines = [f"{'Word':<20} {'Text1':>8} {'Text2':>8}"]
        lines.append("-" * 40)
        for word in ranked:
            lines.append(f"{word:<20} {c1[word]:>8} {c2[word]:>8}")
        return "\n".join(lines)
