from pathlib import Path
from typing import Any

import yaml

from servers.models.server import Server


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "servers.yaml"


def load_config() -> dict[str, Any]:
    """Load and validate the Club 115 server configuration."""

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Could not find server configuration: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError("servers.yaml must contain a YAML mapping.")

    if "ssh" not in config:
        raise ValueError("servers.yaml is missing the 'ssh' section.")

    if "servers" not in config:
        raise ValueError("servers.yaml is missing the 'servers' section.")

    if not isinstance(config["servers"], dict):
        raise ValueError("'servers' must contain a YAML mapping.")

    return config


def get_server(server_id: str) -> Server:
    """Return one configured server as a Server object."""

    config = load_config()
    servers = config["servers"]

    if server_id not in servers:
        available = ", ".join(servers.keys())
        raise KeyError(
            f"Unknown server '{server_id}'. Available servers: {available}"
        )

    data = servers[server_id]
    ssh = config["ssh"]
    sync = data.get("sync", {})

    try:
        configured_directories = sync.get(
            "directories",
            [
                "mods",
                "config",
                "defaultconfigs",
            ],
        )

        preserve_patterns = sync.get("preserve", [])
        ignore_patterns = sync.get("ignore", [])

        return Server(
            server_id=server_id,
            name=data["name"],
            ssh_host=ssh["host"],
            ssh_user=ssh["user"],
            ssh_key=Path(ssh["key"]).expanduser(),
            local_instance=Path(data["local"]["instance"]),
            remote_root=data["remote"]["root"],
            service=data["service"],
            game_port=int(data["game_port"]),
            rcon_port=int(data["rcon_port"]),
            world_name=data["world"]["name"],
            sync_directories=tuple(configured_directories),
            preserve_patterns=tuple(preserve_patterns),
            ignore_patterns=tuple(ignore_patterns),
        )

    except KeyError as error:
        missing_field = error.args[0]
        raise ValueError(
            f"Server '{server_id}' is missing required field: "
            f"{missing_field}"
        ) from error
    
def get_servers() -> dict[str, Server]:
    """Return every configured server, keyed by server ID."""

    config = load_config()

    return {
        server_id: get_server(server_id)
        for server_id in config["servers"]
    }