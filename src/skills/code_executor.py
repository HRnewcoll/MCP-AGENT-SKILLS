"""Code execution skill – run Python snippets in an isolated subprocess."""

import subprocess
import sys
import textwrap


class CodeExecutorSkill:
    """Execute Python code snippets and return their output."""

    name = "code_executor"
    description = (
        "Execute a Python code snippet and return its stdout / stderr output. "
        "The code runs in a fresh subprocess with a configurable timeout."
    )

    DEFAULT_TIMEOUT = 10  # seconds

    def run(self, code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        """
        Execute *code* as a Python script.

        Parameters
        ----------
        code:
            Python source code to execute.
        timeout:
            Maximum number of seconds the subprocess may run (default 10).

        Returns
        -------
        str
            Combined stdout + stderr of the executed script, or an error
            message prefixed with ``"Error: "`` on failure.
        """
        code = textwrap.dedent(code)
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout
            if result.stderr:
                output = output + result.stderr if output else result.stderr
            return output if output else "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: execution timed out after {timeout} seconds"
        except Exception as exc:
            return f"Error: {exc}"
