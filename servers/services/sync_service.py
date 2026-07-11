from __future__ import annotations

from servers.models.server import Server
from servers.models.sync_result import SyncResult
from servers.services.comparison_service import ComparisonService


class SyncService:
    """Synchronize local Minecraft files to a remote server."""

    def __init__(self, server: Server) -> None:
        self.server = server

    def run(self) -> SyncResult:
        """Compare files and refuse to continue if comparison fails."""

        result = SyncResult(server_name=self.server.name)

        comparison_service = ComparisonService(self.server)
        comparison = comparison_service.run()

        if comparison.errors:
            result.errors.extend(comparison.errors)
            result.messages.append(
                "Sync stopped because the comparison failed."
            )
            return result

        if not comparison.has_changes:
            result.messages.append("No changes detected.")
            result.server_verified = True
            return result

        result.messages.append(
            f"Ready to sync {comparison.total_changes} change(s)."
        )

        # Actual backup, stop, upload, delete, restart, and verification
        # will be added next.

        return result