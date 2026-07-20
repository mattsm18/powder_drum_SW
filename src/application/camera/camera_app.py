#
# Title: application/camera/camera_app.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Handle camera application interface between GUI and Hardware

from models.camera_model import CameraModel, CameraSetting
from managers.camera.camera_manager import CameraManager
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

class CameraApp(QObject):
    
    # Outbound Signals
    new_frame = pyqtSignal(object)
    connection_changed = pyqtSignal(bool)

    # CONSTRUCTOR
    def __init__(self):
        super().__init__()

        self.model = CameraModel()
        self.manager = CameraManager()

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
    
    # Model state accessors
    def set_camera_setting(self, setting: CameraSetting, value):
        self.manager.apply_setting(setting, value)
        setattr(self.model.settings, setting.value, value)

    def get_camera_setting(self, setting: CameraSetting):
        return getattr(self.model.settings, setting.value)