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

    on_internal_storage_updated = pyqtSignal(list)
    on_usb_connected = pyqtSignal(Path, list)
    on_usb_disconnected = pyqtSignal()
    on_storage_full = pyqtSignal(str)
    on_internal_size_updated = pyqtSignal(object, object)
    on_usb_size_updated = pyqtSignal(object, object)

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.model = StorageModel()
        self._manager = StorageManager(internal_root=Path.home() / "recordings")
        self._watcher = UsbWatcher(self._on_usb_connect, self._on_usb_disconnect)
        self._watcher.start()
        self.refresh_internal_storage()

    # PUBLIC API
    #--------------------------------------------------------------------------------------

    def refresh_internal_storage(self):
        
        self.model.internal.files = self._manager.list_files(self._manager.internal_root)
        self.model.internal.used_bytes, _ = self._manager.get_size(self._manager.internal_root, self.model.internal.quota_bytes)

        self.on_internal_storage_updated.emit(self.model.internal.files)
        self.on_internal_size_updated.emit(self.model.internal.used_bytes, self.model.internal.quota_bytes)

    #--------------------------------------------------------------------------------------

    def get_storage_path(self, filename: str, reserve_bytes: int) -> Path:
        try:
            self._manager.ensure_space(self._manager.internal_root, self.model.internal.quota_bytes, reserve_bytes)
        except StorageFullError:
            self.on_storage_full.emit("internal")
            raise
        return self._manager.internal_root / filename

    #--------------------------------------------------------------------------------------

    def copy_to_usb(self, entry: FileEntry, progress_callback=None):
        if self.model.usb is None: raise RuntimeError("No USB drive connected")
        try:
            self._manager.ensure_space_on_device(self._manager.usb_root, entry.size_bytes)
        except StorageFullError:
            self.on_storage_full.emit("usb")
            raise
        self._manager.copy_file(entry, self._manager.usb_root, progress_callback)
        self._refresh_usb()

    #--------------------------------------------------------------------------------------

    def _refresh_usb(self):

        if self.model.usb is None: return

        # Update files and size from model
        self.model.usb.files = self._manager.list_files(self._manager.usb_root)
        self.model.usb.used_bytes, self.model.usb.quota_bytes = self._manager.get_usage_with_device_capacity(self._manager.usb_root)

        # Send out QT signal
        self.on_usb_connected.emit(self.model.usb_mount_path, self.model.usb.files)
        self.on_usb_size_updated.emit(self.model.usb.used_bytes, self.model.usb.quota_bytes)

    #--------------------------------------------------------------------------------------

    def delete_file(self, entry: FileEntry):
        self._manager.delete(entry)

        if self._manager.usb_root is not None and self._manager.usb_root in entry.path.parents:
            self._refresh_usb()
        else:
            self.refresh_internal_storage()

    # INTERNAL CALLBACKS
    #--------------------------------------------------------------------------------------

    def _on_usb_connect(self, mount_path: Path):

        # Update root, list files, get size
        self._manager.set_usb_root(mount_path)
        files = self._manager.list_files(self._manager.usb_root)
        used, quota = self._manager.get_usage_with_device_capacity(self._manager.usb_root)

        # Update internal storage model
        self.model.usb = StorageState()
        self.model.usb_mount_path = mount_path
        self.model.usb.files = files
        self.model.usb.used_bytes = used
        self.model.usb.quota_bytes = quota

        # Send out QT Signal
        self.on_usb_connected.emit(mount_path, files)
        self.on_usb_size_updated.emit(used, quota)

    #--------------------------------------------------------------------------------------

    def _on_usb_disconnect(self):
        self._manager.set_usb_root(None)
        self.model.usb = None
        self.model.usb_mount_path = None
        self.on_usb_disconnected.emit()