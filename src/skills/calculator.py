"""Calculator skill – safely evaluate mathematical expressions."""

import ast
import math
import operator
from typing import Union

# Operators that are explicitly allowed.
_SAFE_OPS: dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Math constants / functions available inside expressions.
_SAFE_NAMES: dict = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "ceil": math.ceil,
    "floor": math.floor,
    "abs": abs,
    "round": round,
}


def _eval_node(node: ast.AST) -> Union[int, float]:
    """Recursively evaluate a safe AST node."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in _SAFE_NAMES:
            return _SAFE_NAMES[node.id]  # type: ignore[return-value]
        raise ValueError(f"Unknown name: {node.id!r}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _SAFE_OPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand)
        return _SAFE_OPS[op_type](operand)
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed")
        func_name = node.func.id
        if func_name not in _SAFE_NAMES:
            raise ValueError(f"Unknown function: {func_name!r}")
        func = _SAFE_NAMES[func_name]
        args = [_eval_node(a) for a in node.args]
        return func(*args)
    raise ValueError(f"Unsupported node type: {type(node).__name__}")


class CalculatorSkill:
    """Evaluate mathematical expressions safely."""

    name = "calculator"
    description = (
        "Evaluate a mathematical expression and return the numeric result. "
        "Supports +, -, *, /, //, %, ** and common math functions such as "
        "sqrt, sin, cos, tan, log, ceil, floor as well as constants pi, e."
    )

    def run(self, expression: str) -> str:
        """
        Evaluate *expression* and return the result as a string.

        Parameters
        ----------
        expression:
            A mathematical expression, e.g. ``"2 ** 10 + sqrt(144)"``.

        Returns
        -------
        str
            The numeric result or an error message prefixed with ``"Error: "``.
        """
        expression = expression.strip()
        try:
            tree = ast.parse(expression, mode="eval")
            result = _eval_node(tree)
            return str(result)
        except ZeroDivisionError:
            return "Error: division by zero"
        except Exception as exc:
            return f"Error: {exc}"
