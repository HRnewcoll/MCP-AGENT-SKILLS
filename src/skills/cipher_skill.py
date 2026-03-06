"""Cipher skill – classical text ciphers for encoding and decoding.

Covers the "Security & Passwords", "Communication", and "Personal
Development" categories from the awesome-openclaw-skills directory.
Uses Python stdlib only.

Supported actions
-----------------
caesar_encode       Shift letters by N positions (Caesar cipher).
caesar_decode       Reverse a Caesar shift.
rot13               Apply ROT13 (self-inverse).
atbash              Apply Atbash cipher (reverse alphabet).
vigenere_encode     Polyalphabetic Vigenère cipher encoding.
vigenere_decode     Vigenère cipher decoding.
"""

from __future__ import annotations

import re
import string


class CipherSkill:
    """Encode and decode text using classical ciphers."""

    name = "cipher"
    description = (
        "Classical text ciphers. "
        "Supported actions: 'caesar_encode' (text, shift); "
        "'caesar_decode' (text, shift); 'rot13' (text); "
        "'atbash' (text); 'vigenere_encode' (text, key); "
        "'vigenere_decode' (text, key)."
    )

    def run(
        self,
        action: str,
        text: str = "",
        shift: int = 13,
        key: str = "",
    ) -> str:
        """
        Apply a cipher to *text*.

        Parameters
        ----------
        action:
            One of ``"caesar_encode"``, ``"caesar_decode"``, ``"rot13"``,
            ``"atbash"``, ``"vigenere_encode"``, ``"vigenere_decode"``.
        text:
            Input text to encode or decode.
        shift:
            Number of positions to shift for Caesar cipher (default 13).
        key:
            Keyword for Vigenère cipher (letters only).

        Returns
        -------
        str
            Encoded/decoded text or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "caesar_encode":
            return self._caesar(text, int(shift) % 26)
        if action == "caesar_decode":
            return self._caesar(text, -int(shift) % 26)
        if action == "rot13":
            return self._caesar(text, 13)
        if action == "atbash":
            return self._atbash(text)
        if action == "vigenere_encode":
            return self._vigenere(text, key, encode=True)
        if action == "vigenere_decode":
            return self._vigenere(text, key, encode=False)
        return (
            f"Error: unknown action {action!r}. "
            "Use caesar_encode, caesar_decode, rot13, atbash, "
            "vigenere_encode, or vigenere_decode."
        )

    # ------------------------------------------------------------------
    # Internal implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _caesar(text: str, shift: int) -> str:
        if not text:
            return "Error: text is required"
        result = []
        for ch in text:
            if ch.isupper():
                result.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
            elif ch.islower():
                result.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
            else:
                result.append(ch)
        return "".join(result)

    @staticmethod
    def _atbash(text: str) -> str:
        if not text:
            return "Error: text is required"
        result = []
        for ch in text:
            if ch.isupper():
                result.append(chr(ord("Z") - (ord(ch) - ord("A"))))
            elif ch.islower():
                result.append(chr(ord("z") - (ord(ch) - ord("a"))))
            else:
                result.append(ch)
        return "".join(result)

    @staticmethod
    def _vigenere(text: str, key: str, encode: bool) -> str:
        if not text:
            return "Error: text is required"
        if not key:
            return "Error: key is required for Vigenère cipher"
        key_clean = re.sub(r"[^a-zA-Z]", "", key).upper()
        if not key_clean:
            return "Error: key must contain at least one letter"
        result = []
        key_idx = 0
        for ch in text:
            if ch.isalpha():
                k = ord(key_clean[key_idx % len(key_clean)]) - ord("A")
                if not encode:
                    k = -k
                if ch.isupper():
                    result.append(chr((ord(ch) - ord("A") + k) % 26 + ord("A")))
                else:
                    result.append(chr((ord(ch) - ord("a") + k) % 26 + ord("a")))
                key_idx += 1
            else:
                result.append(ch)
        return "".join(result)
