"""Unit converter skill – convert between common measurement units."""

from __future__ import annotations


class UnitConverterSkill:
    """Convert values between common measurement units."""

    name = "unit_converter"
    description = (
        "Convert between measurement units. "
        "Categories: 'length' (m, km, cm, mm, in, ft, yd, mi), "
        "'weight' (kg, g, mg, lb, oz, t), "
        "'temperature' (C, F, K), "
        "'volume' (l, ml, m3, gallon, floz, cup), "
        "'speed' (kmh, ms, mph, knot), "
        "'area' (m2, km2, cm2, ha, acre, ft2, in2)."
    )

    # Base unit: metre
    _LENGTH: dict[str, float] = {
        "m": 1.0,
        "km": 1_000.0,
        "cm": 0.01,
        "mm": 0.001,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
        "mi": 1_609.344,
    }

    # Base unit: kilogram
    _WEIGHT: dict[str, float] = {
        "kg": 1.0,
        "g": 0.001,
        "mg": 1e-6,
        "lb": 0.45359237,
        "oz": 0.028349523,
        "t": 1_000.0,
    }

    # Base unit: litre
    _VOLUME: dict[str, float] = {
        "l": 1.0,
        "ml": 0.001,
        "m3": 1_000.0,
        "gallon": 3.785411784,
        "floz": 0.02957353,
        "cup": 0.236588,
    }

    # Base unit: m/s
    _SPEED: dict[str, float] = {
        "ms": 1.0,
        "kmh": 1 / 3.6,
        "mph": 0.44704,
        "knot": 0.514444,
    }

    # Base unit: m²
    _AREA: dict[str, float] = {
        "m2": 1.0,
        "km2": 1_000_000.0,
        "cm2": 0.0001,
        "ha": 10_000.0,
        "acre": 4_046.8564,
        "ft2": 0.092903,
        "in2": 0.00064516,
    }

    def run(
        self,
        category: str,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> str:
        """
        Convert *value* from *from_unit* to *to_unit* within *category*.

        Parameters
        ----------
        category:
            Unit category: ``"length"``, ``"weight"``, ``"temperature"``,
            ``"volume"``, ``"speed"``, or ``"area"``.
        value:
            Numeric value to convert.
        from_unit:
            Source unit abbreviation (e.g. ``"km"``).
        to_unit:
            Target unit abbreviation (e.g. ``"mi"``).

        Returns
        -------
        str
            Converted value string or error message prefixed with ``"Error: "``.
        """
        category = category.strip().lower()
        from_unit = from_unit.strip().lower()
        to_unit = to_unit.strip().lower()

        if category == "temperature":
            return self._temperature(value, from_unit, to_unit)

        tables: dict[str, dict[str, float]] = {
            "length": self._LENGTH,
            "weight": self._WEIGHT,
            "volume": self._VOLUME,
            "speed": self._SPEED,
            "area": self._AREA,
        }

        table = tables.get(category)
        if table is None:
            return (
                f"Error: unknown category {category!r}. "
                "Use length, weight, temperature, volume, speed, or area."
            )
        if from_unit not in table:
            return (
                f"Error: unknown unit {from_unit!r} for {category!r}. "
                f"Options: {', '.join(sorted(table))}"
            )
        if to_unit not in table:
            return (
                f"Error: unknown unit {to_unit!r} for {category!r}. "
                f"Options: {', '.join(sorted(table))}"
            )

        result = value * table[from_unit] / table[to_unit]
        return f"{value} {from_unit} = {result:.6g} {to_unit}"

    @staticmethod
    def _temperature(value: float, from_unit: str, to_unit: str) -> str:
        valid = {"c", "f", "k"}
        if from_unit not in valid:
            return f"Error: unknown temperature unit {from_unit!r}. Use c, f, or k."
        if to_unit not in valid:
            return f"Error: unknown temperature unit {to_unit!r}. Use c, f, or k."

        # Convert to Celsius first
        if from_unit == "f":
            c = (value - 32) * 5 / 9
        elif from_unit == "k":
            c = value - 273.15
        else:
            c = value

        # Convert from Celsius to target
        if to_unit == "f":
            result = c * 9 / 5 + 32
        elif to_unit == "k":
            result = c + 273.15
        else:
            result = c

        return f"{value} {from_unit.upper()} = {result:.4g} {to_unit.upper()}"
