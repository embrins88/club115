from __future__ import annotations

from copy import error
import shlex
from pathlib import Path, PurePosixPath
from unittest import result

from servers.models import server
from servers.models.comparison import ComparisonResult
from servers.models.server import Server
from servers.models.upload_result import UploadResult
from servers.services.ssh_service import SSHService


class UploadService:
    """Upload added and updated client files to a remote server."""

    def __init__(
        self,
        server: Server,
        comparison: ComparisonResult,
        *,
        dry_run: bool = False,
    ) -> None:
        self.server = server
        self.comparison = comparison
        self.dry_run = dry_run
        self.ssh = SSHService(server)

    def run(self) -> UploadResult:
        """Upload approved files or preview the operation."""

        result = UploadResult(server_name=self.server.name)

        if self.comparison.errors:
            result.errors.append(
                "Upload refused because the comparison contains errors."
            )
            return result

        changes = self.comparison.added + self.comparison.updated

        if self.dry_run:
            result.planned.extend(change.path for change in changes)
            return result

        try:
            with self.ssh.session() as session:
                for change in changes:
                    try:
                        local_path = self._get_local_path(change.path)
                        remote_path = self._get_remote_path(change.path)

                        parent = str(PurePosixPath(remote_path).parent)

                        session.run(
                            f"mkdir -p {shlex.quote(parent)}"
                        )

                        session.upload(local_path, remote_path)
                        result.uploaded.append(change.path)

                    except Exception as error:
                        result.errors.append(
                            f"Could not upload '{change.path}': {error}"
                        )

        except Exception as error:
            result.errors.append(
                f"Could not open upload session: {error}"
            )

        return result

    def _get_local_path(self, relative_path: str) -> Path:
        """Resolve and validate one local file path."""

        local_path = (
            self.server.local_instance
            / Path(relative_path)
        ).resolve()

        instance_root = self.server.local_instance.resolve()

        try:
            local_path.relative_to(instance_root)
        except ValueError as error:
            raise ValueError(
                f"Path escapes the local instance: {relative_path}"
            ) from error

        if not local_path.is_file():
            raise FileNotFoundError(
                f"Local file does not exist: {local_path}"
            )

        return local_path

    def _get_remote_path(self, relative_path: str) -> str:
        """Build one validated remote destination path."""

        normalized = PurePosixPath(relative_path)

        if normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError(
                f"Unsafe remote relative path: {relative_path}"
            )

        return (
            f"{self.server.remote_root.rstrip('/')}/"
            f"{normalized.as_posix()}"
        )

    def _create_remote_parent(self, remote_path: str) -> None:
        """Create the destination's parent directory if needed."""

        parent = str(PurePosixPath(remote_path).parent)

        self.ssh.run(
            f"mkdir -p {shlex.quote(parent)}"
        )