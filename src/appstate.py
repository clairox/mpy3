import json
from pathlib import Path
from typing import NotRequired, TypedDict
from urllib.parse import unquote, urlparse

from utils import extract_path

SETTINGS_PATH = "settings.json"


class AppState(TypedDict):
    last_played: NotRequired[Path]


def load() -> AppState:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as infile:
            app_settings = json.load(infile)
            last_played = extract_path(Path(app_settings["last_played"]))
            return {"last_played": last_played}
    except FileNotFoundError:
        return {}


def save(state: AppState):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as outfile:
        json.dump(state, outfile)
