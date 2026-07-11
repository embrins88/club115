from dataclasses import dataclass, field


@dataclass
class DeleteResult:
    """Results returned by DeleteService."""

    server_name: str
    deleted: list[str] = field(default_factory=list)
    planned: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not self.errors

    @property
    def files_deleted(self) -> int:
        return len(self.deleted)