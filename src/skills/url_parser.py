"""URL parser skill – parse, build, encode, and manipulate URLs.

Covers the "Browser & Automation" category from the
awesome-openclaw-skills directory.  Uses Python stdlib only
(``urllib.parse``).

Supported actions
-----------------
parse           Break a URL into its components.
build           Construct a URL from components.
encode          Percent-encode a string for use in a URL.
decode          Decode a percent-encoded string.
add_param       Append or update a query parameter.
remove_param    Remove a query parameter.
get_param       Get the value of a query parameter.
list_params     List all query parameters.
extract_domain  Extract just the domain from a URL.
normalize       Normalise a URL (scheme lowercase, strip trailing slash).
"""

from __future__ import annotations

import urllib.parse


class UrlParserSkill:
    """Parse, build, encode, and manipulate URLs."""

    name = "url_parser"
    description = (
        "Parse and manipulate URLs. "
        "Supported actions: 'parse' (url); 'build' (scheme, host, path, params); "
        "'encode' (text); 'decode' (text); 'add_param' (url, key, value); "
        "'remove_param' (url, key); 'get_param' (url, key); "
        "'list_params' (url); 'extract_domain' (url); 'normalize' (url)."
    )

    def run(
        self,
        action: str,
        url: str = "",
        scheme: str = "https",
        host: str = "",
        path: str = "",
        params: str = "",
        text: str = "",
        key: str = "",
        value: str = "",
    ) -> str:
        """
        Perform a URL operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        url:
            The URL string to operate on.
        scheme:
            URL scheme for ``"build"`` (default ``"https"``).
        host:
            Hostname/authority for ``"build"``.
        path:
            URL path for ``"build"``.
        params:
            Query string for ``"build"`` (e.g. ``"key=val&k2=v2"``).
        text:
            Raw string for ``"encode"`` / ``"decode"``.
        key:
            Query parameter name.
        value:
            Query parameter value for ``"add_param"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "parse":
            return self._parse(url)
        if action == "build":
            return self._build(scheme, host, path, params)
        if action == "encode":
            return urllib.parse.quote(text, safe="") if text else ""
        if action == "decode":
            return urllib.parse.unquote(text)
        if action == "add_param":
            return self._add_param(url, key, value)
        if action == "remove_param":
            return self._remove_param(url, key)
        if action == "get_param":
            return self._get_param(url, key)
        if action == "list_params":
            return self._list_params(url)
        if action == "extract_domain":
            return self._extract_domain(url)
        if action == "normalize":
            return self._normalize(url)
        return (
            f"Error: unknown action {action!r}. "
            "Use parse, build, encode, decode, add_param, remove_param, "
            "get_param, list_params, extract_domain, or normalize."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(url: str) -> str:
        if not url:
            return "Error: url is required"
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(p.query, keep_blank_values=True)
        params_str = (
            "\n".join(f"  {k}: {v[0] if len(v) == 1 else v}" for k, v in qs.items())
            if qs
            else "  (none)"
        )
        return (
            f"scheme   : {p.scheme}\n"
            f"netloc   : {p.netloc}\n"
            f"path     : {p.path}\n"
            f"params   : {p.params}\n"
            f"query    :\n{params_str}\n"
            f"fragment : {p.fragment}"
        )

    @staticmethod
    def _build(scheme: str, host: str, path: str, params: str) -> str:
        if not host:
            return "Error: host is required for build"
        if not path.startswith("/"):
            path = "/" + path
        return urllib.parse.urlunparse(
            (scheme or "https", host, path, "", params, "")
        )

    @staticmethod
    def _add_param(url: str, key: str, value: str) -> str:
        if not url:
            return "Error: url is required"
        if not key:
            return "Error: key is required"
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(p.query, keep_blank_values=True)
        qs[key] = [value]
        new_query = urllib.parse.urlencode(
            {k: v[0] for k, v in qs.items()}, quote_via=urllib.parse.quote
        )
        return urllib.parse.urlunparse(
            (p.scheme, p.netloc, p.path, p.params, new_query, p.fragment)
        )

    @staticmethod
    def _remove_param(url: str, key: str) -> str:
        if not url:
            return "Error: url is required"
        if not key:
            return "Error: key is required"
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(p.query, keep_blank_values=True)
        qs.pop(key, None)
        new_query = urllib.parse.urlencode(
            {k: v[0] for k, v in qs.items()}, quote_via=urllib.parse.quote
        )
        return urllib.parse.urlunparse(
            (p.scheme, p.netloc, p.path, p.params, new_query, p.fragment)
        )

    @staticmethod
    def _get_param(url: str, key: str) -> str:
        if not url:
            return "Error: url is required"
        if not key:
            return "Error: key is required"
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(p.query, keep_blank_values=True)
        vals = qs.get(key)
        if vals is None:
            return f"Error: parameter {key!r} not found"
        return vals[0] if len(vals) == 1 else str(vals)

    @staticmethod
    def _list_params(url: str) -> str:
        if not url:
            return "Error: url is required"
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(p.query, keep_blank_values=True)
        if not qs:
            return "(no query parameters)"
        return "\n".join(
            f"{k}: {v[0] if len(v) == 1 else v}" for k, v in qs.items()
        )

    @staticmethod
    def _extract_domain(url: str) -> str:
        if not url:
            return "Error: url is required"
        p = urllib.parse.urlparse(url if "://" in url else "https://" + url)
        return p.hostname or p.netloc

    @staticmethod
    def _normalize(url: str) -> str:
        if not url:
            return "Error: url is required"
        if "://" not in url:
            url = "https://" + url
        p = urllib.parse.urlparse(url)
        path = p.path.rstrip("/") or "/"
        return urllib.parse.urlunparse(
            (p.scheme.lower(), p.netloc.lower(), path, p.params, p.query, p.fragment)
        )
