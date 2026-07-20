#
# Title: models/camera_model.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Represent the current state of the camera for reference throughout codebase

import numpy as np
from enum import Enum

class CameraModel:

    # State Attributes
    def __init__(self):
        self.connected:          bool                = False
        self.recording:          bool                = False
        self.preview_frame:      np.ndarray | None   = None
        self.fps:                float               = 0.0
        self.settings                                = CameraSettings()

class CameraSetting(Enum):
    EXPOSURE_TIME =         "exposure_time_us"
    AUTO_EXPOSURE =         "auto_exposure"
    ANALOGUE_GAIN =         "analogue_gain"
    COLOUR_GAINS =          "colour_gains"
    AUTO_WHITE_BALANCE =    "auto_white_balance"
    BRIGHTNESS =            "brightness"
    CONTRAST =              "contrast"
    SATURATION =            "saturation"
    SHARPNESS =             "sharpness"
    RESOLUTION =            "resolution"
    FPS =                   "fps"

class CameraSettings:

    def __init__(self):

        # Exposure
        self.exposure_time_us = 2000
        self.analogue_gain = 1.0
        self.auto_exposure = True
        
        # White balance
        self.colour_temperature = 4500
        self.colour_gains = (1.0, 1.0)
        self.auto_white_balance = True

        # Image
        self.brightness = 0.0
        self.contrast = 1.0
        self.saturation = 1.0
        self.sharpness = 1.0

        # Capture
        self.resolution = (1280, 720)
        self.fps = 30

