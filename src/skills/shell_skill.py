"""Shell skill – execute shell commands in a sandboxed subprocess."""

from __future__ import annotations

import subprocess


class ShellSkill:
    """Execute shell commands and return their combined stdout/stderr output."""

    name = "shell"
    description = (
        "Execute a shell command and return its output (stdout + stderr). "
        "Commands run with a configurable timeout. "
        "Destructive patterns such as 'rm -rf /' are blocked."
    )

    DEFAULT_TIMEOUT = 30  # seconds

    # Substrings that are unconditionally refused.
    _BLOCKED: frozenset[str] = frozenset(
        {
            "rm -rf /",
            "mkfs",
            "dd if=/dev/zero",
            ":(){:|:&};:",  # fork bomb
        }
    )

    def run(self, command: str, timeout: int = DEFAULT_TIMEOUT, cwd: str = "") -> str:
        """
        Execute a shell *command*.

        Parameters
        ----------
        command:
            Shell command string to execute.
        timeout:
            Maximum execution time in seconds (default 30).
        cwd:
            Working directory for the command (default: current directory).

        Returns
        -------
        str
            Combined stdout + stderr or error message prefixed with ``"Error: "``.
        """
        command = command.strip()
        if not command:
            return "Error: command is required"

        for blocked in self._BLOCKED:
            if blocked in command:
                return "Error: command contains a blocked pattern"

        work_dir = cwd.strip() or None

        try:
            result = subprocess.run(
                command,
                shell=True,  # noqa: S602
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir,
            )
            output = result.stdout
            if result.stderr:
                output = (output + result.stderr) if output else result.stderr
            return output if output else "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: command timed out after {timeout} seconds"
        except Exception as exc:
            return f"Error: {exc}"
