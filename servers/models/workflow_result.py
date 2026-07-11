from dataclasses import dataclass, field

from servers.models.checkpoint_result import CheckpointResult
from servers.models.comparison import ComparisonResult
from servers.models.delete_result import DeleteResult
from servers.models.upload_result import UploadResult


@dataclass
class SyncWorkflowResult:
    """Overall result of one server synchronization workflow."""

    server_name: str
    dry_run: bool = False

    comparison: ComparisonResult | None = None
    checkpoint: CheckpointResult | None = None
    upload: UploadResult | None = None
    deletion: DeleteResult | None = None

    completed_steps: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not self.errors and "complete" in self.completed_steps