from dataclasses import dataclass


@dataclass(frozen=True)
class Colors:
    background = "#FFFFFF"
    foreground = "#000000"

    white = "#FFFFFF"
    black = "#000000"

    margin_debug = "#F8CB9C"
    border_debug = "#E2E051"
    padding_debug = "#C2DDB6"
    content_debug = "#9FC4E7"
