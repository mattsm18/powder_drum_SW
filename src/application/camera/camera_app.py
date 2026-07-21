#
# Title: application/camera/camera_app.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Handle camera application interface between GUI and Hardware

from datetime import datetime
from typing import Callable
from pathlib import Path

from models.camera_model import CameraModel, CameraSetting
from managers.camera.camera_manager import CameraManager
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

RESERVED_BYTES = 5 * 1000 * 1000

class CameraApp(QObject):
    
    # Outbound Signals
    on_new_frame            = pyqtSignal(object)
    on_connection_changed   = pyqtSignal(bool)
    on_recording_started    = pyqtSignal()
    on_recording_stopped    = pyqtSignal()
    on_streaming_started    = pyqtSignal()
    on_streaming_stopped    = pyqtSignal()
    on_photo_taken          = pyqtSignal()
    on_storage_full         = pyqtSignal()

    # CONSTRUCTOR
    def __init__(self, storage_path: Callable[[str, int], Path]):
        super().__init__()

        self.model = CameraModel()
        self.manager = CameraManager()
        self.storage_path = storage_path

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    
    # PUBLIC API
    def connect(self):
        self.manager.connect()
        self.model.connected = True
        self.timer.start(33)

    def update(self):

        # Get latest frame from hardware
        frame = self.manager.capture_frame()
        if frame is None: return

        # Update model and emit frame
        self.model.preview_frame = frame
        self.on_new_frame.emit(frame)
    
    
    def set_camera_setting(self, setting: CameraSetting, value):
        self.manager.apply_setting(setting, value)
        setattr(self.model.settings, setting.value, value)

    def get_camera_setting(self, setting: CameraSetting):
        return getattr(self.model.settings, setting.value)

    def start_recording(self):
        if self.model.recording: return

        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        try:
            path = self.storage_path(filename, RESERVED_BYTES)
        except Exception:
            self.on_storage_full.emit()
            return

        self.manager.start_recording(path, fps=self.model.settings.fps)
        self.model.recording = True
        self.on_recording_started.emit()

    def stop_recording(self):
        if not self.model.recording: return

        self.manager.stop_recording()
        self.model.recording = False
        self.on_recording_stopped.emit()

    def start_streaming(self): pass
    def stop_streaming(self): pass

    def pause_preview(self):
        if self.timer.isActive(): self.timer.stop()

    def resume_preview(self):
        if not self.timer.isActive(): self.timer.start(33)

    def take_photo(self):

        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

        try:
            path = self.storage_path(filename, RESERVED_BYTES)
        except Exception:
            self.on_storage_full.emit()
            return

        self.manager.take_photo(path)
        self.on_photo_taken.emit()