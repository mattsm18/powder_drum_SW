#
# Title: models/storage_model.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Passive state for internal and USB storage

from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto

class MediaType(Enum):
    VIDEO = auto()
    STILL = auto()

@dataclass
class FileEntry:
    path: Path
    size_bytes: int
    media_type: MediaType
    created_at: float

@dataclass
class StorageState:
    files: list[FileEntry] = field(default_factory=list)
    used_bytes: int = 0
    quota_bytes: int = 4 * 1000 * 1000 * 1000 

@dataclass
class StorageModel:
    internal: StorageState = field(default_factory=StorageState)
    usb: StorageState | None = None
    usb_mount_path: Path | None = None