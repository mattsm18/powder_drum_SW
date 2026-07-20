#
# Title: managers/camera/camera_manager.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Handle hardware for Raspberry Pi Global Shutter camera with PiCamera2 library

from picamera2 import Picamera2
from models.camera_model import CameraSetting

class CameraManager():

    # Map of Camera settings to Picamera2 setting names
    _CONTROL_MAP = {
        CameraSetting.EXPOSURE_TIME:        "ExposureTime",
        CameraSetting.AUTO_EXPOSURE:        "AeEnable",
        CameraSetting.ANALOGUE_GAIN:        "AnalogueGain",
        CameraSetting.COLOUR_GAINS:         "ColourGain",
        CameraSetting.AUTO_WHITE_BALANCE:   "AwbEnable",
        CameraSetting.BRIGHTNESS:           "Brightness",
        CameraSetting.CONTRAST:             "Contrast",
        CameraSetting.SATURATION:           "Saturation",
        CameraSetting.SHARPNESS:            "Sharpness",
    }
        
    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        
        super().__init__()
        self._camera = None

    # PUBLIC API
    #--------------------------------------------------------------------------------------

    def connect(self):
        self._camera = Picamera2()
        print(self._camera.camera_controls) # debug available settings
        config = self._camera.create_preview_configuration(main={"format": "RGB888"})
        self._camera.configure(config)
        self._camera.start()

    #--------------------------------------------------------------------------------------

    def disconnect(self): 
        if self._camera:
            self._camera.stop()
            self._camera.close()
            self._camera = None

    #--------------------------------------------------------------------------------------
    
    def capture_frame(self): 
        if not self._camera: return None
        return self._camera.capture_array()
    
    #--------------------------------------------------------------------------------------

    def start_recording(): pass
    def stop_recording(): pass

    #--------------------------------------------------------------------------------------
    
    def apply_setting(self, setting: CameraSetting, value):

        if not self._camera: return

        if setting in (CameraSetting.RESOLUTION, CameraSetting.FPS):
            self._reconfigure(setting, value)
            return

        control_name = self._CONTROL_MAP.get(setting)
        if control_name is None: raise ValueError(f"No PiCamera2 control mapped for {setting}")

        self._camera.set_controls({control_name: value})

    #--------------------------------------------------------------------------------------

    def _reconfigure(self, setting: CameraSetting, value):
        self._camera.stop()

        match setting:
            case CameraSetting.RESOLUTION:
                width, height = value
                config = self._camera.create_preview_configuration(main={"format": "RGB888", "size": (width, height)})
            case CameraSetting.FPS:
                config = self._camera.create_preview_configuration(main={"format": "RGB888"}, controls={"FrameRate": value})
            case _:
                raise ValueError(f"No reconfiguration control mapped for {setting}")

        self._camera.configure(config)
        self._camera.start()
    
    #--------------------------------------------------------------------------------------