from __future__ import annotations

from servers.models.server import Server
from servers.models.workflow_result import SyncWorkflowResult
from servers.services.checkpoint_service import CheckpointService
from servers.services.comparison_service import ComparisonService
from servers.services.delete_service import DeleteService
from servers.services.server_service import ServerControlService
from servers.services.upload_service import UploadService


class SyncWorkflow:
    """Coordinate a complete Minecraft server synchronization."""

    def __init__(
        self,
        server: Server,
        *,
        dry_run: bool = False,
    ) -> None:
        self.server = server
        self.dry_run = dry_run

    def run(self) -> SyncWorkflowResult:
        """Run the synchronization workflow."""

        result = SyncWorkflowResult(
            server_name=self.server.name,
            dry_run=self.dry_run,
        )

        server_was_running = False
        server_service = ServerControlService(self.server)

        try:
            comparison = ComparisonService(self.server).run()
            result.comparison = comparison
            result.completed_steps.append("comparison")

            if comparison.errors:
                result.errors.extend(comparison.errors)
                result.messages.append(
                    "Workflow stopped during comparison."
                )
                return result

            if not comparison.has_changes:
                result.completed_steps.append("complete")
                result.messages.append("No changes detected.")
                return result

            result.messages.append(
                f"{comparison.total_changes} change(s) detected."
            )

            if self.dry_run:
                upload_preview = UploadService(
                    self.server,
                    comparison,
                    dry_run=True,
                ).run()

                delete_preview = DeleteService(
                    self.server,
                    comparison,
                    dry_run=True,
                ).run()

                result.upload = upload_preview
                result.deletion = delete_preview

                if upload_preview.errors:
                    result.errors.extend(upload_preview.errors)

                if delete_preview.errors:
                    result.errors.extend(delete_preview.errors)

                if result.errors:
                    return result

                result.completed_steps.extend(
                    [
                        "upload-preview",
                        "delete-preview",
                        "complete",
                    ]
                )

                result.messages.append(
                    f"Would upload "
                    f"{len(upload_preview.planned)} file(s)."
                )
                result.messages.append(
                    f"Would delete "
                    f"{len(delete_preview.planned)} file(s)."
                )

                return result

            checkpoint = CheckpointService(
                self.server,
                comparison,
            ).run()

            result.checkpoint = checkpoint
            result.completed_steps.append("checkpoint")
            result.messages.append(
                f"Created checkpoint {checkpoint.checkpoint_id}."
            )

            initial_status = server_service.get_status()
            server_was_running = initial_status.is_running

            if server_was_running:
                server_service.stop()
                result.completed_steps.append("stop")
                result.messages.append("Server stopped.")

            upload = UploadService(
                self.server,
                comparison,
            ).run()

            result.upload = upload

            if upload.errors:
                result.errors.extend(upload.errors)
                return result

            result.completed_steps.append("upload")
            result.messages.append(
                f"Uploaded {upload.files_uploaded} file(s)."
            )

            deletion = DeleteService(
                self.server,
                comparison,
            ).run()

            result.deletion = deletion

            if deletion.errors:
                result.errors.extend(deletion.errors)
                return result

            result.completed_steps.append("delete")
            result.messages.append(
                f"Deleted {deletion.files_deleted} file(s)."
            )

            if server_was_running:
                status = server_service.start()

                if not status.is_running:
                    raise RuntimeError(
                        "The server did not return to a running state."
                    )

                result.completed_steps.append("start")
                result.messages.append("Server started.")

            result.completed_steps.append("complete")
            result.messages.append("Synchronization completed.")

            return result

        except Exception as error:
            result.errors.append(str(error))
            return result

        finally:
            if (
                not self.dry_run
                and server_was_running
                and "start" not in result.completed_steps
            ):
                try:
                    server_service.start()
                    result.messages.append(
                        "Server restart attempted after workflow failure."
                    )
                except Exception as restart_error:
                    result.errors.append(
                        f"Emergency restart failed: {restart_error}"
                    )