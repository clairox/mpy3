import json
from pathlib import Path
from typing import Dict
from urllib.parse import unquote, urlparse

SETTINGS_PATH = "settings.json"


def load():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as infile:
            app_settings = json.load(infile)
            last_played = Path(unquote(urlparse(app_settings["last_played"]).path))
            return {"last_played": last_played}
    except FileNotFoundError:
        return {}


def save(state: Dict[str, str]):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as outfile:
        json.dump(state, outfile)
