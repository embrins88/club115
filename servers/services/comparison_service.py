from __future__ import annotations

import fnmatch
import hashlib
import shlex
from pathlib import Path

from servers.models.comparison import ComparisonResult, FileChange
from servers.models.server import Server
from servers.services.ssh_service import SSHService


class ComparisonService:
    """Compare local CurseForge files with files on a remote server."""

    def __init__(self, server: Server) -> None:
        self.server = server
        self.ssh = SSHService(server)

    def run(self) -> ComparisonResult:
        """Build local and remote manifests and compare their contents."""

        result = ComparisonResult(server_name=self.server.name)

        try:
            local_manifest = self._build_local_manifest(result)
            remote_manifest = self._build_remote_manifest()
        except Exception as error:
            result.errors.append(str(error))
            return result

        local_paths = set(local_manifest)
        remote_paths = set(remote_manifest)

        # Files present locally but missing remotely.
        for relative_path in sorted(local_paths - remote_paths):
            result.added.append(
                FileChange(
                    path=relative_path,
                    local_hash=local_manifest[relative_path],
                )
            )

        # Files present remotely but missing locally.
        for relative_path in sorted(remote_paths - local_paths):
            if self._is_preserved(relative_path):
                continue

            result.removed.append(
                FileChange(
                    path=relative_path,
                    remote_hash=remote_manifest[relative_path],
                )
            )

        # Files present in both places but with different contents.
        for relative_path in sorted(local_paths & remote_paths):
            local_hash = local_manifest[relative_path]
            remote_hash = remote_manifest[relative_path]

            if local_hash != remote_hash:
                result.updated.append(
                    FileChange(
                        path=relative_path,
                        local_hash=local_hash,
                        remote_hash=remote_hash,
                    )
                )

        return result

    def _build_local_manifest(
        self,
        result: ComparisonResult,
    ) -> dict[str, str]:
        """Return local relative file paths mapped to SHA-256 hashes."""

        if not self.server.local_instance.exists():
            raise FileNotFoundError(
                f"Local CurseForge instance does not exist: "
                f"{self.server.local_instance}"
            )

        if not self.server.local_instance.is_dir():
            raise NotADirectoryError(
                f"Local CurseForge instance is not a directory: "
                f"{self.server.local_instance}"
            )

        manifest: dict[str, str] = {}

        for directory_name in self.server.sync_directories:
            local_directory = self.server.local_directory(directory_name)

            if not local_directory.exists():
                result.skipped_directories.append(directory_name)
                continue

            if not local_directory.is_dir():
                result.errors.append(
                    f"Configured local sync path is not a directory: "
                    f"{local_directory}"
                )
                continue

            for file_path in local_directory.rglob("*"):
                if not file_path.is_file():
                    continue

                relative_path = file_path.relative_to(
                    self.server.local_instance
                ).as_posix()

                if self._is_ignored(relative_path):
                    continue

                manifest[relative_path] = self._hash_local_file(file_path)

        return manifest

    def _build_remote_manifest(self) -> dict[str, str]:
        """Return remote relative file paths mapped to SHA-256 hashes."""

        command = self._build_remote_hash_command()
        command_result = self.ssh.run(command)

        manifest: dict[str, str] = {}

        for line in command_result.stdout.splitlines():
            if not line.strip():
                continue

            file_hash, separator, relative_path = line.partition("  ")

            if not separator:
                continue

            relative_path = relative_path.strip()

            if self._is_ignored(relative_path):
                continue

            manifest[relative_path] = file_hash.strip()

        return manifest

    def _build_remote_hash_command(self) -> str:
        """Build the Ubuntu command used to hash managed server files."""

        remote_root = shlex.quote(self.server.remote_root)
        find_commands: list[str] = []

        for directory_name in self.server.sync_directories:
            quoted_directory = shlex.quote(directory_name)

            find_commands.append(
                f"if [ -d {quoted_directory} ]; then "
                f"find {quoted_directory} -type f -print0; fi"
            )

        combined_find = "; ".join(find_commands)

        return (
            f"cd {remote_root} && "
            f"{{ {combined_find}; }} "
            "| sort -z "
            "| xargs -0 -r sha256sum"
        )

    def _is_ignored(self, relative_path: str) -> bool:
        """Return True when a file should be excluded from comparison."""

        normalized_path = relative_path.replace("\\", "/")

        return any(
            fnmatch.fnmatch(normalized_path, pattern)
            for pattern in self.server.ignore_patterns
        )

    def _is_preserved(self, relative_path: str) -> bool:
        """Return True when a remote-only file must not be removed."""

        normalized_path = relative_path.replace("\\", "/")

        return any(
            fnmatch.fnmatch(normalized_path, pattern)
            for pattern in self.server.preserve_patterns
        )

    @staticmethod
    def _hash_local_file(file_path: Path) -> str:
        """Calculate the SHA-256 hash of one local file."""

        digest = hashlib.sha256()

        with file_path.open("rb") as local_file:
            while chunk := local_file.read(1024 * 1024):
                digest.update(chunk)

        return digest.hexdigest()