from dataclasses import dataclass
from pathlib import Path


DEFAULT_SYNC_DIRECTORIES = (
    "mods",
    "config",
    "defaultconfigs",
)


@dataclass(frozen=True)
class Server:
    """Configuration for one managed Minecraft server."""

    server_id: str
    name: str

    ssh_host: str
    ssh_user: str
    ssh_key: Path

    local_instance: Path
    remote_root: str

    service: str
    game_port: int
    rcon_port: int
    world_name: str

    sync_directories: tuple[str, ...] = DEFAULT_SYNC_DIRECTORIES
    preserve_patterns: tuple[str, ...] = ()
    ignore_patterns: tuple[str, ...] = ()

    def local_directory(self, directory: str) -> Path:
        return self.local_instance / directory

    def remote_directory(self, directory: str) -> str:
        return f"{self.remote_root.rstrip('/')}/{directory}"

    @property
    def local_mods(self) -> Path:
        return self.local_directory("mods")

    @property
    def local_config(self) -> Path:
        return self.local_directory("config")

    @property
    def local_defaultconfigs(self) -> Path:
        return self.local_directory("defaultconfigs")

    @property
    def local_kubejs(self) -> Path:
        return self.local_directory("kubejs")

    @property
    def local_resourcepacks(self) -> Path:
        return self.local_directory("resourcepacks")

    @property
    def remote_mods(self) -> str:
        return self.remote_directory("mods")

    @property
    def remote_config(self) -> str:
        return self.remote_directory("config")

    @property
    def remote_defaultconfigs(self) -> str:
        return self.remote_directory("defaultconfigs")

    @property
    def remote_kubejs(self) -> str:
        return self.remote_directory("kubejs")

    @property
    def remote_resourcepacks(self) -> str:
        return self.remote_directory("resourcepacks")

    def __str__(self) -> str:
        return self.name