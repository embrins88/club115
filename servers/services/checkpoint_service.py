from __future__ import annotations

import json
import shlex
from datetime import datetime, timezone

from servers.models.checkpoint_result import CheckpointResult
from servers.models.comparison import ComparisonResult
from servers.models.server import Server
from servers.services.ssh_service import SSHService


class CheckpointService:
    """Create a rollback checkpoint before synchronizing server files."""

    def __init__(
        self,
        server: Server,
        comparison: ComparisonResult,
    ) -> None:
        self.server = server
        self.comparison = comparison
        self.ssh = SSHService(server)

    def run(self) -> CheckpointResult:
        """Create a numbered checkpoint and return its details."""

        if self.comparison.errors:
            raise RuntimeError(
                "Cannot create a checkpoint from a failed comparison."
            )

        checkpoint_root = (
            f"/home/{self.server.ssh_user}/minecraft/checkpoints/"
            f"{self.server.server_id}"
        )

        checkpoint_id = self._get_next_checkpoint_id(checkpoint_root)
        checkpoint_directory = f"{checkpoint_root}/{checkpoint_id}"

        archive_path = f"{checkpoint_directory}/files.tar"
        manifest_path = f"{checkpoint_directory}/manifest.json"
        file_list_path = f"{checkpoint_directory}/files-to-save.txt"

        files_to_save = sorted(
            {
                change.path
                for change in (
                    self.comparison.updated
                    + self.comparison.removed
                )
            }
        )

        manifest = {
            "checkpoint_id": checkpoint_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "server_id": self.server.server_id,
            "server_name": self.server.name,
            "remote_root": self.server.remote_root,
            "service": self.server.service,
            "reason": "pre-sync",
            "added": [
                change.path for change in self.comparison.added
            ],
            "updated": [
                change.path for change in self.comparison.updated
            ],
            "removed": [
                change.path for change in self.comparison.removed
            ],
        }

        self.ssh.mkdir(checkpoint_directory)

        self.ssh.write_text(
            manifest_path,
            json.dumps(manifest, indent=2),
        )

        if files_to_save:
            file_list_content = "".join(
                f"{relative_path}\n"
                for relative_path in files_to_save
            )

            self.ssh.write_text(
                file_list_path,
                file_list_content,
            )

            command = (
                f"cd {shlex.quote(self.server.remote_root)} && "
                f"tar -cf {shlex.quote(archive_path)} "
                f"-T {shlex.quote(file_list_path)}"
            )

            self.ssh.run(command)
            created_archive: str | None = archive_path
        else:
            created_archive = None

        return CheckpointResult(
            checkpoint_id=checkpoint_id,
            remote_directory=checkpoint_directory,
            manifest_path=manifest_path,
            archive_path=created_archive,
            files_saved=len(files_to_save),
        )

    def _get_next_checkpoint_id(
        self,
        checkpoint_root: str,
    ) -> str:
        """Return the next checkpoint ID, such as CP000001."""

        command = (
            f"mkdir -p {shlex.quote(checkpoint_root)} && "
            f"find {shlex.quote(checkpoint_root)} "
            "-maxdepth 1 -mindepth 1 -type d "
            "-printf '%f\n' "
            "| grep -E '^CP[0-9]{6}$' "
            "| sort "
            "| tail -n 1"
        )

        result = self.ssh.run(
            command,
            check=False,
        )

        if result.exit_code not in (0, 1):
            raise RuntimeError(
                "Could not determine the next checkpoint ID"
                + (
                    f": {result.stderr}"
                    if result.stderr
                    else "."
                )
            )

        latest_id = result.stdout.strip()

        if not latest_id:
            return "CP000001"

        next_number = int(latest_id[2:]) + 1
        return f"CP{next_number:06d}"