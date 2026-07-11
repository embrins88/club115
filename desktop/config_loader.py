from pathlib import Path
import json


CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> dict:
    """Load the desktop app configuration."""

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Desktop config file not found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)