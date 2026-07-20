#
# Title: gui/widgets/storage_sidebar.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Sidebar widget for browsing internal/USB storage, previewing, and copying files

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QProgressBar, QTabWidget
)

from PyQt6.QtCore import pyqtSignal, Qt
from models.storage_model import FileEntry, MediaType

class StorageSidebar(QWidget):

    # Outbound Signals
    copy_requested = pyqtSignal(object)     # FileEntry
    delete_requested = pyqtSignal(object)   # FileEntry
    preview_requested = pyqtSignal(object)  # FileEntry

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()

        self._usb_available = False

        layout = QVBoxLayout(self)

        # Internal storage usage
        self.internal_usage_label = QLabel("Internal: 0 / 8 GB")
        self.internal_usage_bar = QProgressBar()
        layout.addWidget(self.internal_usage_label)
        layout.addWidget(self.internal_usage_bar)

        # Tabs: internal / USB file lists
        self.tabs = QTabWidget()
        self.internal_list = QListWidget()
        self.usb_list = QListWidget()
        self.tabs.addTab(self.internal_list, "Internal")
        self.tabs.addTab(self.usb_list, "USB (not connected)")
        self.tabs.setTabEnabled(1, False)
        layout.addWidget(self.tabs)

        # Action buttons
        button_row = QHBoxLayout()
        self.copy_button = QPushButton("Copy to USB")
        self.delete_button = QPushButton("Delete")
        button_row.addWidget(self.copy_button)
        button_row.addWidget(self.delete_button)
        layout.addLayout(button_row)

        self._wire_internal_signals()

    # PUBLIC API (slots)
    #--------------------------------------------------------------------------------------

    def set_internal_files(self, files: list[FileEntry]):
        self._populate_list(self.internal_list, files)
        # usage bar handled separately via set_internal_usage

    #--------------------------------------------------------------------------------------

    def set_internal_usage(self, used_bytes: int, quota_bytes: int):
        self.internal_usage_bar.setMaximum(quota_bytes)
        self.internal_usage_bar.setValue(min(used_bytes, quota_bytes))
        self.internal_usage_label.setText(
            f"Internal: {used_bytes / 1e9:.2f} / {quota_bytes / 1e9:.0f} GB")

    #--------------------------------------------------------------------------------------

    def set_usb_connected(self, mount_path: Path, files: list[FileEntry]):
        self._usb_available = True
        self.tabs.setTabEnabled(1, True)
        self.tabs.setTabText(1, f"USB ({mount_path.name})")
        self._populate_list(self.usb_list, files)
        self.copy_button.setEnabled(True)

    #--------------------------------------------------------------------------------------

    def set_usb_disconnected(self):
        self._usb_available = False
        self.usb_list.clear()
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabText(1, "USB (not connected)")
        self.tabs.setCurrentIndex(0)
        self.copy_button.setEnabled(False)

    # INTERNAL
    #--------------------------------------------------------------------------------------

    def _wire_internal_signals(self):
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.internal_list.itemClicked.connect(self._on_item_clicked)
        self.usb_list.itemClicked.connect(self._on_item_clicked)
        self.copy_button.setEnabled(False)  # disabled until USB connects

    #--------------------------------------------------------------------------------------

    def _populate_list(self, list_widget: QListWidget, files: list[FileEntry]):
        list_widget.clear()
        for entry in files:
            icon = "🎬" if entry.media_type == MediaType.VIDEO else "📷"
            size_mb = entry.size_bytes / 1e6
            item = QListWidgetItem(f"{icon}  {entry.path.name}   ({size_mb:.1f} MB)")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            list_widget.addItem(item)

    #--------------------------------------------------------------------------------------

    def _on_item_clicked(self, item: QListWidgetItem):
        entry = item.data(Qt.ItemDataRole.UserRole)
        self.preview_requested.emit(entry)

    #--------------------------------------------------------------------------------------

    def _on_copy_clicked(self):
        entry = self._selected_entry()
        if entry: self.copy_requested.emit(entry)

    #--------------------------------------------------------------------------------------

    def _on_delete_clicked(self):
        entry = self._selected_entry()
        if entry: self.delete_requested.emit(entry)

    #--------------------------------------------------------------------------------------

    def _selected_entry(self) -> FileEntry | None:
        current_list = self.internal_list if self.tabs.currentIndex() == 0 else self.usb_list
        item = current_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None