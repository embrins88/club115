from dataclasses import dataclass, field


@dataclass(frozen=True)
class FileChange:
    """One file difference between the client and server."""

    path: str
    local_hash: str | None = None
    remote_hash: str | None = None


@dataclass
class ComparisonResult:
    """Results returned by ComparisonService."""

    server_name: str
    added: list[FileChange] = field(default_factory=list)
    updated: list[FileChange] = field(default_factory=list)
    removed: list[FileChange] = field(default_factory=list)
    skipped_directories: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.updated or self.removed)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.updated) + len(self.removed)