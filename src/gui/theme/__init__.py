#
# Title: theme/__init__.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Theme tokens + widget-level QSS snippets; global chrome lives in theme.qss

from pathlib import Path

_GLOBAL_QSS_PATH = Path(__file__).with_name("theme.qss")


def load_global_stylesheet() -> str:
    """Qt global stylesheet loaded from theme/theme.qss (same folder as this package)."""
    return _GLOBAL_QSS_PATH.read_text(encoding="utf-8")


DARK_THEME = load_global_stylesheet()

# Colour tokens for use in Python code (keep in sync with theme.qss where duplicated)
COLOUR_GREEN      = "#00FF88"
COLOUR_BLUE       = "#00AAFF"
COLOUR_RED        = "#FF4444"
COLOUR_ORANGE     = "#FF8800"
COLOUR_BG         = "#1A1A1A"
COLOUR_SURFACE    = "#2A2A2A"
COLOUR_BORDER     = "#444444"
COLOUR_TEXT       = "#E0E0E0"
COLOUR_HEADING    = "#FFFFFF"
COLOUR_MUTED      = "#AAAAAA"
COLOUR_DIM        = "#666666"
COLOUR_HINT       = "#888888"
COLOUR_WHITE      = "#FFFFFF"
COLOUR_DISPLAY_BG = COLOUR_BG
COLOUR_DISPLAY_BORDER = "#555555"
COLOUR_STOP       = "#b53131"
COLOUR_STOPPING   = "#f51d1d"
COLOUR_LIGHT_ON   = "#004e8a"

# Inline widget styles (QSS snippets — centralised for widgets that cannot rely on global QSS alone)
STYLE_STUB_LABEL = f"color: {COLOUR_DIM}; font-size: 14px;"
STYLE_SECTION_TITLE = f"color: {COLOUR_HEADING}; padding-bottom: 4px;"
STYLE_SEPARATOR_LINE = f"color: {COLOUR_SURFACE};"


def stylesheet_compact_icon_button() -> str:
    return "min-height: 0px; min-width: 0px;"


def stylesheet_primary_action_button() -> str:
    return f"background-color: {COLOUR_BLUE}; color: {COLOUR_WHITE}; border: none;"


def stylesheet_danger_outline_button() -> str:
    return f"color: {COLOUR_RED}; border-color: {COLOUR_RED};"


def stylesheet_stop_idle_button() -> str:
    return f"background-color: {COLOUR_STOP}; color: {COLOUR_WHITE};"


def stylesheet_stop_pending_button() -> str:
    return f"background-color: {COLOUR_STOPPING}; color: {COLOUR_WHITE};"


def stylesheet_value_readout_pad(accent_colour: str) -> str:
    return (
        f"color: {accent_colour}; "
        f"background-color: {COLOUR_SURFACE}; "
        f"border: 1px solid {COLOUR_BORDER}; "
        "border-radius: 6px; "
        "min-height: 30px;"
    )


def stylesheet_numpad_display(*, invalid: bool = False) -> str:
    if invalid:
        return f"""
            background-color: {COLOUR_DISPLAY_BG};
            border: 1px solid {COLOUR_RED};
            border-radius: 4px;
            padding: 0px 8px;
            color: {COLOUR_RED};
        """
    return f"""
        background-color: {COLOUR_DISPLAY_BG};
        border: 1px solid {COLOUR_DISPLAY_BORDER};
        border-radius: 4px;
        padding: 0px 8px;
        color: {COLOUR_WHITE};
    """
