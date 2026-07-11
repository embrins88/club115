from __future__ import annotations

import shlex
from pathlib import PurePosixPath

from servers.models.comparison import ComparisonResult
from servers.models.delete_result import DeleteResult
from servers.models.server import Server
from servers.services.ssh_service import SSHService


class DeleteService:
    """Delete remote files approved by a comparison result."""

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

    def run(self) -> DeleteResult:
        """Delete obsolete remote files or preview the operation."""

        result = DeleteResult(server_name=self.server.name)

        if self.comparison.errors:
            result.errors.append(
                "Deletion refused because the comparison contains errors."
            )
            return result

        if self.dry_run:
            result.planned.extend(
                change.path for change in self.comparison.removed
            )
            return result

        try:
            with self.ssh.session() as session:
                for change in self.comparison.removed:
                    try:
                        relative_path = self._validate_relative_path(
                            change.path
                        )

                        command = (
                            f"cd {shlex.quote(self.server.remote_root)} && "
                            f"rm -f -- {shlex.quote(relative_path)}"
                        )

                        session.run(command)
                        result.deleted.append(change.path)

                    except Exception as error:
                        result.errors.append(
                            f"Could not delete '{change.path}': {error}"
                        )

        except Exception as error:
            result.errors.append(
                f"Could not open deletion session: {error}"
            )

        return result

    @staticmethod
    def _validate_relative_path(relative_path: str) -> str:
        """Ensure a deletion target cannot escape the server root."""

        normalized = PurePosixPath(relative_path)

        if normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError(
                f"Unsafe remote relative path: {relative_path}"
            )

        return normalized.as_posix()