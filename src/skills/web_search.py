"""Web search skill – query DuckDuckGo Instant Answer API."""

import json
import urllib.parse
import urllib.request
import urllib.error


class WebSearchSkill:
    """Search the web using the DuckDuckGo Instant Answer API."""

    name = "web_search"
    description = (
        "Search the web for information. "
        "Returns a short summary and up to five result snippets from DuckDuckGo."
    )

    _API_URL = "https://api.duckduckgo.com/"

    def run(self, query: str, max_results: int = 5) -> str:
        """
        Search for *query* and return a text summary of results.

        Parameters
        ----------
        query:
            Search query string.
        max_results:
            Maximum number of related topic snippets to include (default 5).

        Returns
        -------
        str
            Search results or an error message prefixed with ``"Error: "``.
        """
        query = query.strip()
        if not query:
            return "Error: query is required"

        params = urllib.parse.urlencode(
            {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
        )
        url = f"{self._API_URL}?{params}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
                data = json.loads(resp.read().decode("utf-8"))
            return self._format(data, max_results)
        except urllib.error.URLError as exc:
            return f"Error: could not reach search service – {exc.reason}"
        except Exception as exc:
            return f"Error: {exc}"

    # ------------------------------------------------------------------
    # Formatting helper
    # ------------------------------------------------------------------

    @staticmethod
    def _format(data: dict, max_results: int) -> str:
        lines: list[str] = []

        abstract = data.get("AbstractText", "").strip()
        if abstract:
            source = data.get("AbstractSource", "")
            lines.append(f"Summary ({source}): {abstract}")

        answer = data.get("Answer", "").strip()
        if answer:
            lines.append(f"Instant answer: {answer}")

        topics = data.get("RelatedTopics", [])
        count = 0
        for topic in topics:
            if count >= max_results:
                break
            if isinstance(topic, dict) and topic.get("Text"):
                lines.append(f"• {topic['Text']}")
                count += 1

        if not lines:
            return "No results found."
        return "\n".join(lines)
