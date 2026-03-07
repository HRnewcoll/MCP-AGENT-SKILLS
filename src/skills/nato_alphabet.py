"""NATO phonetic alphabet skill – convert text to/from the NATO phonetic alphabet.

Covers the "Communication" and "CLI Utilities" categories.
Pure Python, no external libraries.

Supported actions
-----------------
encode          Convert letters to their NATO phonetic code words.
decode          Convert NATO code words back to letters.
spell           Spell out a word letter-by-letter using phonetic codes.
"""

from __future__ import annotations

_TO_NATO: dict[str, str] = {
    "A": "Alpha",   "B": "Bravo",   "C": "Charlie", "D": "Delta",
    "E": "Echo",    "F": "Foxtrot", "G": "Golf",    "H": "Hotel",
    "I": "India",   "J": "Juliet",  "K": "Kilo",    "L": "Lima",
    "M": "Mike",    "N": "November","O": "Oscar",   "P": "Papa",
    "Q": "Quebec",  "R": "Romeo",   "S": "Sierra",  "T": "Tango",
    "U": "Uniform", "V": "Victor",  "W": "Whiskey", "X": "X-ray",
    "Y": "Yankee",  "Z": "Zulu",
    "0": "Zero",    "1": "One",     "2": "Two",     "3": "Three",
    "4": "Four",    "5": "Five",    "6": "Six",     "7": "Seven",
    "8": "Eight",   "9": "Niner",
}

_FROM_NATO: dict[str, str] = {v.lower(): k for k, v in _TO_NATO.items()}


class NatoAlphabetSkill:
    """Convert text to and from the NATO phonetic alphabet."""

    name = "nato_alphabet"
    description = (
        "Convert text to/from NATO phonetic alphabet. "
        "Supported actions: 'encode' (text); 'decode' (text – space-separated code words); "
        "'spell' (text – one code word per letter, formatted for reading aloud)."
    )

    def run(self, action: str, text: str = "") -> str:
        """
        Perform a NATO phonetic alphabet conversion.

        Parameters
        ----------
        action:
            One of ``"encode"``, ``"decode"``, ``"spell"``.
        text:
            Input text.

        Returns
        -------
        str
            Result or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if not text:
            return "Error: text is required"

        if action == "encode":
            return self._encode(text)
        if action == "decode":
            return self._decode(text)
        if action == "spell":
            return self._spell(text)
        return (
            f"Error: unknown action {action!r}. Use encode, decode, or spell."
        )

    @staticmethod
    def _encode(text: str) -> str:
        words: list[str] = []
        for ch in text.upper():
            if ch in _TO_NATO:
                words.append(_TO_NATO[ch])
            elif ch == " ":
                words.append("/")
            else:
                words.append(ch)
        return " ".join(words)

    @staticmethod
    def _decode(text: str) -> str:
        tokens = text.strip().split()
        result: list[str] = []
        for token in tokens:
            if token == "/":
                result.append(" ")
            else:
                ch = _FROM_NATO.get(token.lower())
                if ch:
                    result.append(ch)
                else:
                    result.append(f"[{token}]")
        return "".join(result)

    @staticmethod
    def _spell(text: str) -> str:
        lines: list[str] = []
        for ch in text.upper():
            if ch in _TO_NATO:
                lines.append(f"{ch} – {_TO_NATO[ch]}")
            elif ch == " ":
                lines.append("(space)")
            else:
                lines.append(ch)
        return "\n".join(lines)
