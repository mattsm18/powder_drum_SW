#
# Title: managers/camera/camera_manager.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Handle hardware for Raspberry Pi Global Shutter camera with PiCamera2 library

from picamera2 import Picamera2
from models.camera_model import CameraModel, CameraSettings

class CameraManager():
    
    # CONSTRUCTOR
    def __init__(self):
        
        super().__init__()
        self._camera = None

    # PUBLIC API
    def connect(self):
        self._camera = Picamera2()
        print(self._camera.camera_controls) # debug available settings
        config = self._camera.create_preview_configuration(main={"format": "RGB888"})
        self._camera.configure(config)
        self._camera.start()

    def disconnect(self): 
        if self._camera:
            self._camera.stop()
            self._camera.close()
            self._camera = None

    def capture_frame(self): 
        if not self._camera: return None
        return self._camera.capture_array()
    
    def start_recording(): pass
    def stop_recording(): pass

    def apply_settings(self, settings: CameraSettings):
        
        controls = {}

        controls["AeEnable"] = settings.auto_exposure
        controls["AwbEnable"] = settings.auto_white_balance

        if not settings.auto_exposure:
            controls["ExposureTime"] = settings.exposure_time_us
            controls["AnalogueGain"] = settings.analogue_gain
        
        self._camera.set_controls(controls)


