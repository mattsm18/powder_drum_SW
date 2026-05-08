#
# Title: config/config.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose:
# - Single source of truth loader for application configuration
# - All modules import from here rather than hardcoding values

import json
import os

from dataclasses import dataclass
from typing import Any


# ──────────────────────────────────────────────────────
# Parameter Dataclass
# ──────────────────────────────────────────────────────

@dataclass(slots=True)
class Parameter:

    id: int

    name: str
    label: str

    access: str
    type: type

    default: Any

    min: float | int
    max: float | int

    unit: str
    group: str

    @staticmethod
    def from_dict(data: dict) -> "Parameter":

        type_map = {
            "float": float,
            "int": int,
            "bool": bool,
            "str": str
        }

        return Parameter(
            id=int(data["id"], 16),

            name=data["name"],
            label=data["label"],

            access=data["access"],
            type=type_map[data["type"]],

            default=data["default"],

            min=data["min"],
            max=data["max"],

            unit=data["unit"],
            group=data["group"]
        )


# ──────────────────────────────────────────────────────
# Config Load
# ──────────────────────────────────────────────────────

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config.json"
)

_config: dict = {}


def load() -> dict:

    global _config
    if not _config:
        with open(_CONFIG_PATH, "r") as f: _config = json.load(f)
    return _config


def reload() -> dict:

    global _config
    _config = {}
    return load()


# ──────────────────────────────────────────────────────
# Parameter Access
# ──────────────────────────────────────────────────────

# Get all parameters in group and optionally by access privledge level
def get_parameters(group: str | None = None, access: str | None = None) -> list[Parameter]:

    params = load()["parameters"]

    if group: params = [p for p in params if p["group"] == group]
    if access: params = [p for p in params if access in p["access"]]

    return [Parameter.from_dict(p) for p in params]

# Get Parameter by name
def get_parameter(name: str) -> Parameter | None:

    param = next(
        (p for p in load()["parameters"] if p["name"] == name),
        None
    )

    # did not find parameter by name
    if not param: return None

    return Parameter.from_dict(param)

# Get Parameter by hex_id -> Used for Serial Comms
def get_parameter_by_id(param_id: int) -> Parameter | None:

    param = next(
        (
            p for p in load()["parameters"]
            if int(p["id"], 16) == param_id
        ),
        None
    )

    if not param: return None
    return Parameter.from_dict(param)

# ──────────────────────────────────────────────────────
# Config Block Accessors
# ──────────────────────────────────────────────────────

def get_ui_config() -> dict:     return load()["ui"]
def get_serial_config() -> dict: return load()["serial"]
def get_camera_config() -> dict: return load()["camera"]
def get_vision_config() -> dict: return load()["vision"]