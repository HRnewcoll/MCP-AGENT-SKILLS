"""BMI/body metrics skill – BMI, BMR, ideal weight, and calorie needs.

Covers the "Health & Fitness" category.
Pure Python, no external libraries.

Supported actions
-----------------
bmi             Calculate Body Mass Index.
bmr             Calculate Basal Metabolic Rate (Mifflin-St Jeor).
tdee            Calculate Total Daily Energy Expenditure.
ideal_weight    Estimate ideal body weight ranges.
bmi_category    Classify a BMI value.
"""

from __future__ import annotations


# Activity level multipliers for TDEE
_ACTIVITY = {
    "sedentary": (1.2, "little/no exercise"),
    "light":     (1.375, "light exercise 1-3 days/week"),
    "moderate":  (1.55, "moderate exercise 3-5 days/week"),
    "active":    (1.725, "hard exercise 6-7 days/week"),
    "very_active": (1.9, "very hard exercise, physical job"),
}


class BmiCalculatorSkill:
    """Calculate BMI, BMR, TDEE, and ideal body weight."""

    name = "bmi_calculator"
    description = (
        "Body metrics and nutrition calculations. "
        "Supported actions: 'bmi' (weight_kg, height_cm); "
        "'bmr' (weight_kg, height_cm, age, gender=male/female); "
        "'tdee' (weight_kg, height_cm, age, gender, activity=sedentary/light/moderate/active/very_active); "
        "'ideal_weight' (height_cm, gender=male/female); "
        "'bmi_category' (bmi_value)."
    )

    def run(
        self,
        action: str,
        weight_kg: float = 0.0,
        height_cm: float = 0.0,
        age: int = 0,
        gender: str = "male",
        activity: str = "moderate",
        bmi_value: float = 0.0,
    ) -> str:
        """
        Calculate body metrics.

        Parameters
        ----------
        action:
            The calculation to perform (see description).
        weight_kg:
            Body weight in kilograms.
        height_cm:
            Height in centimetres.
        age:
            Age in years (for BMR/TDEE).
        gender:
            ``"male"`` or ``"female"``.
        activity:
            Activity level for TDEE.
        bmi_value:
            BMI value for ``"bmi_category"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "bmi":
                return self._bmi(weight_kg, height_cm)
            if action == "bmr":
                return self._bmr(weight_kg, height_cm, age, gender)
            if action == "tdee":
                return self._tdee(weight_kg, height_cm, age, gender, activity)
            if action == "ideal_weight":
                return self._ideal_weight(height_cm, gender)
            if action == "bmi_category":
                return self._bmi_category(bmi_value or weight_kg)
        except (ValueError, ZeroDivisionError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use bmi, bmr, tdee, ideal_weight, or bmi_category."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _bmi(weight_kg: float, height_cm: float) -> str:
        if weight_kg <= 0:
            return "Error: weight_kg must be > 0"
        if height_cm <= 0:
            return "Error: height_cm must be > 0"
        h_m = height_cm / 100
        bmi = weight_kg / h_m ** 2
        cat = BmiCalculatorSkill._classify(bmi)
        return (
            f"Weight : {weight_kg} kg\n"
            f"Height : {height_cm} cm\n"
            f"BMI    : {bmi:.1f}\n"
            f"Category: {cat}"
        )

    @staticmethod
    def _classify(bmi: float) -> str:
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25.0:
            return "Normal weight"
        if bmi < 30.0:
            return "Overweight"
        return "Obese"

    @staticmethod
    def _bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> str:
        if weight_kg <= 0 or height_cm <= 0 or age <= 0:
            return "Error: weight_kg, height_cm, and age must be > 0"
        g = gender.lower().strip()
        # Mifflin-St Jeor
        if g == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        elif g == "female":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        else:
            return "Error: gender must be 'male' or 'female'"
        return (
            f"BMR (Mifflin-St Jeor): {bmr:.1f} kcal/day\n"
            f"({gender}, {age}y, {weight_kg}kg, {height_cm}cm)"
        )

    @staticmethod
    def _tdee(weight_kg: float, height_cm: float, age: int, gender: str, activity: str) -> str:
        if weight_kg <= 0 or height_cm <= 0 or age <= 0:
            return "Error: weight_kg, height_cm, and age must be > 0"
        g = gender.lower().strip()
        if g == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        elif g == "female":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        else:
            return "Error: gender must be 'male' or 'female'"
        key = activity.lower().strip()
        if key not in _ACTIVITY:
            return f"Error: activity must be one of: {', '.join(_ACTIVITY)}"
        factor, desc = _ACTIVITY[key]
        tdee = bmr * factor
        return (
            f"BMR      : {bmr:.1f} kcal/day\n"
            f"Activity : {desc}\n"
            f"TDEE     : {tdee:.1f} kcal/day\n"
            f"  Lose weight (−500kcal): {tdee - 500:.1f} kcal/day\n"
            f"  Gain weight (+500kcal): {tdee + 500:.1f} kcal/day"
        )

    @staticmethod
    def _ideal_weight(height_cm: float, gender: str) -> str:
        if height_cm <= 0:
            return "Error: height_cm must be > 0"
        g = gender.lower().strip()
        # Devine formula
        h_inches = height_cm / 2.54
        if g == "male":
            devine = 50 + 2.3 * max(0, h_inches - 60)
        elif g == "female":
            devine = 45.5 + 2.3 * max(0, h_inches - 60)
        else:
            return "Error: gender must be 'male' or 'female'"
        # Healthy BMI range (18.5–24.9)
        h_m = height_cm / 100
        low = 18.5 * h_m ** 2
        high = 24.9 * h_m ** 2
        return (
            f"Height           : {height_cm} cm\n"
            f"Devine formula   : {devine:.1f} kg\n"
            f"Healthy BMI range: {low:.1f} – {high:.1f} kg"
        )

    @staticmethod
    def _bmi_category(bmi: float) -> str:
        if bmi <= 0:
            return "Error: bmi_value must be > 0"
        cat = BmiCalculatorSkill._classify(bmi)
        return f"BMI {bmi:.1f} → {cat}"
