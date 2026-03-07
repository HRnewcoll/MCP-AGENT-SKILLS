"""Matrix skill – basic matrix operations without external libraries.

Covers the "Math & Education" and "Data & Analytics" categories.
Pure Python, no external libraries.

Supported actions
-----------------
add             Add two matrices.
multiply        Multiply two matrices.
transpose       Transpose a matrix.
determinant     Compute the determinant of a square matrix (up to 4×4).
identity        Generate an n×n identity matrix.
scalar_multiply Multiply a matrix by a scalar.
trace           Sum of diagonal elements.
"""

from __future__ import annotations

import json
from typing import Union

Matrix = list[list[float]]


def _parse_matrix(text: str) -> Matrix:
    """
    Parse a matrix from a compact string representation.

    Formats accepted
    ----------------
    ``[[1,2],[3,4]]``   JSON array of arrays
    ``1,2;3,4``         rows separated by semicolons, cols by commas
    """
    text = text.strip()
    if text.startswith("[["):
        data = json.loads(text)
        return [[float(v) for v in row] for row in data]
    rows = []
    for row_str in text.split(";"):
        rows.append([float(v.strip()) for v in row_str.split(",") if v.strip()])
    return rows


def _fmt(m: Matrix) -> str:
    if not m:
        return "[]"
    col_widths = [max(len(f"{m[r][c]:.4g}") for r in range(len(m))) for c in range(len(m[0]))]
    lines = []
    for row in m:
        cells = [f"{v:>{col_widths[i]}.4g}" for i, v in enumerate(row)]
        lines.append("│ " + "  ".join(cells) + " │")
    return "\n".join(lines)


def _det2(m: Matrix) -> float:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def _det3(m: Matrix) -> float:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def _det4(m: Matrix) -> float:
    result = 0.0
    for c in range(4):
        sign = (-1) ** c
        sub = [[m[r][cc] for cc in range(4) if cc != c] for r in range(1, 4)]
        result += sign * m[0][c] * _det3(sub)
    return result


class MatrixSkill:
    """Perform basic matrix operations without external libraries."""

    name = "matrix"
    description = (
        "Matrix operations. "
        "Matrices can be specified as '[[1,2],[3,4]]' or '1,2;3,4' (rows by ';', cols by ','). "
        "Supported actions: 'add' (matrix_a, matrix_b); "
        "'multiply' (matrix_a, matrix_b); 'transpose' (matrix_a); "
        "'determinant' (matrix_a – max 4×4); 'identity' (n); "
        "'scalar_multiply' (matrix_a, scalar); 'trace' (matrix_a)."
    )

    def run(
        self,
        action: str,
        matrix_a: str = "",
        matrix_b: str = "",
        n: int = 3,
        scalar: float = 1.0,
    ) -> str:
        """
        Perform a matrix operation.

        Parameters
        ----------
        action:
            The operation (see description).
        matrix_a:
            First matrix.
        matrix_b:
            Second matrix (for binary operations).
        n:
            Size for ``"identity"``.
        scalar:
            Scalar value for ``"scalar_multiply"``.

        Returns
        -------
        str
            Result matrix/value or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "add":
                return self._add(matrix_a, matrix_b)
            if action == "multiply":
                return self._mul(matrix_a, matrix_b)
            if action == "transpose":
                return self._transpose(matrix_a)
            if action == "determinant":
                return self._det(matrix_a)
            if action == "identity":
                return _fmt(self._identity(int(n)))
            if action == "scalar_multiply":
                return self._scalar(matrix_a, float(scalar))
            if action == "trace":
                return self._trace(matrix_a)
        except (ValueError, json.JSONDecodeError, IndexError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use add, multiply, transpose, determinant, identity, "
            "scalar_multiply, or trace."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _add(a_str: str, b_str: str) -> str:
        if not a_str or not b_str:
            return "Error: matrix_a and matrix_b are required"
        a = _parse_matrix(a_str)
        b = _parse_matrix(b_str)
        if len(a) != len(b) or any(len(a[i]) != len(b[i]) for i in range(len(a))):
            return "Error: matrices must have the same dimensions"
        result = [[a[i][j] + b[i][j] for j in range(len(a[i]))] for i in range(len(a))]
        return _fmt(result)

    @staticmethod
    def _mul(a_str: str, b_str: str) -> str:
        if not a_str or not b_str:
            return "Error: matrix_a and matrix_b are required"
        a = _parse_matrix(a_str)
        b = _parse_matrix(b_str)
        rows_a, cols_a = len(a), len(a[0])
        rows_b, cols_b = len(b), len(b[0])
        if cols_a != rows_b:
            return f"Error: incompatible dimensions ({rows_a}×{cols_a}) × ({rows_b}×{cols_b})"
        result = [
            [sum(a[i][k] * b[k][j] for k in range(cols_a)) for j in range(cols_b)]
            for i in range(rows_a)
        ]
        return _fmt(result)

    @staticmethod
    def _transpose(a_str: str) -> str:
        if not a_str:
            return "Error: matrix_a is required"
        a = _parse_matrix(a_str)
        result = [[a[r][c] for r in range(len(a))] for c in range(len(a[0]))]
        return _fmt(result)

    @staticmethod
    def _det(a_str: str) -> str:
        if not a_str:
            return "Error: matrix_a is required"
        a = _parse_matrix(a_str)
        n = len(a)
        if any(len(row) != n for row in a):
            return "Error: matrix must be square"
        if n == 1:
            return str(a[0][0])
        if n == 2:
            return f"det = {_det2(a):.6g}"
        if n == 3:
            return f"det = {_det3(a):.6g}"
        if n == 4:
            return f"det = {_det4(a):.6g}"
        return "Error: determinant supported for matrices up to 4×4"

    @staticmethod
    def _identity(n: int) -> Matrix:
        return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    @staticmethod
    def _scalar(a_str: str, k: float) -> str:
        if not a_str:
            return "Error: matrix_a is required"
        a = _parse_matrix(a_str)
        result = [[v * k for v in row] for row in a]
        return _fmt(result)

    @staticmethod
    def _trace(a_str: str) -> str:
        if not a_str:
            return "Error: matrix_a is required"
        a = _parse_matrix(a_str)
        n = min(len(a), len(a[0]))
        tr = sum(a[i][i] for i in range(n))
        return f"trace = {tr:.6g}"
