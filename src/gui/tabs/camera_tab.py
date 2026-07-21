#
# Title: gui/tabs/camera_tab.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Camera preview tab with recording controls and storage sidebar

import numpy as np

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from gui.widgets.preview_widget import PreviewWidget

from models.camera_model import CameraSetting

ICON_WIDTH = 64
ICON_HEIGHT = 56

class CameraTab(QWidget):

    # Outbound Signals
    camera_setting_changed = pyqtSignal(CameraSetting, object)
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()
    take_photo = pyqtSignal()
    start_streaming = pyqtSignal()
    stop_streaming = pyqtSignal()

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()

        # Create Widgets and Buttons
        self.preview = PreviewWidget()
        self.preview.setMinimumSize(640, 480)
        self.preview.setStyleSheet("background-color: black;")

        self.photo_button = QPushButton()
        self.photo_button.setIcon(QIcon("assets/icons/photo_icon.svg"))
        self.photo_button.setIconSize(QSize(ICON_WIDTH, ICON_HEIGHT))

        self.record_button = QPushButton()
        self.record_button.setIcon(QIcon("assets/icons/video_icon.svg"))
        self.record_button.setIconSize(QSize(ICON_WIDTH, ICON_HEIGHT))
        self.record_button.setCheckable(True)

        self.stream_button = QPushButton()
        self.stream_button.setIcon(QIcon("assets/icons/stream_icon.svg"))
        self.stream_button.setIconSize(QSize(ICON_WIDTH, ICON_HEIGHT))
        self.stream_button.setCheckable(True)

        self.outline_button = QPushButton()
        self.outline_button.setIcon(QIcon("assets/icons/outline_icon.svg"))
        self.outline_button.setIconSize(QSize(ICON_WIDTH, ICON_HEIGHT))
        self.outline_button.setCheckable(True)
        
        self.vision_button = QPushButton()
        self.vision_button.setIcon(QIcon("assets/icons/vision_icon.svg"))
        self.vision_button.setIconSize(QSize(ICON_WIDTH, ICON_HEIGHT))
        self.vision_button.setCheckable(True)
        
        # Create Layouts
        root_layout = QHBoxLayout(self)
        preview_layout = QVBoxLayout()
        button_layout = QVBoxLayout()

        # Attach widgets and buttons to layouts
        preview_layout.addWidget(self.preview)
        button_layout.addWidget(self.photo_button)
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.stream_button)
        button_layout.addWidget(self.outline_button)
        button_layout.addWidget(self.vision_button)
        button_layout.addStretch()

        # Render root
        root_layout.addLayout(preview_layout, stretch=1)
        root_layout.addLayout(button_layout)

        # Wiring
        self.record_button.clicked.connect(self._on_record_pressed)
        self.photo_button.clicked.connect(self._on_photo_pressed)
        self.stream_button.clicked.connect(self._on_stream_pressed)

    # PUBLIC API (slots)
    #--------------------------------------------------------------------------------------

    def set_preview(self, frame: np.ndarray): self.preview.set_frame(frame)

    #--------------------------------------------------------------------------------------
    # Wiring / Signal emits
    #--------------------------------------------------------------------------------------

    def _on_photo_pressed(self):

        self.take_photo.emit()
        self.preview.trigger_flash()

    #--------------------------------------------------------------------------------------

    def _on_record_pressed(self):

        if self.record_button.isChecked(): 

            self.start_recording.emit()
            self.preview.set_recording(True)

        else: 

            self.stop_recording.emit()
            self.preview.set_recording(False)

    #--------------------------------------------------------------------------------------

    def _on_stream_pressed(self):

        if self.stream_button.isChecked(): 

            self.start_streaming.emit()
            self.preview.set_streaming(True)

        else: 

            self.stop_streaming.emit()
            self.preview.set_streaming(False)

    #--------------------------------------------------------------------------------------