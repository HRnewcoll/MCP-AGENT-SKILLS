"""Sentiment analysis skill – lexicon-based sentiment scoring of text.

Covers the "Data & Analytics" and "Communication" categories.
Pure Python, no external libraries.

Uses a hand-crafted sentiment lexicon and simple rule-based analysis.

Supported actions
-----------------
analyze         Score the sentiment of a text (positive/negative/neutral).
score           Return the raw sentiment score only.
words           List positive and negative words found in the text.
compare         Compare the sentiment of two texts.
"""

from __future__ import annotations

import re

# --- Positive word lexicon ---
_POSITIVE: frozenset[str] = frozenset({
    "good", "great", "excellent", "amazing", "wonderful", "fantastic",
    "outstanding", "superb", "brilliant", "perfect", "love", "loved",
    "enjoy", "enjoyed", "happy", "happiness", "joy", "joyful", "pleased",
    "delighted", "thrilled", "excited", "awesome", "beautiful", "best",
    "better", "positive", "nice", "kind", "helpful", "useful", "valuable",
    "win", "won", "success", "successful", "achieve", "achieved", "praise",
    "recommend", "recommended", "like", "liked", "impressed", "impressive",
    "satisfied", "satisfying", "magnificent", "splendid", "glorious",
    "cheerful", "optimistic", "grateful", "thankful", "appreciated",
    "innovative", "creative", "efficient", "effective", "reliable",
    "trustworthy", "honest", "fair", "generous", "caring",
})

# --- Negative word lexicon ---
_NEGATIVE: frozenset[str] = frozenset({
    "bad", "terrible", "horrible", "awful", "dreadful", "disgusting",
    "poor", "worst", "worse", "hate", "hated", "dislike", "disliked",
    "sad", "unhappy", "miserable", "upset", "angry", "furious", "annoyed",
    "disappointed", "disappointing", "failure", "failed", "fail", "broken",
    "wrong", "error", "mistake", "problem", "issue", "complaint", "complaints",
    "ugly", "nasty", "rude", "cruel", "offensive", "harmful", "dangerous",
    "useless", "worthless", "inferior", "defective", "faulty", "corrupt",
    "dishonest", "unfair", "deceptive", "fraud", "scam",
    "slow", "boring", "confusing", "difficult", "frustrating", "frustration",
    "regret", "regretted", "waste", "wasted",
})

# Negation words that flip the next word's sentiment
_NEGATIONS: frozenset[str] = frozenset({
    "not", "no", "never", "nobody", "nothing", "nowhere", "neither",
    "nor", "cannot", "cant", "won't", "wont", "isn't", "isnt",
    "wasn't", "wasnt", "aren't", "arent", "doesn't", "doesnt",
    "didn't", "didnt", "don't", "dont",
})

# Booster words that amplify the next sentiment word
_BOOSTERS = {
    "very": 1.5, "extremely": 2.0, "incredibly": 2.0,
    "really": 1.5, "quite": 1.2, "somewhat": 0.7,
    "a bit": 0.5, "slightly": 0.5, "utterly": 2.0, "absolutely": 2.0,
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z']+\b", text.lower())


def _score(tokens: list[str]) -> tuple[float, list[str], list[str]]:
    """Return (total_score, positive_words, negative_words)."""
    total = 0.0
    pos_found: list[str] = []
    neg_found: list[str] = []
    negate = False
    boost = 1.0

    for i, tok in enumerate(tokens):
        if tok in _NEGATIONS:
            negate = True
            boost = 1.0
            continue
        boost = _BOOSTERS.get(tok, boost if tok in _BOOSTERS else 1.0)

        val = 0.0
        if tok in _POSITIVE:
            val = 1.0 * boost
            if not negate:
                pos_found.append(tok)
            else:
                neg_found.append(f"not {tok}")
        elif tok in _NEGATIVE:
            val = -1.0 * boost
            if not negate:
                neg_found.append(tok)
            else:
                pos_found.append(f"not {tok}")

        if negate:
            val = -val
        total += val
        if tok not in _NEGATIONS and tok not in _BOOSTERS:
            negate = False
        boost = 1.0

    return total, pos_found, neg_found


class SentimentSkill:
    """Lexicon-based sentiment analysis for text."""

    name = "sentiment"
    description = (
        "Analyse the sentiment of text using a built-in lexicon. "
        "Supported actions: 'analyze' (text); 'score' (text); "
        "'words' (text); 'compare' (text, text2)."
    )

    def run(
        self,
        action: str,
        text: str = "",
        text2: str = "",
    ) -> str:
        """
        Analyse text sentiment.

        Parameters
        ----------
        action:
            One of ``"analyze"``, ``"score"``, ``"words"``, ``"compare"``.
        text:
            The text to analyse.
        text2:
            Second text for ``"compare"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if not text:
            return "Error: text is required"

        if action == "analyze":
            return self._analyze(text)
        if action == "score":
            tokens = _tokenize(text)
            s, _, _ = _score(tokens)
            return f"{s:.3f}"
        if action == "words":
            return self._words(text)
        if action == "compare":
            return self._compare(text, text2)
        return (
            f"Error: unknown action {action!r}. Use analyze, score, words, or compare."
        )

    @staticmethod
    def _label(score: float) -> str:
        if score > 0.5:
            return "positive 😊"
        if score < -0.5:
            return "negative 😞"
        return "neutral 😐"

    def _analyze(self, text: str) -> str:
        tokens = _tokenize(text)
        s, pos, neg = _score(tokens)
        label = self._label(s)
        return (
            f"Sentiment : {label}\n"
            f"Score     : {s:.3f}\n"
            f"Positive  : {len(pos)} word(s)\n"
            f"Negative  : {len(neg)} word(s)\n"
            f"Total words: {len(tokens)}"
        )

    def _words(self, text: str) -> str:
        tokens = _tokenize(text)
        _, pos, neg = _score(tokens)
        return (
            f"Positive words: {', '.join(pos) if pos else '(none)'}\n"
            f"Negative words: {', '.join(neg) if neg else '(none)'}"
        )

    def _compare(self, text1: str, text2: str) -> str:
        if not text2:
            return "Error: text2 is required for compare"
        t1 = _tokenize(text1)
        t2 = _tokenize(text2)
        s1, _, _ = _score(t1)
        s2, _, _ = _score(t2)
        l1, l2 = self._label(s1), self._label(s2)
        diff = s1 - s2
        winner = "Text 1" if s1 > s2 else ("Text 2" if s2 > s1 else "tie")
        return (
            f"Text 1: {l1} ({s1:.3f})\n"
            f"Text 2: {l2} ({s2:.3f})\n"
            f"Difference: {diff:+.3f}  →  {winner} is more positive"
        )
