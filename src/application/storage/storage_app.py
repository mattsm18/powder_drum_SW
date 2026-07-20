#
# Title: application/storage/storage_app.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Business logic wiring StorageManager <-> StorageModel <-> storage sidebar

from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from managers.storage.storage_manager import StorageManager, StorageFullError
from managers.storage.usb_watcher import UsbWatcher
from models.storage_model import StorageModel, StorageState, FileEntry

class StorageApp(QObject):

    internal_updated = pyqtSignal(list)
    usb_connected = pyqtSignal(Path, list)
    usb_disconnected = pyqtSignal()
    storage_full = pyqtSignal(str)
    internal_usage_updated = pyqtSignal(object, object)
    usb_usage_updated = pyqtSignal(object, object) 
    
    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.model = StorageModel()
        self._manager = StorageManager(internal_root=Path.home() / "recordings")
        self._watcher = UsbWatcher(self._on_usb_connect, self._on_usb_disconnect)
        self._watcher.start()
        self.refresh_internal()

    # PUBLIC API
    #--------------------------------------------------------------------------------------

    def refresh_internal(self):
        self.model.internal.files = self._manager.list_files(self._manager.internal_root)
        self.model.internal.used_bytes, _ = self._manager.get_usage(self._manager.internal_root, self.model.internal.quota_bytes)
        self.internal_updated.emit(self.model.internal.files)
        self.internal_usage_updated.emit(self.model.internal.used_bytes, self.model.internal.quota_bytes)


    #--------------------------------------------------------------------------------------

    def get_recording_path(self, filename: str, reserve_bytes: int) -> Path:
        try:
            self._manager.ensure_space(self._manager.internal_root, self.model.internal.quota_bytes, reserve_bytes)
        except StorageFullError:
            self.storage_full.emit("internal")
            raise
        return self._manager.internal_root / filename

    #--------------------------------------------------------------------------------------

    def copy_to_usb(self, entry: FileEntry, progress_callback=None):
        if self.model.usb is None: raise RuntimeError("No USB drive connected")
        self._manager.ensure_space(self._manager.usb_root, self.model.usb.quota_bytes, entry.size_bytes)
        self._manager.copy_file(entry, self._manager.usb_root, progress_callback)
        self._refresh_usb()

    def _refresh_usb(self):
        if self.model.usb is None: return
        self.model.usb.files = self._manager.list_files(self._manager.usb_root)
        self.model.usb.used_bytes, _ = self._manager.get_usage(self._manager.usb_root, self.model.usb.quota_bytes)
        self.usb_connected.emit(self.model.usb_mount_path, self.model.usb.files)
        self.usb_usage_updated.emit(self.model.usb.used_bytes, self.model.usb.quota_bytes)
    #--------------------------------------------------------------------------------------

    def delete_file(self, entry: FileEntry):
        self._manager.delete(entry)
        self.refresh_internal()

    # INTERNAL CALLBACKS
    #--------------------------------------------------------------------------------------

    def _on_usb_connect(self, mount_path: Path):
        self._manager.set_usb_root(mount_path)
        self.model.usb = StorageState()
        self.model.usb_mount_path = mount_path
        files = self._manager.list_files(mount_path)
        self.model.usb.files = files
        self.model.usb.used_bytes, _ = self._manager.get_usage(mount_path, self.model.usb.quota_bytes)
        self.usb_connected.emit(mount_path, files)
        self.usb_usage_updated.emit(self.model.usb.used_bytes, self.model.usb.quota_bytes)

    #--------------------------------------------------------------------------------------

    def _on_usb_disconnect(self):
        self._manager.set_usb_root(None)
        self.model.usb = None
        self.model.usb_mount_path = None
        self.usb_disconnected.emit()