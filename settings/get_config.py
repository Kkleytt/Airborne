import json
from pathlib import Path


def get_config():
    config_path = Path(__file__).resolve().parent / "local_settings.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config
