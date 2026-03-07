"""Fuzzy match skill – fuzzy string matching and similarity scoring.

Covers the "Data & Analytics" and "Search & Research" categories.
Pure Python, no external libraries.

Uses the Levenshtein distance algorithm for edit-based similarity
and the Jaro-Winkler metric for phonetic-style similarity.

Supported actions
-----------------
distance        Levenshtein edit distance between two strings.
similarity      Similarity ratio (0–1) between two strings.
best_match      Find the best match for a string in a list.
rank_matches    Rank all candidates by similarity to a query.
jaro            Jaro similarity (0–1).
jaro_winkler    Jaro-Winkler similarity (0–1, favours prefix matches).
"""

from __future__ import annotations


def _levenshtein(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance."""
    if s1 == s2:
        return 0
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1, 1):
        curr = [i] + [0] * len(s2)
        for j, c2 in enumerate(s2, 1):
            curr[j] = min(
                prev[j] + 1,        # deletion
                curr[j - 1] + 1,    # insertion
                prev[j - 1] + (0 if c1 == c2 else 1),  # substitution
            )
        prev = curr
    return prev[-1]


def _similarity(s1: str, s2: str) -> float:
    if not s1 and not s2:
        return 1.0
    dist = _levenshtein(s1.lower(), s2.lower())
    max_len = max(len(s1), len(s2))
    return 1.0 - dist / max_len


def _jaro(s1: str, s2: str) -> float:
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    match_dist = max(len1, len2) // 2 - 1
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0
    for i in range(len1):
        lo = max(0, i - match_dist)
        hi = min(i + match_dist + 1, len2)
        for j in range(lo, hi):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    return (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3.0


def _jaro_winkler(s1: str, s2: str, p: float = 0.1) -> float:
    jaro = _jaro(s1, s2)
    prefix = 0
    for a, b in zip(s1, s2):
        if a == b:
            prefix += 1
        else:
            break
        if prefix == 4:
            break
    return jaro + prefix * p * (1.0 - jaro)


class FuzzyMatchSkill:
    """Fuzzy string matching using Levenshtein distance and Jaro-Winkler."""

    name = "fuzzy_match"
    description = (
        "Fuzzy string matching and similarity. "
        "Supported actions: 'distance' (s1, s2); 'similarity' (s1, s2); "
        "'best_match' (query, candidates – comma-separated); "
        "'rank_matches' (query, candidates – comma-separated, top_n=10); "
        "'jaro' (s1, s2); 'jaro_winkler' (s1, s2)."
    )

    def run(
        self,
        action: str,
        s1: str = "",
        s2: str = "",
        query: str = "",
        candidates: str = "",
        top_n: int = 10,
    ) -> str:
        """
        Perform a fuzzy matching operation.

        Parameters
        ----------
        action:
            One of ``"distance"``, ``"similarity"``, ``"best_match"``,
            ``"rank_matches"``, ``"jaro"``, ``"jaro_winkler"``.
        s1 / s2:
            Two strings for pairwise operations.
        query:
            Search query for ``"best_match"`` and ``"rank_matches"``.
        candidates:
            Comma-separated list of candidate strings.
        top_n:
            Max results for ``"rank_matches"`` (default 10).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "distance":
            if not s1 or not s2:
                return "Error: s1 and s2 are required"
            return str(_levenshtein(s1, s2))

        if action == "similarity":
            if not s1 or not s2:
                return "Error: s1 and s2 are required"
            return f"{_similarity(s1, s2):.4f}"

        if action == "best_match":
            return self._best_match(query, candidates)

        if action == "rank_matches":
            return self._rank(query, candidates, int(top_n))

        if action == "jaro":
            if not s1 or not s2:
                return "Error: s1 and s2 are required"
            return f"{_jaro(s1, s2):.4f}"

        if action == "jaro_winkler":
            if not s1 or not s2:
                return "Error: s1 and s2 are required"
            return f"{_jaro_winkler(s1, s2):.4f}"

        return (
            f"Error: unknown action {action!r}. "
            "Use distance, similarity, best_match, rank_matches, jaro, or jaro_winkler."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _best_match(query: str, candidates: str) -> str:
        if not query:
            return "Error: query is required"
        if not candidates:
            return "Error: candidates is required"
        cands = [c.strip() for c in candidates.split(",") if c.strip()]
        if not cands:
            return "Error: no candidates provided"
        best = max(cands, key=lambda c: _similarity(query, c))
        score = _similarity(query, best)
        return f"Best match for {query!r}: {best!r} (similarity: {score:.4f})"

    @staticmethod
    def _rank(query: str, candidates: str, top_n: int) -> str:
        if not query:
            return "Error: query is required"
        if not candidates:
            return "Error: candidates is required"
        cands = [c.strip() for c in candidates.split(",") if c.strip()]
        if not cands:
            return "Error: no candidates provided"
        ranked = sorted(cands, key=lambda c: _similarity(query, c), reverse=True)[:top_n]
        lines = [f"Top {min(top_n, len(ranked))} matches for {query!r}:"]
        for i, c in enumerate(ranked, 1):
            lines.append(f"  {i}. {c!r} ({_similarity(query, c):.4f})")
        return "\n".join(lines)
