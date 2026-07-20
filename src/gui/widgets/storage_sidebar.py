#
# Title: gui/widgets/storage_sidebar.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Sidebar widget for browsing internal/USB storage and previewing files

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QProgressBar, QStackedWidget, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from models.storage_model import FileEntry, MediaType


class StorageSidebar(QWidget):

    # Outbound Signals
    copy_requested = pyqtSignal(object)     # FileEntry - not wired yet, for future action menu
    delete_requested = pyqtSignal(object)   # FileEntry - not wired yet, for future action menu
    preview_requested = pyqtSignal(object)  # FileEntry

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()

        self._usb_available = False
        self.setFixedWidth(400)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        internal_section = self._build_internal_section()
        usb_section = self._build_usb_section()

        root.addWidget(internal_section, stretch=1)
        root.addWidget(self._divider())
        root.addWidget(usb_section, stretch=1)

    # LAYOUT BUILDERS
    #--------------------------------------------------------------------------------------

    def _build_internal_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.internal_usage_label = QLabel("Internal  0.0 / 8.0 GB")
        self.internal_usage_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        self.internal_usage_bar = QProgressBar()
        self.internal_usage_bar.setTextVisible(False)
        self.internal_usage_bar.setFixedHeight(8)

        self.internal_list = QListWidget()
        self.internal_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.internal_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(self.internal_usage_label)
        layout.addWidget(self.internal_usage_bar)
        layout.addWidget(self.internal_list, stretch=1)
        return section

    #--------------------------------------------------------------------------------------

    def _build_usb_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.usb_usage_label = QLabel("USB Drive  0.0 / 8.0 GB")
        self.usb_usage_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        self.usb_usage_bar = QProgressBar()
        self.usb_usage_bar.setTextVisible(False)
        self.usb_usage_bar.setFixedHeight(8)

        # Stack: index 0 = "no drive" placeholder, index 1 = actual file list
        self.usb_stack = QStackedWidget()

        self.usb_empty_placeholder = QLabel("No USB drive connected")
        self.usb_empty_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.usb_empty_placeholder.setWordWrap(True)
        self.usb_empty_placeholder.setStyleSheet("color: #888; font-size: 13px; padding: 20px;")

        self.usb_list = QListWidget()
        self.usb_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.usb_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.usb_stack.addWidget(self.usb_empty_placeholder)  # index 0
        self.usb_stack.addWidget(self.usb_list)               # index 1
        self.usb_stack.setCurrentIndex(0)

        layout.addWidget(self.usb_usage_label)
        layout.addWidget(self.usb_usage_bar)
        layout.addWidget(self.usb_stack, stretch=1)

        # Start fully greyed out
        self._set_usb_enabled(False)
        return section

    #--------------------------------------------------------------------------------------

    def _divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    # PUBLIC API (slots)
    #--------------------------------------------------------------------------------------

    def set_internal_files(self, files: list[FileEntry]):
        self._populate_list(self.internal_list, files)

    #--------------------------------------------------------------------------------------

    def set_internal_usage(self, used_bytes: int, quota_bytes: int):
        used_mb = used_bytes // (1024 * 1024)
        quota_mb = quota_bytes // (1024 * 1024)
        self.internal_usage_bar.setMaximum(quota_mb)
        self.internal_usage_bar.setValue(min(used_mb, quota_mb))
        self.internal_usage_label.setText(f"Internal  {used_bytes / 1e9:.1f} / {quota_bytes / 1e9:.1f} GB")

    #--------------------------------------------------------------------------------------

    def set_usb_connected(self, mount_path: Path, files: list[FileEntry]):
        self._usb_available = True
        self._set_usb_enabled(True)
        self.usb_stack.setCurrentIndex(1)
        self._populate_list(self.usb_list, files)

    #--------------------------------------------------------------------------------------

    def set_usb_disconnected(self):
        self._usb_available = False
        self.usb_list.clear()
        self.usb_stack.setCurrentIndex(0)
        self._set_usb_enabled(False)

    #--------------------------------------------------------------------------------------

    def set_usb_usage(self, used_bytes: int, quota_bytes: int):
        used_mb = used_bytes // (1024 * 1024)
        quota_mb = quota_bytes // (1024 * 1024)
        self.usb_usage_bar.setMaximum(quota_mb)
        self.usb_usage_bar.setValue(min(used_mb, quota_mb))
        self.usb_usage_label.setText(f"USB Drive  {used_bytes / 1e9:.1f} / {quota_bytes / 1e9:.1f} GB")

    # INTERNAL
    #--------------------------------------------------------------------------------------

    def _set_usb_enabled(self, enabled: bool):
        self.usb_usage_bar.setEnabled(enabled)
        self.usb_usage_label.setEnabled(enabled)
        self.usb_usage_label.setStyleSheet(f"font-weight: 600; font-size: 14px; color: {'black' if enabled else '#999'};")

    #--------------------------------------------------------------------------------------

    def _populate_list(self, list_widget: QListWidget, files: list[FileEntry]):
        list_widget.clear()
        for entry in files:
            size_mb = entry.size_bytes / 1e6
            item = QListWidgetItem(f"{entry.path.name}   ({size_mb:.1f} MB)")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            item.setToolTip(entry.path.name)
            list_widget.addItem(item)

    #--------------------------------------------------------------------------------------
