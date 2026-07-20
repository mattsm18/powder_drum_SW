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

RESERVE_BYTES_FOR_RECORDING = 500 * 1024 * 1024

class CameraApp(QObject):
    
    # Outbound Signals
    new_frame = pyqtSignal(object)
    connection_changed = pyqtSignal(bool)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    storage_full = pyqtSignal()

    # CONSTRUCTOR
    def __init__(self, get_recording_path: Callable[[str, int], Path]):
        super().__init__()

        self.model = CameraModel()
        self.manager = CameraManager()
        self._get_recording_path = get_recording_path

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    
    # PUBLIC API
    def connect(self):
        self.manager.connect()
        self.model.connected = True
        self.timer.start(33)

    # Called on timer
    def update(self):

        # Get latest frame from hardware
        frame = self.manager.capture_frame()
        if frame is None: return

        # Update model and emit frame
        self.model.preview_frame = frame
        self.new_frame.emit(frame)
    
    
    def set_camera_setting(self, setting: CameraSetting, value):
        self.manager.apply_setting(setting, value)
        setattr(self.model.settings, setting.value, value)

    def get_camera_setting(self, setting: CameraSetting):
        return getattr(self.model.settings, setting.value)

    def start_recording(self):
        if self.model.recording: return

        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        try:
            path = self._get_recording_path(filename, RESERVE_BYTES_FOR_RECORDING)
        except Exception:
            self.storage_full.emit()
            return

        self.manager.start_recording(path)
        self.model.recording = True
        self.recording_started.emit()

    def stop_recording(self):
        if not self.model.recording: return

        self.manager.stop_recording()
        self.model.recording = False
        self.recording_stopped.emit()