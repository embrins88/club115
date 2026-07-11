from dataclasses import dataclass, field


@dataclass
class UploadResult:
    """Results returned by UploadService."""

    server_name: str
    uploaded: list[str] = field(default_factory=list)
    planned: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not self.errors

    @property
    def files_uploaded(self) -> int:
        return len(self.uploaded)