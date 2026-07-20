#
# Title: managers/storage/storage_manager.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Filesystem operations for internal and USB storage locations

from pathlib import Path
from models.storage_model import FileEntry, MediaType

class StorageFullError(Exception): pass

class StorageManager():

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self, internal_root: Path):
        self._internal_root = internal_root
        self._internal_root.mkdir(parents=True, exist_ok=True)
        self._usb_root = None

    # PUBLIC API
    #--------------------------------------------------------------------------------------

    def set_usb_root(self, mount_path: Path | None):
        if mount_path is None:
            self._usb_root = None
            return
        self._usb_root = mount_path / "powder_drum_recordings"
        self._usb_root.mkdir(parents=True, exist_ok=True)

    #--------------------------------------------------------------------------------------

    def list_files(self, root: Path) -> list[FileEntry]:
        entries = []
        for p in root.rglob("*"):
            if p.is_file():
                mtype = MediaType.VIDEO if p.suffix.lower() in (".mp4", ".h264") else MediaType.STILL
                entries.append(FileEntry(p, p.stat().st_size, mtype, p.stat().st_mtime))
        return sorted(entries, key=lambda e: e.created_at, reverse=True)

    #--------------------------------------------------------------------------------------

    def get_usage(self, root: Path, quota_bytes: int) -> tuple[int, int]:
        used = sum(f.size_bytes for f in self.list_files(root))
        return used, quota_bytes

    #--------------------------------------------------------------------------------------

    def ensure_space(self, root: Path, quota_bytes: int, needed_bytes: int):
        used, _ = self.get_usage(root, quota_bytes)
        if used + needed_bytes > quota_bytes:
            raise StorageFullError(f"Not enough space in {root}")

    #--------------------------------------------------------------------------------------

    def delete(self, entry: FileEntry):
        entry.path.unlink(missing_ok=True)

    #--------------------------------------------------------------------------------------

    def copy_file(self, entry: FileEntry, dest_root: Path, progress_callback=None):
        dest_path = dest_root / entry.path.name
        with open(entry.path, "rb") as src, open(dest_path, "wb") as dst:
            copied = 0
            while chunk := src.read(1024 * 1024):
                dst.write(chunk)
                copied += len(chunk)
                if progress_callback:
                    progress_callback(copied, entry.size_bytes)

    # PROPERTIES
    #--------------------------------------------------------------------------------------

    @property
    def internal_root(self) -> Path:
        return self._internal_root

    @property
    def usb_root(self) -> Path | None:
        return self._usb_root