"""Archive skill – create, list, and extract zip and tar archives.

Covers the "CLI Utilities" category from the awesome-openclaw-skills
directory.  Uses Python stdlib only (``zipfile``, ``tarfile``).

Supported actions
-----------------
create_zip      Create a new zip archive from files.
extract_zip     Extract a zip archive to a directory.
list_zip        List contents of a zip archive.
add_to_zip      Add a file to an existing zip archive.
create_tar      Create a tar (.tar.gz) archive from files.
extract_tar     Extract a tar archive.
list_tar        List contents of a tar archive.
"""

from __future__ import annotations

import os
import tarfile
import zipfile
from pathlib import Path


class ArchiveSkill:
    """Create, list, and extract zip and tar archives."""

    name = "archive"
    description = (
        "Manage zip and tar archives. "
        "Supported actions: 'create_zip' (archive, files); "
        "'extract_zip' (archive, dest); 'list_zip' (archive); "
        "'add_to_zip' (archive, files); 'create_tar' (archive, files); "
        "'extract_tar' (archive, dest); 'list_tar' (archive)."
        "\nfiles: space-separated file/directory paths."
    )

    def run(
        self,
        action: str,
        archive: str = "",
        files: str = "",
        dest: str = ".",
    ) -> str:
        """
        Perform an archive operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        archive:
            Path to the archive file.
        files:
            Space-separated list of files/directories to include.
        dest:
            Destination directory for extraction (default current dir).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "create_zip":
            return self._create_zip(archive, files)
        if action == "extract_zip":
            return self._extract_zip(archive, dest)
        if action == "list_zip":
            return self._list_zip(archive)
        if action == "add_to_zip":
            return self._add_to_zip(archive, files)
        if action == "create_tar":
            return self._create_tar(archive, files)
        if action == "extract_tar":
            return self._extract_tar(archive, dest)
        if action == "list_tar":
            return self._list_tar(archive)
        return (
            f"Error: unknown action {action!r}. "
            "Use create_zip, extract_zip, list_zip, add_to_zip, "
            "create_tar, extract_tar, or list_tar."
        )

    # ------------------------------------------------------------------
    # ZIP helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _create_zip(archive: str, files: str) -> str:
        if not archive:
            return "Error: archive path is required"
        if not files:
            return "Error: files is required for create_zip"
        try:
            file_list = files.split()
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for f in file_list:
                    p = Path(f)
                    if not p.exists():
                        return f"Error: file {f!r} not found"
                    if p.is_dir():
                        for fp in p.rglob("*"):
                            if fp.is_file():
                                zf.write(fp)
                    else:
                        zf.write(p)
            return f"Created {archive!r} with {len(file_list)} source(s)"
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _extract_zip(archive: str, dest: str) -> str:
        if not archive:
            return "Error: archive path is required"
        if not Path(archive).exists():
            return f"Error: archive {archive!r} not found"
        try:
            with zipfile.ZipFile(archive, "r") as zf:
                zf.extractall(dest)
                names = zf.namelist()
            return f"Extracted {len(names)} file(s) to {dest!r}"
        except zipfile.BadZipFile:
            return f"Error: {archive!r} is not a valid zip file"
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _list_zip(archive: str) -> str:
        if not archive:
            return "Error: archive path is required"
        if not Path(archive).exists():
            return f"Error: archive {archive!r} not found"
        try:
            with zipfile.ZipFile(archive, "r") as zf:
                infos = zf.infolist()
            if not infos:
                return "(empty archive)"
            lines = [f"{'Name':<40} {'Size':>10}"]
            lines.append("-" * 52)
            for info in infos:
                lines.append(f"{info.filename:<40} {info.file_size:>10,} B")
            return "\n".join(lines)
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _add_to_zip(archive: str, files: str) -> str:
        if not archive:
            return "Error: archive path is required"
        if not files:
            return "Error: files is required"
        try:
            file_list = files.split()
            mode = "a" if Path(archive).exists() else "w"
            with zipfile.ZipFile(archive, mode, compression=zipfile.ZIP_DEFLATED) as zf:
                for f in file_list:
                    p = Path(f)
                    if not p.exists():
                        return f"Error: file {f!r} not found"
                    zf.write(p)
            return f"Added {len(file_list)} file(s) to {archive!r}"
        except Exception as exc:
            return f"Error: {exc}"

    # ------------------------------------------------------------------
    # TAR helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _create_tar(archive: str, files: str) -> str:
        if not archive:
            return "Error: archive path is required"
        if not files:
            return "Error: files is required for create_tar"
        try:
            file_list = files.split()
            mode = "w:gz" if archive.endswith(".gz") else "w"
            with tarfile.open(archive, mode) as tf:
                for f in file_list:
                    if not Path(f).exists():
                        return f"Error: file {f!r} not found"
                    tf.add(f)
            return f"Created {archive!r} with {len(file_list)} source(s)"
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _extract_tar(archive: str, dest: str) -> str:
        if not archive:
            return "Error: archive path is required"
        if not Path(archive).exists():
            return f"Error: archive {archive!r} not found"
        try:
            with tarfile.open(archive) as tf:
                # Security: filter to avoid path traversal
                members = tf.getmembers()
                tf.extractall(dest, filter="data")
            return f"Extracted {len(members)} member(s) to {dest!r}"
        except tarfile.TarError as exc:
            return f"Error: {exc}"
        except TypeError:
            # Python < 3.12 doesn't have the filter parameter
            try:
                with tarfile.open(archive) as tf:
                    members = tf.getmembers()
                    tf.extractall(dest)
                return f"Extracted {len(members)} member(s) to {dest!r}"
            except Exception as exc2:
                return f"Error: {exc2}"
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _list_tar(archive: str) -> str:
        if not archive:
            return "Error: archive path is required"
        if not Path(archive).exists():
            return f"Error: archive {archive!r} not found"
        try:
            with tarfile.open(archive) as tf:
                members = tf.getmembers()
            if not members:
                return "(empty archive)"
            lines = [f"{'Name':<40} {'Size':>10}"]
            lines.append("-" * 52)
            for m in members:
                lines.append(f"{m.name:<40} {m.size:>10,} B")
            return "\n".join(lines)
        except Exception as exc:
            return f"Error: {exc}"
