"""Git skill – run common git operations on a local repository.

All operations are performed via subprocess calls to the ``git`` binary that
must already be installed on the host.  The skill accepts an optional
``repo_path`` argument for every action so it can target any local directory.

Supported actions
-----------------
status          Show working-tree status.
log             Show recent commit history.
diff            Show uncommitted changes.
add             Stage file(s) for commit.
commit          Create a commit with a message.
branch          List branches (or create a new one).
checkout        Switch to a branch.
init            Initialise a new repository.
show            Show details of a specific commit.
"""

from __future__ import annotations

import shutil
import subprocess


_MAX_LOG_LINES = 40


def _git(*args: str, cwd: str = ".") -> tuple[str, str, int]:
    """Run a git command and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class GitSkill:
    """Run common git operations on a local repository."""

    name = "git"
    description = (
        "Run git operations on a local repository (git must be installed). "
        "Supported actions: 'status' (repo_path); 'log' (repo_path, lines); "
        "'diff' (repo_path); 'add' (repo_path, files); "
        "'commit' (repo_path, message); 'branch' (repo_path, branch); "
        "'checkout' (repo_path, branch); 'init' (repo_path); "
        "'show' (repo_path, commit)."
    )

    # Whitelist of allowed git subcommands to prevent injection.
    _ALLOWED = {
        "status", "log", "diff", "add", "commit",
        "branch", "checkout", "init", "show",
    }

    def run(
        self,
        action: str,
        repo_path: str = ".",
        message: str = "",
        files: str = ".",
        branch: str = "",
        commit: str = "HEAD",
        lines: int = 10,
    ) -> str:
        """
        Perform a git operation.

        Parameters
        ----------
        action:
            One of ``"status"``, ``"log"``, ``"diff"``, ``"add"``,
            ``"commit"``, ``"branch"``, ``"checkout"``, ``"init"``,
            ``"show"``.
        repo_path:
            Path to the local git repository (default: current directory).
        message:
            Commit message (required for ``"commit"``).
        files:
            Space-separated file paths to stage (for ``"add"``; default ``"."``)
        branch:
            Branch name (for ``"branch"`` / ``"checkout"``).
        commit:
            Commit ref for ``"show"`` (default ``"HEAD"``).
        lines:
            Number of log entries to show (default 10).

        Returns
        -------
        str
            Command output or error message prefixed with ``"Error: "``.
        """
        if not shutil.which("git"):
            return "Error: git binary not found – please install git"

        action = action.strip().lower()
        if action not in self._ALLOWED:
            return (
                f"Error: unknown action {action!r}. "
                f"Use one of: {', '.join(sorted(self._ALLOWED))}"
            )

        if action == "status":
            return self._run_or_error(["status"], repo_path)

        if action == "log":
            n = max(1, min(int(lines), _MAX_LOG_LINES))
            return self._run_or_error(
                ["log", f"--oneline", f"-{n}"], repo_path
            )

        if action == "diff":
            return self._run_or_error(["diff"], repo_path) or "(no changes)"

        if action == "add":
            paths = files.split() if files.strip() else ["."]
            return self._run_or_error(["add", "--", *paths], repo_path)

        if action == "commit":
            if not message:
                return "Error: message is required for commit"
            return self._run_or_error(["commit", "-m", message], repo_path)

        if action == "branch":
            if branch:
                return self._run_or_error(["branch", branch], repo_path)
            return self._run_or_error(["branch", "--list"], repo_path)

        if action == "checkout":
            if not branch:
                return "Error: branch is required for checkout"
            return self._run_or_error(["checkout", branch], repo_path)

        if action == "init":
            return self._run_or_error(["init"], repo_path)

        if action == "show":
            return self._run_or_error(
                ["show", "--stat", commit], repo_path
            )

        return f"Error: unhandled action {action!r}"

    @staticmethod
    def _run_or_error(args: list[str], cwd: str) -> str:
        stdout, stderr, rc = _git(*args, cwd=cwd)
        if rc != 0:
            msg = stderr or stdout or f"git {args[0]} failed (exit {rc})"
            return f"Error: {msg}"
        return stdout or f"(git {args[0]} completed successfully)"
