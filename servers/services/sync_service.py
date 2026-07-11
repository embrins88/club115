from __future__ import annotations

from servers.models.workflow_result import SyncWorkflowResult
from servers.services.server_config import get_server
from servers.workflows.sync_workflow import SyncWorkflow


class SyncService:
    """Public interface for previewing and running server synchronization."""

    def preview(self, server_id: str) -> SyncWorkflowResult:
        """Preview synchronization without modifying the server."""

        server = get_server(server_id)

        workflow = SyncWorkflow(
            server,
            dry_run=True,
        )

        return workflow.run()

    def sync(self, server_id: str) -> SyncWorkflowResult:
        """Run a live synchronization workflow."""

        server = get_server(server_id)

        workflow = SyncWorkflow(
            server,
            dry_run=False,
        )

        return workflow.run()