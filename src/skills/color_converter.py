"""Color converter skill – convert between HEX, RGB, HSL, and HSV formats.

Covers the "Web & Frontend Development" category from the
awesome-openclaw-skills directory.  Uses Python stdlib only (``colorsys``).

Supported actions
-----------------
hex_to_rgb      Convert CSS hex (#RRGGBB) to rgb(R, G, B).
rgb_to_hex      Convert R G B integers to CSS hex.
hex_to_hsl      Convert CSS hex to hsl(H, S%, L%).
hsl_to_hex      Convert H S L values to CSS hex.
rgb_to_hsl      Convert R G B to H S L.
hsl_to_rgb      Convert H S L to R G B.
hex_to_hsv      Convert CSS hex to H S V.
lighten         Lighten a hex colour by a percentage.
darken          Darken a hex colour by a percentage.
complementary   Return the complementary hex colour.
mix             Mix two hex colours at a given ratio (0-100).
"""

from __future__ import annotations

import colorsys
import re


def _parse_hex(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"Invalid hex colour: {hex_str!r}")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return r, g, b


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(round(r)))),
        max(0, min(255, int(round(g)))),
        max(0, min(255, int(round(b)))),
    )


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return round(h * 360, 1), round(s * 100, 1), round(l * 100, 1)


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


class ColorConverterSkill:
    """Convert and manipulate colours across HEX, RGB, HSL, and HSV formats."""

    name = "color_converter"
    description = (
        "Convert and manipulate web colours. "
        "Supported actions: 'hex_to_rgb' (hex_color); 'rgb_to_hex' (r, g, b); "
        "'hex_to_hsl' (hex_color); 'hsl_to_hex' (h, s, l); "
        "'rgb_to_hsl' (r, g, b); 'hsl_to_rgb' (h, s, l); "
        "'hex_to_hsv' (hex_color); 'lighten' (hex_color, amount); "
        "'darken' (hex_color, amount); 'complementary' (hex_color); "
        "'mix' (hex1, hex2, ratio)."
    )

    def run(
        self,
        action: str,
        hex_color: str = "",
        hex1: str = "",
        hex2: str = "",
        r: int = 0,
        g: int = 0,
        b: int = 0,
        h: float = 0.0,
        s: float = 0.0,
        l: float = 0.0,
        amount: float = 10.0,
        ratio: float = 50.0,
    ) -> str:
        """
        Convert or manipulate a colour.

        Parameters
        ----------
        action:
            Conversion/manipulation to perform (see description).
        hex_color:
            CSS hex colour string, e.g. ``"#3498db"`` or ``"3498db"``.
        hex1 / hex2:
            Two hex colours for ``"mix"``.
        r, g, b:
            Red, green, blue components (0-255).
        h, s, l:
            Hue (0-360), saturation (0-100%), lightness (0-100%).
        amount:
            Lightness change percentage for ``"lighten"`` / ``"darken"``
            (default 10).
        ratio:
            Mix ratio 0-100 for ``"mix"`` (0 = all hex1, 100 = all hex2;
            default 50).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        try:
            if action == "hex_to_rgb":
                rr, gg, bb = _parse_hex(hex_color)
                return f"rgb({rr}, {gg}, {bb})"

            if action == "rgb_to_hex":
                return _rgb_to_hex(r, g, b)

            if action == "hex_to_hsl":
                rr, gg, bb = _parse_hex(hex_color)
                hv, sv, lv = _rgb_to_hsl(rr, gg, bb)
                return f"hsl({hv}, {sv}%, {lv}%)"

            if action == "hsl_to_hex":
                rr, gg, bb = _hsl_to_rgb(h, s, l)
                return _rgb_to_hex(rr, gg, bb)

            if action == "rgb_to_hsl":
                hv, sv, lv = _rgb_to_hsl(r, g, b)
                return f"hsl({hv}, {sv}%, {lv}%)"

            if action == "hsl_to_rgb":
                rr, gg, bb = _hsl_to_rgb(h, s, l)
                return f"rgb({rr}, {gg}, {bb})"

            if action == "hex_to_hsv":
                rr, gg, bb = _parse_hex(hex_color)
                hv, sv, vv = colorsys.rgb_to_hsv(rr / 255, gg / 255, bb / 255)
                return f"hsv({round(hv * 360, 1)}, {round(sv * 100, 1)}%, {round(vv * 100, 1)}%)"

            if action == "lighten":
                rr, gg, bb = _parse_hex(hex_color)
                hv, sv, lv = _rgb_to_hsl(rr, gg, bb)
                lv = min(100.0, lv + float(amount))
                rr2, gg2, bb2 = _hsl_to_rgb(hv, sv, lv)
                return _rgb_to_hex(rr2, gg2, bb2)

            if action == "darken":
                rr, gg, bb = _parse_hex(hex_color)
                hv, sv, lv = _rgb_to_hsl(rr, gg, bb)
                lv = max(0.0, lv - float(amount))
                rr2, gg2, bb2 = _hsl_to_rgb(hv, sv, lv)
                return _rgb_to_hex(rr2, gg2, bb2)

            if action == "complementary":
                rr, gg, bb = _parse_hex(hex_color)
                hv, sv, lv = _rgb_to_hsl(rr, gg, bb)
                comp_h = (hv + 180) % 360
                rr2, gg2, bb2 = _hsl_to_rgb(comp_h, sv, lv)
                return _rgb_to_hex(rr2, gg2, bb2)

            if action == "mix":
                if not hex1 or not hex2:
                    return "Error: hex1 and hex2 are required for mix"
                r1, g1, b1 = _parse_hex(hex1)
                r2, g2, b2 = _parse_hex(hex2)
                t = max(0.0, min(100.0, float(ratio))) / 100.0
                rm = r1 + (r2 - r1) * t
                gm = g1 + (g2 - g1) * t
                bm = b1 + (b2 - b1) * t
                return _rgb_to_hex(rm, gm, bm)

        except (ValueError, TypeError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use hex_to_rgb, rgb_to_hex, hex_to_hsl, hsl_to_hex, "
            "rgb_to_hsl, hsl_to_rgb, hex_to_hsv, lighten, darken, "
            "complementary, or mix."
        )
