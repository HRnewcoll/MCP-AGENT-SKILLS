"""Color palette skill – generate harmonious color palettes and conversions.

Covers the "Design & UI" category.
Pure Python, no external libraries.

Supported actions
-----------------
complementary   Generate complementary color.
analogous       Generate 3 analogous colors.
triadic         Generate triadic color scheme.
split_complementary  Split-complementary scheme.
tetradic        Square/tetradic color scheme.
shades          Generate N shades (dark to light) of a color.
hex_to_rgb      Convert hex color to RGB.
rgb_to_hex      Convert RGB to hex.
rgb_to_hsl      Convert RGB to HSL.
hsl_to_rgb      Convert HSL to RGB.
"""

from __future__ import annotations

import re
import math


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#").strip()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {hex_color!r}")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return r, g, b


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_, g_, b_ = r / 255, g / 255, b / 255
    cmax = max(r_, g_, b_)
    cmin = min(r_, g_, b_)
    delta = cmax - cmin
    l = (cmax + cmin) / 2
    if delta == 0:
        h = s = 0.0
    else:
        s = delta / (1 - abs(2 * l - 1))
        if cmax == r_:
            h = 60 * (((g_ - b_) / delta) % 6)
        elif cmax == g_:
            h = 60 * ((b_ - r_) / delta + 2)
        else:
            h = 60 * ((r_ - g_) / delta + 4)
    return h % 360, s * 100, l * 100


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    s_ = s / 100
    l_ = l / 100
    c = (1 - abs(2 * l_ - 1)) * s_
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l_ - c / 2
    if 0 <= h < 60:
        r_, g_, b_ = c, x, 0.0
    elif 60 <= h < 120:
        r_, g_, b_ = x, c, 0.0
    elif 120 <= h < 180:
        r_, g_, b_ = 0.0, c, x
    elif 180 <= h < 240:
        r_, g_, b_ = 0.0, x, c
    elif 240 <= h < 300:
        r_, g_, b_ = x, 0.0, c
    else:
        r_, g_, b_ = c, 0.0, x
    return round((r_ + m) * 255), round((g_ + m) * 255), round((b_ + m) * 255)


def _rotate_hue(h: float, degrees: float) -> float:
    return (h + degrees) % 360


def _fmt_color(hex_c: str) -> str:
    r, g, b = _hex_to_rgb(hex_c)
    h, s, l = _rgb_to_hsl(r, g, b)
    return f"{hex_c}  rgb({r},{g},{b})  hsl({h:.0f}°,{s:.0f}%,{l:.0f}%)"


class ColorPaletteSkill:
    """Generate color palettes and perform color space conversions."""

    name = "color_palette"
    description = (
        "Color palette generation and conversion. "
        "Supported actions: 'complementary' (hex_color); "
        "'analogous' (hex_color); 'triadic' (hex_color); "
        "'split_complementary' (hex_color); 'tetradic' (hex_color); "
        "'shades' (hex_color, count=5); "
        "'hex_to_rgb' (hex_color); 'rgb_to_hex' (r, g, b); "
        "'rgb_to_hsl' (r, g, b); 'hsl_to_rgb' (hue, saturation, lightness)."
    )

    def run(
        self,
        action: str,
        hex_color: str = "",
        r: int = 0,
        g: int = 0,
        b: int = 0,
        hue: float = 0.0,
        saturation: float = 100.0,
        lightness: float = 50.0,
        count: int = 5,
    ) -> str:
        action = action.strip().lower()

        try:
            if action == "complementary":
                return self._scheme(hex_color, [180])
            if action == "analogous":
                return self._scheme(hex_color, [-30, 30])
            if action == "triadic":
                return self._scheme(hex_color, [120, 240])
            if action == "split_complementary":
                return self._scheme(hex_color, [150, 210])
            if action == "tetradic":
                return self._scheme(hex_color, [90, 180, 270])
            if action == "shades":
                return self._shades(hex_color, int(count))
            if action == "hex_to_rgb":
                if not hex_color:
                    return "Error: hex_color is required"
                rv, gv, bv = _hex_to_rgb(hex_color)
                return f"rgb({rv}, {gv}, {bv})"
            if action == "rgb_to_hex":
                return _rgb_to_hex(int(r), int(g), int(b))
            if action == "rgb_to_hsl":
                hv, sv, lv = _rgb_to_hsl(int(r), int(g), int(b))
                return f"hsl({hv:.1f}, {sv:.1f}%, {lv:.1f}%)"
            if action == "hsl_to_rgb":
                rv, gv, bv = _hsl_to_rgb(float(hue), float(saturation), float(lightness))
                return f"rgb({rv}, {gv}, {bv})"
        except (ValueError, ZeroDivisionError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use complementary, analogous, triadic, split_complementary, "
            "tetradic, shades, hex_to_rgb, rgb_to_hex, rgb_to_hsl, or hsl_to_rgb."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _scheme(hex_color: str, rotations: list[float]) -> str:
        if not hex_color:
            return "Error: hex_color is required"
        rv, gv, bv = _hex_to_rgb(hex_color)
        h, s, l = _rgb_to_hsl(rv, gv, bv)
        lines = [f"Base : {_fmt_color(hex_color)}"]
        for deg in rotations:
            nh = _rotate_hue(h, deg)
            nr, ng, nb = _hsl_to_rgb(nh, s, l)
            nhex = _rgb_to_hex(nr, ng, nb)
            lines.append(f"+{deg:>4}° : {_fmt_color(nhex)}")
        return "\n".join(lines)

    @staticmethod
    def _shades(hex_color: str, count: int) -> str:
        if not hex_color:
            return "Error: hex_color is required"
        rv, gv, bv = _hex_to_rgb(hex_color)
        h, s, _ = _rgb_to_hsl(rv, gv, bv)
        count = max(2, min(int(count), 20))
        lines = []
        for i in range(count):
            l = 10 + (80 / (count - 1)) * i
            nr, ng, nb = _hsl_to_rgb(h, s, l)
            nhex = _rgb_to_hex(nr, ng, nb)
            lines.append(f"{nhex}  rgb({nr},{ng},{nb})  L={l:.0f}%")
        return "\n".join(lines)
