from dataclasses import dataclass


@dataclass(frozen=True)
class CheckpointResult:
    """Information about a successfully created sync checkpoint."""

    checkpoint_id: str
    remote_directory: str
    manifest_path: str
    archive_path: str | None
    files_saved: int