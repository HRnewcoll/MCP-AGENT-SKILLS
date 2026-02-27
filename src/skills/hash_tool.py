"""Hash tool skill – hash and verify strings with common algorithms."""

from __future__ import annotations

import hashlib
import hmac as _hmac


class HashToolSkill:
    """Hash text using common cryptographic algorithms."""

    name = "hash_tool"
    description = (
        "Hash text using common algorithms. "
        "Supported actions: 'md5', 'sha1', 'sha256', 'sha512', "
        "'sha3_256', 'blake2b', 'hmac_sha256' (requires secret)."
    )

    def run(
        self,
        action: str,
        text: str = "",
        secret: str = "",
        encoding: str = "utf-8",
    ) -> str:
        """
        Hash *text* using the specified algorithm.

        Parameters
        ----------
        action:
            Hashing algorithm (see description for full list).
        text:
            The input text to hash.
        secret:
            HMAC secret key (only used for 'hmac_sha256').
        encoding:
            Character encoding for the input (default ``"utf-8"``).

        Returns
        -------
        str
            Hex digest string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if not text:
            return "Error: text is required"

        try:
            data = text.encode(encoding)
        except LookupError:
            return f"Error: unknown encoding {encoding!r}"

        algorithms: dict = {
            "md5": lambda d: hashlib.md5(d).hexdigest(),  # noqa: S324
            "sha1": lambda d: hashlib.sha1(d).hexdigest(),  # noqa: S324
            "sha256": lambda d: hashlib.sha256(d).hexdigest(),
            "sha512": lambda d: hashlib.sha512(d).hexdigest(),
            "sha3_256": lambda d: hashlib.sha3_256(d).hexdigest(),
            "blake2b": lambda d: hashlib.blake2b(d).hexdigest(),
        }

        if action in algorithms:
            return algorithms[action](data)

        if action == "hmac_sha256":
            if not secret:
                return "Error: secret is required for hmac_sha256"
            try:
                key = secret.encode(encoding)
                mac = _hmac.new(key, data, hashlib.sha256)
                return mac.hexdigest()
            except Exception as exc:
                return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use md5, sha1, sha256, sha512, sha3_256, blake2b, or hmac_sha256."
        )
