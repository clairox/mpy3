"""
This module handles loading and saving app state
"""

import json
from pathlib import Path
from typing import NotRequired, TypedDict

from utils import extract_path

SETTINGS_PATH = "settings.json"


class AppState(TypedDict):
    """
    State of the app
    """

    last_played: NotRequired[Path]


def load() -> AppState:
    """
    Loads state from settings file
    """

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as infile:
            app_settings = json.load(infile)
            last_played = extract_path(Path(app_settings["last_played"]))
            return {"last_played": last_played}
    except FileNotFoundError:
        return {}


def save(state: AppState):
    """
    Saves state to settings file
    """

    with open(SETTINGS_PATH, "w", encoding="utf-8") as outfile:
        json.dump(state, outfile)
