"""System info skill – query OS, Python runtime, and environment details."""

from __future__ import annotations

import os
import platform
import sys


class SystemInfoSkill:
    """Retrieve information about the current system and runtime environment."""

    name = "system_info"
    description = (
        "Retrieve system and environment information. "
        "Supported actions: 'os' (operating system details), "
        "'python' (Python runtime version and executable), "
        "'env' (list environment variable names), "
        "'cwd' (current working directory), "
        "'all' (full summary)."
    )

    def run(self, action: str = "all") -> str:
        """
        Retrieve system information.

        Parameters
        ----------
        action:
            One of ``"os"``, ``"python"``, ``"env"``, ``"cwd"``, ``"all"``.

        Returns
        -------
        str
            Information string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "os":
            return self._os_info()
        if action == "python":
            return self._python_info()
        if action == "env":
            return self._env_names()
        if action == "cwd":
            return os.getcwd()
        if action == "all":
            return "\n".join([
                "=== OS ===",
                self._os_info(),
                "\n=== Python ===",
                self._python_info(),
                "\n=== Working Directory ===",
                os.getcwd(),
            ])
        return f"Error: unknown action {action!r}. Use os, python, env, cwd, or all."

    # ------------------------------------------------------------------

    @staticmethod
    def _os_info() -> str:
        return (
            f"System   : {platform.system()} {platform.release()}\n"
            f"Machine  : {platform.machine()}\n"
            f"Processor: {platform.processor() or 'unknown'}\n"
            f"Node     : {platform.node()}"
        )

    @staticmethod
    def _python_info() -> str:
        return (
            f"Version       : {sys.version}\n"
            f"Implementation: {platform.python_implementation()}\n"
            f"Executable    : {sys.executable}"
        )

    @staticmethod
    def _env_names() -> str:
        names = sorted(os.environ.keys())
        return "\n".join(names) if names else "(no environment variables)"
