#
# Title: models/camera_model.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Represent the current state of the camera for reference throughout codebase

import numpy as np

class CameraModel:

    # State Attributes
    def __init__(self):
        self.connected:          bool                = False
        self.recording:          bool                = False
        self.preview_frame:      np.ndarray | None   = None
        self.fps:                float               = 0.0
        self.settings                                = CameraSettings()

class CameraSettings:

    def __init__(self):
        self.exposure_time_us = 2000
        self.analogue_gain = 1.0
        
        self.auto_exposure = True
        self.auto_white_balance = True


