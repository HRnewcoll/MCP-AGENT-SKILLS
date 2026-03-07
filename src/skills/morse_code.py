"""Morse code skill – encode text to Morse code and decode back.

Covers the "Communication" and "CLI Utilities" categories from the
awesome-openclaw-skills directory.  Uses Python stdlib only.

Supported actions
-----------------
encode    Convert plain text to Morse code.
decode    Convert Morse code back to plain text.
"""

from __future__ import annotations

import re


# International Morse code alphabet
_TO_MORSE: dict[str, str] = {
    "A": ".-",   "B": "-...", "C": "-.-.", "D": "-..",  "E": ".",
    "F": "..-.", "G": "--.",  "H": "....", "I": "..",   "J": ".---",
    "K": "-.-",  "L": ".-..", "M": "--",   "N": "-.",   "O": "---",
    "P": ".--.", "Q": "--.-", "R": ".-.",  "S": "...",  "T": "-",
    "U": "..-",  "V": "...-", "W": ".--",  "X": "-..-", "Y": "-.--",
    "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--",
    "-": "-....-", "/": "-..-.",  "@": ".--.-.", "(": "-.--.",
    ")": "-.--.-", "&": ".-...",  ":": "---...", ";": "-.-.-.",
    "=": "-...-",  "+": ".-.-.",  "_": "..--.-", "\"": ".-..-.",
    "$": "...-..-","'": ".----.",
}

_FROM_MORSE: dict[str, str] = {v: k for k, v in _TO_MORSE.items()}

# Word separator in Morse is typically rendered as ' / '
_WORD_SEP = " / "
_CHAR_SEP = " "


class MorseCodeSkill:
    """Encode text to Morse code and decode Morse code back to text."""

    name = "morse_code"
    description = (
        "Encode and decode Morse code. "
        "Supported actions: 'encode' (text) – convert text to Morse; "
        "'decode' (text) – convert Morse (dots/dashes separated by spaces, "
        "words separated by ' / ') back to text."
    )

    def run(self, action: str, text: str = "") -> str:
        """
        Encode or decode Morse code.

        Parameters
        ----------
        action:
            ``"encode"`` or ``"decode"``.
        text:
            Input text or Morse code string.

        Returns
        -------
        str
            Encoded/decoded result or error message prefixed with
            ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "encode":
            return self._encode(text)
        if action == "decode":
            return self._decode(text)
        return (
            f"Error: unknown action {action!r}. Use encode or decode."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _encode(text: str) -> str:
        if not text:
            return "Error: text is required"
        words = text.upper().split()
        encoded_words = []
        skipped: list[str] = []
        for word in words:
            chars = []
            for ch in word:
                code = _TO_MORSE.get(ch)
                if code:
                    chars.append(code)
                else:
                    skipped.append(ch)
            if chars:
                encoded_words.append(_CHAR_SEP.join(chars))
        result = _WORD_SEP.join(encoded_words)
        if skipped:
            result += f"\n(Skipped unsupported characters: {', '.join(repr(c) for c in set(skipped))})"
        return result

    @staticmethod
    def _decode(text: str) -> str:
        if not text:
            return "Error: text is required"
        # Normalise various dash characters to '-'
        text = re.sub(r"[–—]", "-", text)
        words = text.strip().split(_WORD_SEP)
        decoded_words = []
        for word in words:
            if not word.strip():
                continue
            chars = []
            for code in word.strip().split(_CHAR_SEP):
                code = code.strip()
                if not code:
                    continue
                ch = _FROM_MORSE.get(code)
                if ch:
                    chars.append(ch)
                else:
                    chars.append(f"[?{code}]")
            decoded_words.append("".join(chars))
        return " ".join(decoded_words)
