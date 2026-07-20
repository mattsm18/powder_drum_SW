#
# Title: gui/tabs/camera_tab.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Camera preview tab with recording controls and storage sidebar

import numpy as np
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import pyqtSignal, Qt

from models.camera_model import CameraSetting
from gui.widgets.storage_sidebar import StorageSidebar

class CameraTab(QWidget):

    # Outbound Signals
    camera_setting_changed = pyqtSignal(CameraSetting, object)
    record_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    copy_requested = pyqtSignal(object)     # FileEntry, forwarded from sidebar
    delete_requested = pyqtSignal(object)   # FileEntry, forwarded from sidebar

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()

        root_layout = QHBoxLayout(self)

        # Main preview area
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("background-color: black;")

        self.record_button = QPushButton("Start Recording")
        self.record_button.setCheckable(True)

        preview_layout.addWidget(self.preview_label)
        preview_layout.addWidget(self.record_button)

        # Sidebar
        self.sidebar = StorageSidebar()

        root_layout.addLayout(preview_layout, stretch=3)
        root_layout.addWidget(self.sidebar, stretch=1)

        self._wire_internal_signals()

    # PUBLIC API (slots)
    #--------------------------------------------------------------------------------------

    def set_preview(self, frame: np.ndarray):
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.preview_label.setPixmap(QPixmap.fromImage(image).scaled(
            self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    #--------------------------------------------------------------------------------------

    def set_recording_state(self):
        self.record_button.setChecked(True)
        self.record_button.setText("Stop Recording")

    #--------------------------------------------------------------------------------------

    def set_idle_state(self):
        self.record_button.setChecked(False)
        self.record_button.setText("Start Recording")

    # Forwarded straight to the sidebar (kept here so Application only wires camera_tab)
    #--------------------------------------------------------------------------------------

    def set_internal_files(self, files):
        self.sidebar.set_internal_files(files)

    def set_internal_usage(self, used_bytes, quota_bytes):
        self.sidebar.set_internal_usage(used_bytes, quota_bytes)

    def set_usb_connected(self, mount_path, files):
        self.sidebar.set_usb_connected(mount_path, files)

    def set_usb_disconnected(self):
        self.sidebar.set_usb_disconnected()

    # INTERNAL
    #--------------------------------------------------------------------------------------

    def _wire_internal_signals(self):
        self.record_button.clicked.connect(self._on_record_clicked)
        self.sidebar.copy_requested.connect(self.copy_requested)
        self.sidebar.delete_requested.connect(self.delete_requested)

    #--------------------------------------------------------------------------------------

    def _on_record_clicked(self):
        if self.record_button.isChecked():
            self.record_requested.emit()
        else:
            self.stop_requested.emit()