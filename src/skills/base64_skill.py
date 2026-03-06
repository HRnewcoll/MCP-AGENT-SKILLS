"""Base64 / URL / Hex encoding and decoding skill.

Covers the "CLI Utilities" and "Browser & Automation" categories from the
awesome-openclaw-skills directory.  Uses Python stdlib only – no external
dependencies required.

Supported actions
-----------------
encode_b64      Base64-encode a UTF-8 string.
decode_b64      Decode a Base64 string to UTF-8.
encode_url      Percent-encode a string for use in a URL.
decode_url      Decode percent-encoded (URL-encoded) characters.
encode_hex      Encode a string as lowercase hex.
decode_hex      Decode hex back to a UTF-8 string.
encode_b32      Base32-encode a string.
decode_b32      Decode a Base32 string.
encode_b16      Base16 (uppercase hex) encode.
decode_b16      Decode Base16.
"""

from __future__ import annotations

import base64
import binascii
import urllib.parse


class Base64Skill:
    """Encode and decode data using Base64, URL, hex, and Base32 schemes."""

    name = "base64"
    description = (
        "Encode and decode strings. "
        "Supported actions: 'encode_b64', 'decode_b64', "
        "'encode_url', 'decode_url', "
        "'encode_hex', 'decode_hex', "
        "'encode_b32', 'decode_b32', "
        "'encode_b16', 'decode_b16'."
    )

    def run(self, action: str, data: str = "") -> str:
        """
        Encode or decode *data* using the chosen scheme.

        Parameters
        ----------
        action:
            The encoding/decoding operation (see description).
        data:
            The string to process.

        Returns
        -------
        str
            Encoded/decoded result or error message prefixed with
            ``"Error: "``.
        """
        action = action.strip().lower()
        if not data and action not in ("encode_b64", "decode_b64"):
            # Allow empty data for b64 to demonstrate empty-string round-trip
            if not data:
                return "Error: data is required"

        try:
            if action == "encode_b64":
                return base64.b64encode(data.encode()).decode()

            if action == "decode_b64":
                # Add padding if missing
                padded = data + "=" * (-len(data) % 4)
                return base64.b64decode(padded).decode("utf-8")

            if action == "encode_url":
                return urllib.parse.quote(data, safe="")

            if action == "decode_url":
                return urllib.parse.unquote(data)

            if action == "encode_hex":
                return data.encode("utf-8").hex()

            if action == "decode_hex":
                return bytes.fromhex(data).decode("utf-8")

            if action == "encode_b32":
                return base64.b32encode(data.encode()).decode()

            if action == "decode_b32":
                padded = data.upper() + "=" * (-len(data) % 8)
                return base64.b32decode(padded).decode("utf-8")

            if action == "encode_b16":
                return base64.b16encode(data.encode()).decode()

            if action == "decode_b16":
                return base64.b16decode(data.upper()).decode("utf-8")

        except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use encode_b64, decode_b64, encode_url, decode_url, "
            "encode_hex, decode_hex, encode_b32, decode_b32, "
            "encode_b16, or decode_b16."
        )
