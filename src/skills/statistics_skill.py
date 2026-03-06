"""Statistics skill – descriptive statistics on numeric data sets.

Covers the "Data & Analytics" category from the awesome-openclaw-skills
directory.  Uses Python stdlib ``statistics`` module only.

Supported actions
-----------------
mean            Arithmetic mean of a list of numbers.
median          Median value.
mode            Most frequent value (raises error if no unique mode).
stdev           Sample standard deviation.
pstdev          Population standard deviation.
variance        Sample variance.
pvariance       Population variance.
summary         Full summary (min, max, mean, median, stdev, count).
percentile      Nth percentile (0-100) of the data set.
correlation     Pearson correlation coefficient of two same-length lists.
"""

from __future__ import annotations

import statistics


def _parse_numbers(data: str) -> list[float]:
    """Parse comma-separated numbers into a list of floats."""
    return [float(x.strip()) for x in data.split(",") if x.strip()]


class StatisticsSkill:
    """Compute descriptive statistics on numeric data sets."""

    name = "statistics"
    description = (
        "Compute descriptive statistics on numeric data. "
        "Pass data as a comma-separated list of numbers. "
        "Supported actions: 'mean', 'median', 'mode', 'stdev', 'pstdev', "
        "'variance', 'pvariance', 'summary', 'percentile' (requires n=0-100), "
        "'correlation' (requires data2)."
    )

    def run(
        self,
        action: str,
        data: str = "",
        data2: str = "",
        n: float = 50.0,
    ) -> str:
        """
        Compute a statistical measure on *data*.

        Parameters
        ----------
        action:
            The statistic to compute (see description).
        data:
            Comma-separated list of numbers, e.g. ``"1, 2, 3, 4, 5"``.
        data2:
            Second data set for ``"correlation"`` (comma-separated).
        n:
            Percentile (0-100) for ``"percentile"`` (default 50).

        Returns
        -------
        str
            Numeric result or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            nums = _parse_numbers(data)
        except ValueError:
            return "Error: data must be comma-separated numbers"

        if not nums and action not in ("correlation",):
            return "Error: data is required"

        try:
            if action == "mean":
                return str(round(statistics.mean(nums), 10))

            if action == "median":
                return str(statistics.median(nums))

            if action == "mode":
                return str(statistics.mode(nums))

            if action == "stdev":
                if len(nums) < 2:
                    return "Error: stdev requires at least 2 data points"
                return str(round(statistics.stdev(nums), 10))

            if action == "pstdev":
                return str(round(statistics.pstdev(nums), 10))

            if action == "variance":
                if len(nums) < 2:
                    return "Error: variance requires at least 2 data points"
                return str(round(statistics.variance(nums), 10))

            if action == "pvariance":
                return str(round(statistics.pvariance(nums), 10))

            if action == "summary":
                if len(nums) < 2:
                    return f"count={len(nums)}  min={nums[0]}  max={nums[0]}  mean={nums[0]}"
                return (
                    f"count={len(nums)}\n"
                    f"min={min(nums)}\n"
                    f"max={max(nums)}\n"
                    f"mean={round(statistics.mean(nums), 6)}\n"
                    f"median={statistics.median(nums)}\n"
                    f"stdev={round(statistics.stdev(nums), 6)}"
                )

            if action == "percentile":
                sorted_nums = sorted(nums)
                idx = (float(n) / 100.0) * (len(sorted_nums) - 1)
                lo = int(idx)
                hi = min(lo + 1, len(sorted_nums) - 1)
                frac = idx - lo
                result = sorted_nums[lo] + frac * (sorted_nums[hi] - sorted_nums[lo])
                return str(round(result, 10))

            if action == "correlation":
                try:
                    nums2 = _parse_numbers(data2)
                except ValueError:
                    return "Error: data2 must be comma-separated numbers"
                if len(nums) != len(nums2):
                    return "Error: data and data2 must have the same length"
                if len(nums) < 2:
                    return "Error: correlation requires at least 2 data points"
                return str(round(statistics.correlation(nums, nums2), 10))

        except statistics.StatisticsError as exc:
            return f"Error: {exc}"
        except Exception as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use mean, median, mode, stdev, pstdev, variance, pvariance, "
            "summary, percentile, or correlation."
        )
