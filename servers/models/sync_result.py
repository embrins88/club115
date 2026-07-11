from dataclasses import dataclass, field


@dataclass
class SyncResult:
    """Results returned by SyncService."""

    server_name: str

    backup_created: bool = False
    server_stopped: bool = False
    files_uploaded: int = 0
    files_deleted: int = 0
    server_started: bool = False
    server_verified: bool = False

    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not self.errors and self.server_verified