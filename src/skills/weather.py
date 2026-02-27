"""Weather skill – fetch current weather via wttr.in (no API key required)."""

import json
import urllib.error
import urllib.parse
import urllib.request


class WeatherSkill:
    """Retrieve current weather conditions for a given location."""

    name = "weather"
    description = (
        "Get the current weather for a city or location. "
        "Returns temperature, condition, humidity and wind speed."
    )

    _BASE_URL = "https://wttr.in/{location}?format=j1"

    def run(self, location: str) -> str:
        """
        Fetch weather for *location*.

        Parameters
        ----------
        location:
            City name or location string (e.g. ``"London"``).

        Returns
        -------
        str
            Human-readable weather summary or an error message prefixed with
            ``"Error: "``.
        """
        location = location.strip()
        if not location:
            return "Error: location is required"

        url = self._BASE_URL.format(location=urllib.parse.quote(location))
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
                data = json.loads(resp.read().decode("utf-8"))
            return self._format(location, data)
        except urllib.error.URLError as exc:
            return f"Error: could not reach weather service – {exc.reason}"
        except Exception as exc:
            return f"Error: {exc}"

    # ------------------------------------------------------------------
    # Formatting helper
    # ------------------------------------------------------------------

    @staticmethod
    def _format(location: str, data: dict) -> str:
        try:
            current = data["current_condition"][0]
            temp_c = current.get("temp_C", "?")
            temp_f = current.get("temp_F", "?")
            desc = current.get("weatherDesc", [{}])[0].get("value", "unknown")
            humidity = current.get("humidity", "?")
            wind_kmph = current.get("windspeedKmph", "?")
            return (
                f"Weather in {location}:\n"
                f"  Condition : {desc}\n"
                f"  Temperature: {temp_c}°C / {temp_f}°F\n"
                f"  Humidity   : {humidity}%\n"
                f"  Wind       : {wind_kmph} km/h"
            )
        except (KeyError, IndexError, TypeError) as exc:
            return f"Error: unexpected response format – {exc}"
