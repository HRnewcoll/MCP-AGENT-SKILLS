"""HTTP request skill – make HTTP GET / POST / HEAD requests to external URLs."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class HttpRequestSkill:
    """Make HTTP requests to external APIs and web pages."""

    name = "http_request"
    description = (
        "Make HTTP requests to external URLs or APIs. "
        "Supported actions: 'get' (HTTP GET), 'post' (HTTP POST with JSON body), "
        "'head' (HTTP HEAD – returns status and headers only)."
    )

    _DEFAULT_TIMEOUT = 15
    _MAX_RESPONSE_BYTES = 50_000  # 50 KB cap to avoid huge payloads

    def run(
        self,
        action: str,
        url: str,
        body: str = "",
        headers: str = "",
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> str:
        """
        Perform an HTTP request.

        Parameters
        ----------
        action:
            One of ``"get"``, ``"post"``, ``"head"``.
        url:
            The target URL (must start with http:// or https://).
        body:
            JSON body string for POST requests.
        headers:
            Optional JSON object string of additional request headers.
        timeout:
            Request timeout in seconds (default 15).

        Returns
        -------
        str
            Response status + body, or an error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        url = url.strip()
        if not url:
            return "Error: url is required"
        if not url.startswith(("http://", "https://")):
            return "Error: url must start with http:// or https://"

        extra_headers: dict = {}
        if headers:
            try:
                extra_headers = json.loads(headers)
                if not isinstance(extra_headers, dict):
                    return "Error: headers must be a JSON object"
            except json.JSONDecodeError as exc:
                return f"Error: could not parse headers – {exc}"

        if action == "get":
            return self._get(url, extra_headers, timeout)
        if action == "post":
            return self._post(url, body, extra_headers, timeout)
        if action == "head":
            return self._head(url, extra_headers, timeout)
        return f"Error: unknown action {action!r}. Use get, post, or head."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_request(
        self, url: str, method: str, data: bytes | None, extra_headers: dict
    ) -> urllib.request.Request:
        req = urllib.request.Request(url, data=data, method=method)  # noqa: S310
        req.add_header("User-Agent", "MCP-Agent-Skills/1.0")
        for k, v in extra_headers.items():
            req.add_header(str(k), str(v))
        return req

    def _execute(
        self, req: urllib.request.Request, timeout: int, include_body: bool = True
    ) -> str:
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
                status = resp.status
                resp_headers = dict(resp.headers)
                if include_body:
                    body = resp.read(self._MAX_RESPONSE_BYTES).decode(
                        "utf-8", errors="replace"
                    )
                    return f"Status: {status}\n{body}"
                lines = [f"Status: {status}"]
                for k, v in resp_headers.items():
                    lines.append(f"{k}: {v}")
                return "\n".join(lines)
        except urllib.error.HTTPError as exc:
            return f"Error: HTTP {exc.code} {exc.reason}"
        except urllib.error.URLError as exc:
            return f"Error: could not reach URL – {exc.reason}"
        except Exception as exc:
            return f"Error: {exc}"

    def _get(self, url: str, extra_headers: dict, timeout: int) -> str:
        req = self._build_request(url, "GET", None, extra_headers)
        return self._execute(req, timeout)

    def _post(self, url: str, body: str, extra_headers: dict, timeout: int) -> str:
        data = body.encode("utf-8") if body else b""
        merged = {"Content-Type": "application/json", **extra_headers}
        req = self._build_request(url, "POST", data, merged)
        return self._execute(req, timeout)

    def _head(self, url: str, extra_headers: dict, timeout: int) -> str:
        req = self._build_request(url, "HEAD", None, extra_headers)
        return self._execute(req, timeout, include_body=False)
