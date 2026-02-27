"""Data converter skill – convert between JSON, CSV, Base64, hex, and URL encoding."""

from __future__ import annotations

import base64
import binascii
import csv
import io
import json
import urllib.parse


class DataConverterSkill:
    """Convert data between common serialisation and encoding formats."""

    name = "data_converter"
    description = (
        "Convert data between formats. "
        "Supported actions: 'json_format', 'json_minify', 'json_to_csv', "
        "'csv_to_json', 'base64_encode', 'base64_decode', "
        "'hex_encode', 'hex_decode', 'url_encode', 'url_decode'."
    )

    def run(self, action: str, data: str = "", indent: int = 2) -> str:
        """
        Convert *data* from one format to another.

        Parameters
        ----------
        action:
            Conversion operation (see description for full list).
        data:
            Input data string.
        indent:
            JSON indentation spaces for 'json_format' (default 2).

        Returns
        -------
        str
            Converted output or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "json_format":
            return self._json_format(data, indent)
        if action == "json_minify":
            return self._json_minify(data)
        if action == "json_to_csv":
            return self._json_to_csv(data)
        if action == "csv_to_json":
            return self._csv_to_json(data)
        if action == "base64_encode":
            return self._base64_encode(data)
        if action == "base64_decode":
            return self._base64_decode(data)
        if action == "hex_encode":
            return self._hex_encode(data)
        if action == "hex_decode":
            return self._hex_decode(data)
        if action == "url_encode":
            return urllib.parse.quote(data, safe="")
        if action == "url_decode":
            try:
                return urllib.parse.unquote(data)
            except Exception as exc:
                return f"Error: {exc}"
        return (
            f"Error: unknown action {action!r}. "
            "Use json_format, json_minify, json_to_csv, csv_to_json, "
            "base64_encode, base64_decode, hex_encode, hex_decode, "
            "url_encode, or url_decode."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _json_format(data: str, indent: int) -> str:
        if not data:
            return "Error: data is required"
        try:
            obj = json.loads(data)
            return json.dumps(obj, indent=indent, ensure_ascii=False)
        except json.JSONDecodeError as exc:
            return f"Error: invalid JSON – {exc}"

    @staticmethod
    def _json_minify(data: str) -> str:
        if not data:
            return "Error: data is required"
        try:
            obj = json.loads(data)
            return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
        except json.JSONDecodeError as exc:
            return f"Error: invalid JSON – {exc}"

    @staticmethod
    def _json_to_csv(data: str) -> str:
        if not data:
            return "Error: data is required"
        try:
            obj = json.loads(data)
        except json.JSONDecodeError as exc:
            return f"Error: invalid JSON – {exc}"
        if not isinstance(obj, list):
            return "Error: JSON must be a list of objects"
        if not obj:
            return ""
        if not isinstance(obj[0], dict):
            return "Error: JSON list items must be objects"
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=list(obj[0].keys()))
        writer.writeheader()
        writer.writerows(obj)
        return out.getvalue()

    @staticmethod
    def _csv_to_json(data: str) -> str:
        if not data:
            return "Error: data is required"
        try:
            reader = csv.DictReader(io.StringIO(data))
            rows = list(reader)
            return json.dumps(rows, ensure_ascii=False, indent=2)
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _base64_encode(data: str) -> str:
        if not data:
            return "Error: data is required"
        return base64.b64encode(data.encode("utf-8")).decode("ascii")

    @staticmethod
    def _base64_decode(data: str) -> str:
        if not data:
            return "Error: data is required"
        try:
            return base64.b64decode(data.encode("ascii")).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as exc:
            return f"Error: invalid base64 – {exc}"

    @staticmethod
    def _hex_encode(data: str) -> str:
        if not data:
            return "Error: data is required"
        return data.encode("utf-8").hex()

    @staticmethod
    def _hex_decode(data: str) -> str:
        if not data:
            return "Error: data is required"
        try:
            return bytes.fromhex(data).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            return f"Error: invalid hex – {exc}"
