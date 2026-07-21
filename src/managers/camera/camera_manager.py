#
# Title: managers/camera/camera_manager.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Handle hardware for Raspberry Pi Global Shutter camera with PiCamera2 library

from pathlib import Path
from PIL import Image
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
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
        self._encoder = None
        self._is_recording = False

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
            if self._is_recording: self.stop_recording()
            self._camera.stop()
            self._camera.close()
            self._camera = None

    #--------------------------------------------------------------------------------------
    
    def capture_frame(self): 
        if not self._camera: return None
        return self._camera.capture_array()
    
    #--------------------------------------------------------------------------------------

    def take_photo(self, path: Path):
        
        if not self._camera: return None

        frame = self.capture_frame()
        if frame is None: return None

        path = Path(path)
        if path.suffix.lower() != ".png":
            path = path.with_suffix(".png")
        path.parent.mkdir(parents=True, exist_ok=True)

        # RGB888 config from Picamera2 is actually ordered BGR, so swap
        # channels before handing the array to PIL (which expects RGB).
        image = Image.fromarray(frame[:, :, ::-1] if frame.ndim == 3 and frame.shape[2] == 3 else frame)
        image.save(path, format="PNG")

        return path

    #--------------------------------------------------------------------------------------

    def start_recording(self, path: Path, bitrate: int = None, fps: int = None):
        if not self._camera: return
        if self._is_recording: return

        if fps:
            frame_duration_us = int(1_000_000 / fps)
            self._camera.set_controls({"FrameDurationLimits": (frame_duration_us, frame_duration_us)})

        self._encoder = H264Encoder(bitrate=bitrate) if bitrate else H264Encoder()
        output = FfmpegOutput(str(path))
        self._camera.start_encoder(self._encoder, output)
        self._is_recording = True

    #--------------------------------------------------------------------------------------

    def stop_recording(self):
        if not self._camera or not self._is_recording: return

        self._camera.stop_encoder(self._encoder)
        self._encoder = None
        self._is_recording = False

        # Release the frame-duration lock applied in start_recording so
        # preview auto-exposure can vary frame timing again.
        self._camera.set_controls({"FrameDurationLimits": (100, 1_000_000)})

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
        was_recording = self._is_recording
        if was_recording: self.stop_recording()

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

        if was_recording: pass
    
    #--------------------------------------------------------------------------------------